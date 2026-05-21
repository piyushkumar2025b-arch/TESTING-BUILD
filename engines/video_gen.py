import streamlit as st
import requests
import json
import urllib.parse
import re

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🎬 Cinematic Storyboard Video</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Convert a story idea into a fully-realized animated storyboard. Combines AI scripting, imagery, panning effects, and synth ambient audio.
        </p>
    </div>
    """, unsafe_allow_html=True)

    video_prompt = st.text_area(
        "Enter your video script concept",
        value="An explorer walking through a dense luminous jungle, finding a hidden glowing temple, opening the ancient gates, and stepping into a golden dimension.",
        height=90
    )
    
    if st.button("Generate Storyboard Video"):
        with st.spinner("Synthesizing cinematic scripts and rendering storyboard keyframes..."):
            # Step 1: Query Pollinations Text to break down the concept into 4 scenes
            system_prompt = (
                "You are an expert storyboard scriptwriter. Break down the user's concept into exactly 4 chronological scenes. "
                "Output ONLY a valid JSON array of objects. Do not include markdown code block wrappers (like ```json). "
                "Each object MUST contain two keys: "
                "1. 'image_prompt': a detailed prompt for generating the image of this scene (e.g. including art style like 'cinematic photography, detailed landscape, depth of field'). "
                "2. 'subtitles': a short subtitle narrative (max 15 words) describing the scene. "
                "Be highly creative and cinematic."
            )
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": video_prompt}
                ],
                "model": "openai"
            }
            
            try:
                res = requests.post("https://text.pollinations.ai/", json=payload, timeout=20)
                if res.status_code == 200:
                    raw_text = res.text.strip()
                    # Clean markdown wrappers if returned
                    raw_text = re.sub(r"^```json\s*", "", raw_text, flags=re.IGNORECASE)
                    raw_text = re.sub(r"^```\s*", "", raw_text, flags=re.IGNORECASE)
                    raw_text = re.sub(r"\s*```$", "", raw_text, flags=re.IGNORECASE)
                    
                    try:
                        storyboard = json.loads(raw_text)
                    except Exception as json_err:
                        st.error("AI returned an invalid JSON script. Retrying fallback script extraction...")
                        # Fallback parsing with regex if json fails
                        storyboard = []
                        prompts = re.findall(r'"image_prompt"\s*:\s*"([^"]+)"', raw_text)
                        subs = re.findall(r'"subtitles"\s*:\s*"([^"]+)"', raw_text)
                        for p, s in zip(prompts[:4], subs[:4]):
                            storyboard.append({"image_prompt": p, "subtitles": s})
                            
                    if len(storyboard) < 4:
                        # Direct hardcoded fallback if parsing was completely corrupted
                        storyboard = [
                            {"image_prompt": f"Scene 1: {video_prompt}, cinematic wide shot, detailed art", "subtitles": "The journey begins..."},
                            {"image_prompt": f"Scene 2: Exploring further, epic perspective, cinematic lights", "subtitles": "Venturing deeper into the unknown."},
                            {"image_prompt": f"Scene 3: A dramatic discovery, glowing colors, masterwork", "subtitles": "Beholding a grand revelation."},
                            {"image_prompt": f"Scene 4: The climax, beautiful particles, full cinematic detail", "subtitles": "Stepping forward into destiny."}
                        ]

                    # Step 2: Formulate image URLs for each frame
                    scene_data = []
                    for idx, scene in enumerate(storyboard):
                        image_prompt = scene.get("image_prompt", f"Scene {idx+1}")
                        subtitles = scene.get("subtitles", "Narrating scene...")
                        
                        # Add high-quality aesthetic keywords
                        styled_prompt = f"{image_prompt}, cinematic lighting, photorealistic, 8k, aspect ratio 16:9"
                        encoded = urllib.parse.quote(styled_prompt)
                        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=960&height=540&seed={2026 + idx}&model=flux"
                        
                        scene_data.append({
                            "url": img_url,
                            "subtitles": subtitles
                        })
                        
                    # HTML and JS to display a video player component with audio oscillator pads
                    # The component does crossfade, Ken Burns zooming scale, and subtitles rendering
                    html_carousel = f"""
                    <div id="video-canvas-container" style="
                        width: 100%;
                        max-width: 800px;
                        margin: 0 auto;
                        background: #000;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
                        position: relative;
                        aspect-ratio: 16/9;
                        border: 1px solid rgba(255,255,255,0.1);
                    ">
                        <!-- Play/Pause & Sound Button -->
                        <div id="controls-bar" style="
                            position: absolute;
                            top: 15px;
                            left: 15px;
                            z-index: 10;
                            display: flex;
                            gap: 10px;
                        ">
                            <button onclick="togglePlayback()" id="play-btn" style="
                                background: rgba(99, 102, 241, 0.85);
                                color: white;
                                border: none;
                                border-radius: 6px;
                                padding: 6px 14px;
                                font-weight: bold;
                                cursor: pointer;
                            ">PLAY VIDEO</button>
                            <button onclick="toggleSound()" id="sound-btn" style="
                                background: rgba(255, 255, 255, 0.2);
                                color: white;
                                border: none;
                                border-radius: 6px;
                                padding: 6px 14px;
                                cursor: pointer;
                            ">🔊 SOUND ON</button>
                        </div>
                        
                        <!-- Timeline track -->
                        <div id="timeline" style="
                            position: absolute;
                            bottom: 60px;
                            left: 5%;
                            width: 90%;
                            height: 4px;
                            background: rgba(255,255,255,0.2);
                            border-radius: 2px;
                            z-index: 10;
                        ">
                            <div id="progress-bar" style="width: 0%; height: 100%; background: #f472b6; border-radius: 2px; transition: width 0.1s linear;"></div>
                        </div>

                        <!-- Image frames container -->
                        <div id="viewport" style="width: 100%; height: 100%; position: relative;">
                            { "".join([f'<div class="slide" id="slide-{i}" style="width: 100%; height: 100%; position: absolute; top:0; left:0; opacity: 0; transition: opacity 1.5s ease-in-out; background-image: url(\'{scene["url"]}\'); background-size: cover; background-position: center;"></div>' for i, scene in enumerate(scene_data)]) }
                        </div>

                        <!-- Subtitle overlay -->
                        <div id="subtitle-box" style="
                            position: absolute;
                            bottom: 15px;
                            left: 5%;
                            width: 90%;
                            text-align: center;
                            font-family: 'Outfit', sans-serif;
                            font-size: 1.2rem;
                            font-weight: 500;
                            color: #ffffff;
                            text-shadow: 0 2px 8px rgba(0,0,0,0.9), 0 0 10px rgba(0,0,0,0.5);
                            background: rgba(0,0,0,0.4);
                            padding: 8px 15px;
                            border-radius: 6px;
                            z-index: 10;
                            box-sizing: border-box;
                        ">
                            Loading storyboard narrative...
                        </div>
                    </div>

                    <style>
                        /* Ken Burns Animation Class */
                        .kb-active {{
                            animation: kenburns 8s ease forwards;
                        }}
                        @keyframes kenburns {{
                            0% {{ transform: scale(1.0) translate(0, 0); }}
                            100% {{ transform: scale(1.12) translate(-2%, -1%); }}
                        }}
                    </style>

                    <script>
                        const scenes = {json.dumps(scene_data)};
                        let currentIdx = 0;
                        let isPlaying = false;
                        let soundEnabled = true;
                        let audioCtx = null;
                        let ambientOsc = null;
                        let playbackInterval = null;
                        let timelineInterval = null;
                        const durationPerScene = 6000; // 6 seconds per scene
                        let sceneStartTime = 0;

                        function setupAudio() {{
                            if (!audioCtx) {{
                                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                            }}
                            if (audioCtx.state === 'suspended') {{
                                audioCtx.resume();
                            }}
                        }}

                        function startAmbientSynth(freq) {{
                            if (!soundEnabled) return;
                            setupAudio();
                            try {{
                                // Create synth pad
                                ambientOsc = audioCtx.createOscillator();
                                const filter = audioCtx.createBiquadFilter();
                                const gainNode = audioCtx.createGain();

                                ambientOsc.type = 'triangle';
                                ambientOsc.frequency.setValueAtTime(freq, audioCtx.currentTime);

                                filter.type = 'lowpass';
                                filter.frequency.setValueAtTime(250, audioCtx.currentTime);

                                gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
                                gainNode.gain.linearRampToValueAtTime(0.08, audioCtx.currentTime + 1.5);

                                ambientOsc.connect(filter);
                                filter.connect(gainNode);
                                gainNode.connect(audioCtx.destination);

                                ambientOsc.start();
                                
                                // Sweep gain down on transition
                                setTimeout(() => {{
                                    gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 1.0);
                                    setTimeout(() => {{
                                        ambientOsc.stop();
                                    }}, 1000);
                                }}, durationPerScene - 1200);

                            }} catch(e) {{ console.log(e); }}
                        }}

                        function showScene(idx) {{
                            // Reset slides classes and opacity
                            for(let i=0; i<4; i++) {{
                                const slide = document.getElementById('slide-' + i);
                                slide.style.opacity = '0';
                                slide.classList.remove('kb-active');
                            }}

                            const activeSlide = document.getElementById('slide-' + idx);
                            activeSlide.style.opacity = '1';
                            activeSlide.classList.add('kb-active');

                            const subtitleBox = document.getElementById('subtitle-box');
                            subtitleBox.innerText = scenes[idx].subtitles;

                            // Synth chord sweeps depending on scene idx
                            const frequencies = [110, 130.81, 146.83, 164.81]; // A2, C3, D3, E3
                            startAmbientSynth(frequencies[idx]);
                            
                            sceneStartTime = Date.now();
                        }}

                        function togglePlayback() {{
                            const btn = document.getElementById('play-btn');
                            if (isPlaying) {{
                                clearInterval(playbackInterval);
                                clearInterval(timelineInterval);
                                isPlaying = false;
                                btn.innerText = "PLAY VIDEO";
                                btn.style.background = "rgba(99, 102, 241, 0.85)";
                            }} else {{
                                setupAudio();
                                isPlaying = true;
                                btn.innerText = "PAUSE";
                                btn.style.background = "#ef4444";
                                
                                showScene(currentIdx);
                                playbackInterval = setInterval(() => {{
                                    currentIdx = (currentIdx + 1) % 4;
                                    showScene(currentIdx);
                                }}, durationPerScene);

                                timelineInterval = setInterval(() => {{
                                    const elapsed = Date.now() - sceneStartTime;
                                    const pct = Math.min((elapsed / durationPerScene) * 100, 100);
                                    document.getElementById('progress-bar').style.width = pct + '%';
                                }}, 100);
                            }}
                        }}

                        function toggleSound() {{
                            soundEnabled = !soundEnabled;
                            const btn = document.getElementById('sound-btn');
                            if (soundEnabled) {{
                                btn.innerText = "🔊 SOUND ON";
                                btn.style.background = "rgba(255, 255, 255, 0.2)";
                            }} else {{
                                btn.innerText = "🔇 MUTED";
                                btn.style.background = "rgba(239, 68, 68, 0.4)";
                            }}
                        }}

                        // Initial display of the first slide
                        showScene(0);
                    </script>
                    """
                    
                    st.components.v1.html(html_carousel, height=520)
                    
                    # Also display standard grid of the rendered slides for manual download
                    st.markdown("### 📷 Storyboard Frames Download")
                    cols = st.columns(4)
                    for c_idx, col in enumerate(cols):
                        with col:
                            st.image(scene_data[c_idx]["url"], caption=f"Scene {c_idx+1}: {storyboard[c_idx]['subtitles']}", use_container_width=True)
                            try:
                                img_data = requests.get(scene_data[c_idx]["url"], timeout=10).content
                                st.download_button(
                                    label=f"Save Frame {c_idx+1}",
                                    data=img_data,
                                    file_name=f"frame_{c_idx+1}.png",
                                    mime="image/png",
                                    key=f"dl_frame_{c_idx}"
                                )
                            except:
                                pass
                else:
                    st.error("Failed to fetch storyboard script from AI model.")
            except Exception as e:
                st.error(f"Error executing storyboard logic: {str(e)}")
