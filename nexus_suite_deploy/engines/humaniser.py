import streamlit as st
import requests

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🧬 Text Humaniser & Bypass Engine</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Convert robotic, AI-generated text into highly engaging, natural, and human-like writing that bypasses AI content detectors.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_input, col_params = st.columns([2, 1])
    
    with col_input:
        text_to_humanize = st.text_area(
            "Paste AI-Generated Text here",
            value="Artificial intelligence has revolutionized content creation. However, text produced by large language models often exhibits predictable linguistic patterns. Using advanced algorithms, this tool restructures sentences to mimic natural human speech variations.",
            height=180
        )
        
    with col_params:
        st.markdown("### Settings")
        tone = st.selectbox(
            "Rewriting Tone",
            ["Natural & Conversational", "Professional & Executive", "Academic & Analytical", "Creative & Expressive"]
        )
        
        strength = st.slider(
            "Humanization Level",
            min_value=1,
            max_value=3,
            value=2,
            help="1: Light polish (maintains original structure closely), 2: Balanced rephrasing, 3: Deep rewrite (restructures sentences completely for maximum bypass)"
        )
        
        model_selection = st.selectbox(
            "Rewrite AI Model",
            ["Llama 3.3 70B (Recommended)", "Mistral Nemo", "GPT-4o-Mini equivalent"]
        )
        
        models = {
            "Llama 3.3 70B (Recommended)": "llama",
            "Mistral Nemo": "mistral",
            "GPT-4o-Mini equivalent": "openai"
        }

    # Action trigger
    if st.button("Humanize Text"):
        if text_to_humanize.strip():
            with st.spinner("Analyzing text flow and injecting humanistic writing styles..."):
                # System prompt definition
                system_prompt = (
                    "You are a master copywriter and linguist. Your goal is to rewrite the user's text to make it sound completely human, "
                    "neutralizing any trace of machine-generation patterns (like repetitive transition words, uniform sentence lengths, and stiff grammar). "
                    "You must achieve this by applying the following directives:\n"
                    f"- Adopt a {tone} tone.\n"
                    f"- Rewrite with level {strength} intensity (where level 1 is light syntax adjustment, level 2 is moderate rephrasing, and level 3 is deep restructuring of sentences and vocabulary).\n"
                    "- Maintain the exact original core facts, messages, and intent of the input text.\n"
                    "- Use varied sentence structures (combine short punchy sentences with compound/complex ones).\n"
                    "- Output ONLY the final rewritten text. Do not provide any introduction, explanation, quotes, or conversational notes."
                )
                
                payload = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text_to_humanize}
                    ],
                    "model": models[model_selection]
                }
                
                try:
                    res = requests.post("https://text.pollinations.ai/", json=payload, timeout=25)
                    if res.status_code == 200:
                        humanized_text = res.text.strip()
                        
                        # Display Results side by side
                        st.markdown("### 📊 Contrast Analysis")
                        col_orig, col_human = st.columns(2)
                        
                        with col_orig:
                            st.markdown("""
                            <div style='background:rgba(255, 75, 75, 0.05); padding:15px; border-radius:10px; border:1px solid rgba(255, 75, 75, 0.2);'>
                                <h4 style='color:#ff4b4b; margin:0 0 10px 0;'>Original AI Text</h4>
                                <p style='font-size:0.95rem; line-height:1.5; color:#e2e8f0;'>""" + text_to_humanize.replace("\n", "<br>") + """</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Stats
                            words_orig = len(text_to_humanize.split())
                            chars_orig = len(text_to_humanize)
                            st.markdown(f"**Words:** {words_orig} | **Characters:** {chars_orig}")
                            
                        with col_human:
                            st.markdown("""
                            <div style='background:rgba(16, 185, 129, 0.05); padding:15px; border-radius:10px; border:1px solid rgba(16, 185, 129, 0.2);'>
                                <h4 style='color:#10b981; margin:0 0 10px 0;'>Humanized Output</h4>
                                <p style='font-size:0.95rem; line-height:1.5; color:#e2e8f0;'>""" + humanized_text.replace("\n", "<br>") + """</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Stats
                            words_hum = len(humanized_text.split())
                            chars_hum = len(humanized_text)
                            st.markdown(f"**Words:** {words_hum} | **Characters:** {chars_hum}")
                            st.download_button(
                                label="Download Humanized Text",
                                data=humanized_text,
                                file_name="humanized_text.txt",
                                mime="text/plain"
                            )
                    else:
                        st.error("API Error. Couldn't rewrite text. Please retry.")
                except Exception as e:
                    st.error(f"Network error rewriting text: {str(e)}")
        else:
            st.warning("Please enter some text to humanize.")
