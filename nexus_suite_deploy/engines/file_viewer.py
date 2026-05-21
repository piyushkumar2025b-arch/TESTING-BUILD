import streamlit as st
import pandas as pd
import json
import base64
import os

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>📂 Universal Files Inspector</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Inspect, analyze, and view the contents of any file type (CSV, JSON, PDF, Images, Code, Audio, Video) directly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a file to inspect", type=["csv", "json", "pdf", "png", "jpg", "jpeg", "webp", "svg", "mp3", "wav", "mp4", "txt", "py", "js", "html", "css", "md"])

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_ext = os.path.splitext(file_name)[1].lower()
        file_size = len(uploaded_file.getvalue())

        # Render stats card
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.02); padding:12px 18px; border-radius:10px; margin-bottom:20px; border:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <span style='color:#94a3b8; font-size:0.8rem;'>File Inspected:</span>
                <h4 style='margin:2px 0 0 0; color:#fff;'>{file_name}</h4>
            </div>
            <div style='text-align:right;'>
                <span style='color:#94a3b8; font-size:0.8rem;'>Metadata:</span>
                <p style='margin:2px 0 0 0; font-family:monospace; color:#818cf8;'>Size: {file_size/1024:.2f} KB | Type: {file_ext.upper()}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # File inspectors routers
        if file_ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
            st.markdown("### 🖼️ Image Viewer")
            st.image(uploaded_file, use_container_width=True)
            
        elif file_ext == ".csv":
            st.markdown("### 📊 Interactive Data Table")
            try:
                df = pd.read_csv(uploaded_file)
                st.write(f"Dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
                st.dataframe(df, use_container_width=True)
                
                # Optional chart summaries
                num_cols = df.select_dtypes(include=['number']).columns.tolist()
                if num_cols:
                    st.markdown("#### Simple Visualizer")
                    chart_col = st.selectbox("Select numeric column to plot", num_cols)
                    st.line_chart(df[chart_col])
            except Exception as e:
                st.error(f"Error parsing CSV file: {str(e)}")
                
        elif file_ext == ".json":
            st.markdown("### 🌲 Interactive JSON Tree")
            try:
                json_data = json.loads(uploaded_file.getvalue().decode("utf-8"))
                st.json(json_data)
            except Exception as e:
                st.error(f"Error parsing JSON: {str(e)}")
                
        elif file_ext == ".pdf":
            st.markdown("### 📄 PDF Document Reader")
            # PDF embedding in iframe via base64 encoding
            base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
        elif file_ext in [".mp3", ".wav"]:
            st.markdown("### 🔊 Audio Inspector & Visualizer Waveform")
            
            # Encode audio to Base64 for the Web Audio visualizer component
            base64_audio = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            audio_format = "mp3" if file_ext == ".mp3" else "wav"
            data_url = f"data:audio/{audio_format};base64,{base64_audio}"
            
            html_audio_visualizer = f"""
            <div id="vis-container" style="
                background: #090b14;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                padding: 20px;
                max-width: 600px;
                margin: 0 auto;
                text-align: center;
            ">
                <audio id="player-node" controls src="{data_url}" style="width:100%; margin-bottom:15px;"></audio>
                <canvas id="vis-canvas" width="560" height="120" style="display:block; background:#000; border-radius:6px; border:1px solid rgba(255,255,255,0.05);"></canvas>
            </div>
            
            <script>
                const audio = document.getElementById('player-node');
                const canvas = document.getElementById('vis-canvas');
                const ctx = canvas.getContext('2d');
                
                let audioCtx = null;
                let analyser = null;
                let source = null;
                let dataArray = null;
                
                audio.addEventListener('play', () => {{
                    if (!audioCtx) {{
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = audioCtx.createAnalyser();
                        source = audioCtx.createMediaElementSource(audio);
                        source.connect(analyser);
                        analyser.connect(audioCtx.destination);
                        
                        analyser.fftSize = 256;
                        const bufferLength = analyser.frequencyBinCount;
                        dataArray = new Uint8Array(bufferLength);
                        
                        draw();
                    }}
                }});
                
                function draw() {{
                    requestAnimationFrame(draw);
                    if (!analyser) return;
                    
                    const bufferLength = analyser.frequencyBinCount;
                    analyser.getByteFrequencyData(dataArray);
                    
                    ctx.fillStyle = '#000';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    const barWidth = (canvas.width / bufferLength) * 1.5;
                    let barHeight;
                    let x = 0;
                    
                    for(let i = 0; i < bufferLength; i++) {{
                        barHeight = dataArray[i] / 2;
                        
                        // Neon pink/indigo gradient filling
                        const grad = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight);
                        grad.addColorStop(0, '#6366f1');
                        grad.addColorStop(1, '#f472b6');
                        
                        ctx.fillStyle = grad;
                        ctx.fillRect(x, canvas.height - barHeight, barWidth - 2, barHeight);
                        
                        x += barWidth;
                    }}
                }}
            </script>
            """
            st.components.v1.html(html_audio_visualizer, height=225)
            
        elif file_ext == ".mp4":
            st.markdown("### 🎬 Video Player")
            st.video(uploaded_file)
            
        else: # Text or code files
            st.markdown("### 📝 Code & Text Reader")
            try:
                content = uploaded_file.getvalue().decode("utf-8")
                # Syntax highlight dynamically based on extension
                lang = file_ext.replace(".", "")
                if lang == "txt":
                    lang = "plaintext"
                st.code(content, language=lang, line_numbers=True)
            except Exception as e:
                st.error(f"Error reading text content: {str(e)}")
    else:
        st.info("Upload any file above to check details and render it inside the inspect viewports.")
