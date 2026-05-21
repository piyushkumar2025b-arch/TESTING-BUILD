import streamlit as st
import requests
import json
import re

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>💻 HTML/CSS Design Sandbox</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Generate UI designs with AI, edit code in real-time, and preview layouts inside an interactive iframe.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize editor states
    if "sandbox_html" not in st.session_state:
        st.session_state.sandbox_html = """<div class="card">
  <h2>Aether Card</h2>
  <p>Modify code or prompt the AI to rewrite this template into complex pages.</p>
  <button class="glow-btn">Unlock Magic</button>
</div>"""
        
    if "sandbox_css" not in st.session_state:
        st.session_state.sandbox_css = """body {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  margin: 0;
  background: radial-gradient(circle, #0f172a, #020617);
  font-family: 'Inter', sans-serif;
  color: white;
}

.card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  text-align: center;
  max-width: 350px;
}

h2 {
  margin-top: 0;
  color: #818cf8;
}

p {
  font-size: 0.95rem;
  color: #94a3b8;
  line-height: 1.5;
}

.glow-btn {
  background: linear-gradient(135deg, #818cf8, #f472b6);
  border: none;
  border-radius: 8px;
  color: white;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(244, 114, 182, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}

.glow-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 25px rgba(244, 114, 182, 0.7);
}"""

    # AI generator sidebar / section
    st.markdown("### 🤖 Generate Design with AI")
    ai_prompt = st.text_input("Describe the component/layout you want (e.g. 'Sleek dark glassmorphic login card with neon inputs')", "")
    
    if st.button("Generate Layout"):
        if ai_prompt:
            with st.spinner("AI is coding your design details..."):
                system_prompt = (
                    "You are a master UI/UX engineer. Create web layouts based on user instructions. "
                    "You MUST reply ONLY with a valid JSON object. Do not wrap in markdown tags like ```json. "
                    "The JSON object must contain exactly two keys: "
                    "1. 'html': The HTML body code (exclude <html>, <head>, or <body> tags - just the inner content). "
                    "2. 'css': The corresponding CSS styles. "
                    "Make sure the design is futuristic, beautiful, and fully functional with styles for buttons, containers, typography, hover states, etc."
                )
                
                payload = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": ai_prompt}
                    ],
                    "model": "openai"
                }
                
                try:
                    res = requests.post("https://text.pollinations.ai/", json=payload, timeout=25)
                    if res.status_code == 200:
                        raw_response = res.text.strip()
                        
                        # Clean markdown wrappers if returned
                        raw_response = re.sub(r"^```json\s*", "", raw_response, flags=re.IGNORECASE)
                        raw_response = re.sub(r"^```\s*", "", raw_response, flags=re.IGNORECASE)
                        raw_response = re.sub(r"\s*```$", "", raw_response, flags=re.IGNORECASE)
                        
                        try:
                            code_data = json.loads(raw_response)
                            st.session_state.sandbox_html = code_data.get("html", st.session_state.sandbox_html)
                            st.session_state.sandbox_css = code_data.get("css", st.session_state.sandbox_css)
                            st.success("Design generated successfully!")
                        except Exception as e:
                            st.error("Failed to parse JSON code blocks from AI. Using fallback extraction...")
                            # Fallback regex search
                            html_match = re.search(r'"html"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_response)
                            css_match = re.search(r'"css"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_response)
                            if html_match and css_match:
                                st.session_state.sandbox_html = html_match.group(1).encode().decode('unicode-escape')
                                st.session_state.sandbox_css = css_match.group(1).encode().decode('unicode-escape')
                            else:
                                st.info("Check raw response: " + raw_response[:300])
                    else:
                        st.error("API error fetching layout code.")
                except Exception as e:
                    st.error(f"Error querying design AI: {str(e)}")
        else:
            st.warning("Please type a design description first.")

    # Split workspace
    col_code, col_preview = st.columns([1, 1])
    
    with col_code:
        st.markdown("### 📝 Source Code Editor")
        tab_html, tab_css = st.tabs(["HTML Body", "CSS Styles"])
        
        with tab_html:
            new_html = st.text_area("HTML Source", value=st.session_state.sandbox_html, height=350, key="editor_html")
            st.session_state.sandbox_html = new_html
            
        with tab_css:
            new_css = st.text_area("CSS Source", value=st.session_state.sandbox_css, height=350, key="editor_css")
            st.session_state.sandbox_css = new_css

    with col_preview:
        st.markdown("### 🖥️ Live Dynamic Preview")
        
        # Combine HTML and CSS with fonts and basic resets
        full_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                {st.session_state.sandbox_css}
            </style>
        </head>
        <body>
            {st.session_state.sandbox_html}
        </body>
        </html>
        """
        
        # Embed in Iframe
        st.components.v1.html(full_code, height=380, scrolling=True)

    # Downloads
    st.markdown("### 💾 Export Design")
    col_dl_html, col_dl_css, _ = st.columns([1, 1, 2])
    
    with col_dl_html:
        st.download_button(
            label="Download Complete index.html",
            data=full_code,
            file_name="index.html",
            mime="text/html"
        )
        
    with col_dl_css:
        st.download_button(
            label="Download stylesheet.css",
            data=st.session_state.sandbox_css,
            file_name="stylesheet.css",
            mime="text/css"
        )
