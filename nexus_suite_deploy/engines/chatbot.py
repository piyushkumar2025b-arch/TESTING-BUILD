import streamlit as st
import requests

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🌌 AI Chatbot Assistant</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Chat in real-time with state-of-the-art models. Backed by free keyless AI engines.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model and Persona controls
    col1, col2 = st.columns([1, 1])
    with col1:
        model_options = {
            "OpenAI GPT-4o-mini": "openai",
            "Meta Llama 3.3 70B": "llama",
            "Mistral Nemo": "mistral",
            "Unity AI (Qwen)": "unity"
        }
        selected_model_name = st.selectbox("Select Model", list(model_options.keys()))
        selected_model = model_options[selected_model_name]
        
    with col2:
        personas = {
            "General Assistant": "You are a helpful, brilliant, and polite AI assistant.",
            "Software Engineer": "You are a senior full-stack software developer. Answer technical questions with complete, clean, optimized code blocks and detailed explanations.",
            "Creative Writer": "You are an imaginative and poetic writer. Answer requests with elegant, descriptive, and flowery prose.",
            "Algorithm & LeetCode Coach": "You are an elite competitive programmer. Guide the user step-by-step to optimize their time and space complexities. Always trace your solution."
        }
        selected_persona_name = st.selectbox("Select Persona", list(personas.keys()))
        selected_persona = personas[selected_persona_name]
        
    from engines import database
    import datetime

    # Get all active sessions
    saved_sessions = database.get_chat_sessions()
    
    # We will store active session in st.session_state.active_chat_session
    if "active_chat_session" not in st.session_state:
        if saved_sessions:
            st.session_state.active_chat_session = saved_sessions[0]
        else:
            st.session_state.active_chat_session = "New Session"

    # Selectbox to load sessions
    session_options = ["New Session"] + saved_sessions
    
    # Render controls row
    col_session, col_actions = st.columns([2, 1])
    
    with col_session:
        # Determine index of current session
        current_idx = 0
        if st.session_state.active_chat_session in session_options:
            current_idx = session_options.index(st.session_state.active_chat_session)
            
        selected_session = st.selectbox("Select Chat Session", session_options, index=current_idx)
        if selected_session != st.session_state.active_chat_session:
            st.session_state.active_chat_session = selected_session
            st.session_state.chat_history = [] if selected_session == "New Session" else database.get_chat_history(selected_session)
            st.rerun()

    with col_actions:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            if st.button("🗑️ Delete Session"):
                if st.session_state.active_chat_session != "New Session":
                    database.clear_chat_history(st.session_state.active_chat_session)
                    st.session_state.active_chat_session = "New Session"
                    st.session_state.chat_history = []
                    st.rerun()
        with col_c2:
            if st.button("🔄 Reset Chat"):
                st.session_state.chat_history = []
                if st.session_state.active_chat_session != "New Session":
                    database.clear_chat_history(st.session_state.active_chat_session)
                st.rerun()

    # Load history if not loaded yet or empty
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if st.session_state.active_chat_session != "New Session" and not st.session_state.chat_history:
        st.session_state.chat_history = database.get_chat_history(st.session_state.active_chat_session)

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Chat Input
    if user_prompt := st.chat_input("Enter message here..."):
        # If it's a new session, auto-generate a session name
        if st.session_state.active_chat_session == "New Session":
            # Generate a nice name from first words of the prompt
            words = user_prompt.split()[:4]
            name_prefix = " ".join(words)
            timestamp = datetime.datetime.now().strftime("%d %b %H:%M")
            session_name = f"{name_prefix}... ({timestamp})" if len(words) >= 4 else f"{user_prompt[:15]} ({timestamp})"
            st.session_state.active_chat_session = session_name
            st.session_state.chat_history = []
            
        # Display user message
        with st.chat_message("user"):
            st.write(user_prompt)
            
        # Add to history
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        database.save_chat_message(st.session_state.active_chat_session, "user", user_prompt)
        
        # Call API
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*Nexus is thinking...*")
            
            # Formulate the payload
            api_url = "https://text.pollinations.ai/"
            
            # Put system persona first
            payload_messages = [{"role": "system", "content": selected_persona}]
            
            # Limit context window to last 15 messages for responsiveness
            for msg in st.session_state.chat_history[-15:]:
                payload_messages.append(msg)
                
            payload = {
                "messages": payload_messages,
                "model": selected_model,
                "jsonMode": False
            }
            
            try:
                response = requests.post(api_url, json=payload, timeout=30)
                if response.status_code == 200:
                    ai_response = response.text
                    message_placeholder.markdown(ai_response)
                    # Save assistant message
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    database.save_chat_message(st.session_state.active_chat_session, "assistant", ai_response)
                    st.rerun()
                else:
                    message_placeholder.error(f"Error: Received status code {response.status_code} from API.")
            except Exception as e:
                message_placeholder.error(f"Failed to communicate with AI endpoint: {str(e)}")
