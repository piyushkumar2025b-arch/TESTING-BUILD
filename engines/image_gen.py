import streamlit as st
import urllib.parse
import requests
import random

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🖼️ HD Image Generator</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Generate stunning high-definition illustrations, concept art, and photorealistic graphics in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_input, col_config = st.columns([2, 1])
    
    with col_input:
        prompt = st.text_area(
            "What do you want to generate?",
            value="A futuristic cybernetic city with neon lights and flying cars, synthwave style",
            height=120
        )
        
        # Style presets
        style_presets = {
            "None": "",
            "Photorealistic": "photorealistic, hyper-detailed, 8k resolution, shot on 35mm lens, dramatic lighting",
            "Anime / Digital Art": "anime style, vibrant colors, detailed line art, masterpiece, high quality digital illustration",
            "Cyberpunk / Neon": "cyberpunk style, neon lights, high contrast, dark atmosphere, retro-futuristic aesthetic",
            "3D Render / Claymation": "3d render, blender render, octane render, cute clay model, smooth surfaces, pastel lighting",
            "Fantasy Oil Painting": "fantasy oil painting, thick visible brushstrokes, classical art style, dramatic canvas"
        }
        selected_style = st.selectbox("Style Preset", list(style_presets.keys()))
        
    with col_config:
        st.markdown("### Image Parameters")
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["1:1 (Square - 1024x1024)", "16:9 (Landscape - 1280x720)", "9:16 (Portrait - 720x1280)", "4:3 (Classic - 1024x768)"]
        )
        
        # Translate aspect ratio to width/height
        dims = {
            "1:1 (Square - 1024x1024)": (1024, 1024),
            "16:9 (Landscape - 1280x720)": (1280, 720),
            "9:16 (Portrait - 720x1280)": (720, 1280),
            "4:3 (Classic - 1024x768)": (1024, 768)
        }
        width, height = dims[aspect_ratio]
        
        model_options = {
            "Flux (Standard/Fast)": "flux",
            "Flux Realism (Photo-focused)": "flux-realism",
            "Flux Anime (Vibrant art)": "flux-anime",
            "Turbo (Extremely Fast)": "turbo"
        }
        selected_model_name = st.selectbox("API Gen Model", list(model_options.keys()))
        selected_model = model_options[selected_model_name]
        
        use_random_seed = st.checkbox("Randomize Seed", value=True)
        if use_random_seed:
            seed = random.randint(1, 99999999)
        else:
            seed = st.number_input("Custom Seed", min_value=1, max_value=99999999, value=42)

    # Compile the final prompt
    final_prompt = prompt
    if selected_style != "None":
        final_prompt += f", {style_presets[selected_style]}"
        
    # URL encode prompt
    encoded_prompt = urllib.parse.quote(final_prompt)
    
    # Pollinations image url structure
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={selected_model}&nologo=true"
    
    import base64
    from engines import database

    # Generate action
    if st.button("Generate Art"):
        with st.spinner("Invoking creative API pipelines..."):
            try:
                # Fetch image bytes to verify load and for downloading
                response = requests.get(image_url, timeout=45)
                if response.status_code == 200:
                    st.markdown("""
                    <div style='text-align: center; margin: 20px 0;'>
                        <p style='color: #6366f1; font-weight: 600;'>Generation Successful!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display generated image
                    st.image(response.content, caption=f"Prompt: {final_prompt} | Seed: {seed}", use_container_width=True)
                    
                    # Add download button
                    st.download_button(
                        label="Download Generated Image (PNG)",
                        data=response.content,
                        file_name=f"nexus_{seed}.png",
                        mime="image/png"
                    )
                    
                    # Convert to base64 and save in database
                    img_base64 = base64.b64encode(response.content).decode()
                    database.save_image_generation(
                        prompt=prompt,
                        style=selected_style,
                        model=selected_model,
                        seed=seed,
                        image_base64=img_base64
                    )
                    st.rerun()
                else:
                    st.error(f"API Error (Status Code {response.status_code}). Please try again.")
            except Exception as e:
                st.error(f"Failed to fetch image from Pollinations API: {str(e)}")
                st.info(f"Fallback: You can preview the image direct link: [Direct Link]({image_url})")

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #a5b4fc;'>🌌 Saved Creations Gallery</h3>", unsafe_allow_html=True)
    
    # Load history
    generations = database.get_image_generations(limit=12)
    if generations:
        cols = st.columns(3)
        for idx, item in enumerate(generations):
            col = cols[idx % 3]
            with col:
                img_data = f"data:image/png;base64,{item['image_base64']}"
                st.markdown(f"""
                <div class='glass-card' style='padding: 10px; margin-bottom: 10px;'>
                    <img src='{img_data}' style='width:100%; border-radius: 8px; margin-bottom: 8px;'/>
                    <div style='font-size:0.8rem; line-height: 1.3;'>
                        <p style='margin: 0; font-weight:600; color:#f472b6; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'>{item['prompt']}</p>
                        <p style='margin: 2px 0 8px 0; color:#94a3b8;'>Model: <b>{item['model']}</b> | Seed: <b>{item['seed']}</b></p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_dl, c_del = st.columns([1, 1])
                with c_dl:
                    st.download_button(
                        label="💾 Download",
                        data=base64.b64decode(item['image_base64']),
                        file_name=f"nexus_gallery_{item['seed']}.png",
                        mime="image/png",
                        key=f"dl_{item['id']}"
                    )
                with c_del:
                    if st.button("🗑️ Delete", key=f"del_{item['id']}"):
                        database.delete_image_generation(item['id'])
                        st.rerun()
    else:
        st.info("No generated images saved locally yet. Complete a prompt above to start your gallery!")

