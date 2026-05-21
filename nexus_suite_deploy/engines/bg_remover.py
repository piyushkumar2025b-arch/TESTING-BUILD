import streamlit as st
import base64
from PIL import Image
import io

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>✂️ Background Remover (Chroma Key & Threshold)</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Remove backgrounds from images instantly in your browser. Click on any color in the image to make it transparent, or use threshold masks.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Read and convert image to Base64 so we can pass it to the HTML component
        image = Image.open(uploaded_file)
        
        # Max dimension scaling to prevent performance issues in Canvas
        image.thumbnail((800, 800))
        
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        # HTML canvas app for pixel manipulation
        html_remover = """
        <div id="bg-remover-app" style="
            font-family: 'Outfit', sans-serif;
            color: #f1f5f9;
            background: #0d101c;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
        ">
            <!-- Controls -->
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:15px; margin-bottom:20px; background:rgba(255,255,255,0.02); padding:15px; border-radius:8px;">
                <div>
                    <label style="display:block; margin-bottom:5px; font-weight:600; font-size:0.9rem;">Mode</label>
                    <select id="remove-mode" onchange="switchMode()" style="width:100%; background:#1e293b; border:1px solid #475569; color:white; padding:6px; border-radius:6px; cursor:pointer;">
                        <option value="chromakey">Chroma Key (Click to Select Color)</option>
                        <option value="bright-threshold">Remove Bright (White/Grey BG)</option>
                        <option value="dark-threshold">Remove Dark (Black/Dark BG)</option>
                    </select>
                </div>
                <div>
                    <label style="display:block; margin-bottom:5px; font-weight:600; font-size:0.9rem;">Tolerance (Color Match)</label>
                    <input type="range" id="tolerance" min="1" max="100" value="25" oninput="processImage()" style="width:100%; accent-color:#818cf8;">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8;">
                        <span>Narrow</span><span id="tol-val">25</span><span>Wide</span>
                    </div>
                </div>
                <div>
                    <label style="display:block; margin-bottom:5px; font-weight:600; font-size:0.9rem;">Edge Feathering (Blur)</label>
                    <input type="range" id="feather" min="0" max="10" value="1" oninput="processImage()" style="width:100%; accent-color:#f472b6;">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8;">
                        <span>None</span><span id="feat-val">1px</span><span>Soft</span>
                    </div>
                </div>
            </div>

            <!-- Canvas viewport -->
            <div style="text-align:center; margin-bottom:20px; position:relative; overflow:hidden;">
                <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:8px;" id="mode-tip">💡 Tip: Click anywhere on the image below to sample and remove that background color.</p>
                <div style="
                    display: inline-block;
                    position: relative;
                    border: 2px dashed rgba(255,255,255,0.1);
                    border-radius: 8px;
                    background-image: 
                        linear-gradient(45deg, #1e293b 25%, transparent 25%), 
                        linear-gradient(-45deg, #1e293b 25%, transparent 25%), 
                        linear-gradient(45deg, transparent 75%, #1e293b 75%), 
                        linear-gradient(-45deg, transparent 75%, #1e293b 75%);
                    background-size: 20px 20px;
                    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                ">
                    <canvas id="image-canvas" style="display:block; max-width:100%; cursor:crosshair;"></canvas>
                </div>
            </div>

            <!-- Selected Key Color Preview -->
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:15px; padding:10px; background:rgba(255,255,255,0.02); border-radius:6px;">
                <div style="display:flex; align-items:center;">
                    <span style="font-weight:600; font-size:0.9rem; margin-right:10px;">Target Key Color:</span>
                    <div id="color-preview" style="width:25px; height:25px; border-radius:4px; border:1px solid #fff; background:#ffffff;"></div>
                    <span id="color-rgb" style="font-family:monospace; margin-left:10px; font-size:0.85rem;">rgb(255,255,255)</span>
                </div>
                <button onclick="downloadPNG()" style="
                    background: linear-gradient(135deg, #818cf8, #f472b6);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 18px;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(129, 140, 248, 0.4);
                ">📥 Download PNG (Transparent)</button>
            </div>
        </div>

        <script>
            const canvas = document.getElementById('image-canvas');
            const ctx = canvas.getContext('2d');
            
            // Loaded image instance
            let img = new Image();
            let originalImageData = null;
            let targetColor = { r: 255, g: 255, b: 255 }; // Default key is white

            img.onload = function() {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                originalImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                processImage();
            };
            img.src = "{data_url}";

            // Capture clicks on canvas to sample chroma color
            canvas.addEventListener('click', function(e) {
                if (document.getElementById('remove-mode').value !== 'chromakey') return;

                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = Math.floor((e.clientX - rect.left) * scaleX);
                const y = Math.floor((e.clientY - rect.top) * scaleY);

                // Sample pixel
                const pixelIndex = (y * canvas.width + x) * 4;
                targetColor.r = originalImageData.data[pixelIndex];
                targetColor.g = originalImageData.data[pixelIndex + 1];
                targetColor.b = originalImageData.data[pixelIndex + 2];

                // Update UI previewer
                document.getElementById('color-preview').style.background = `rgb(${targetColor.r}, ${targetColor.g}, ${targetColor.b})`;
                document.getElementById('color-rgb').innerText = `rgb(${targetColor.r}, ${targetColor.g}, ${targetColor.b})`;

                processImage();
            });

            function switchMode() {
                const mode = document.getElementById('remove-mode').value;
                const tip = document.getElementById('mode-tip');
                if (mode === 'chromakey') {
                    tip.innerText = "💡 Tip: Click anywhere on the image below to sample and remove that background color.";
                } else if (mode === 'bright-threshold') {
                    tip.innerText = "💡 Adjust Tolerance to change the brightness threshold. Fades out light pixels.";
                } else {
                    tip.innerText = "💡 Adjust Tolerance to change the darkness threshold. Fades out dark pixels.";
                }
                processImage();
            }

            // Sync visual labels
            document.getElementById('tolerance').oninput = function() {
                document.getElementById('tol-val').innerText = this.value;
                processImage();
            };
            document.getElementById('feather').oninput = function() {
                document.getElementById('feat-val').innerText = this.value + "px";
                processImage();
            };

            function processImage() {
                if (!originalImageData) return;
                
                const mode = document.getElementById('remove-mode').value;
                const tolerance = parseFloat(document.getElementById('tolerance').value);
                const feather = parseInt(document.getElementById('feather').value);
                
                // Get fresh output buffer
                const outImageData = ctx.createImageData(canvas.width, canvas.height);
                const srcData = originalImageData.data;
                const destData = outImageData.data;

                // Color removal loops
                for (let i = 0; i < srcData.length; i += 4) {
                    const r = srcData[i];
                    const g = srcData[i+1];
                    const b = srcData[i+2];
                    const a = srcData[i+3];

                    let alpha = a;

                    if (mode === 'chromakey') {
                        // Euclidean color distance
                        const diffR = r - targetColor.r;
                        const diffG = g - targetColor.g;
                        const diffB = b - targetColor.b;
                        const distance = Math.sqrt(diffR*diffR + diffG*diffG + diffB*diffB);

                        // Threshold evaluation (scale distance to max of 442)
                        const normDistance = (distance / 442) * 100;
                        if (normDistance < tolerance) {
                            // Soft edge feathering calculations
                            if (feather > 0 && normDistance > tolerance - feather) {
                                const ratio = (normDistance - (tolerance - feather)) / feather;
                                alpha = Math.floor(a * ratio);
                            } else {
                                alpha = 0;
                            }
                        }
                    } 
                    else if (mode === 'bright-threshold') {
                        // Calculate brightness
                        const brightness = 0.299 * r + 0.587 * g + 0.114 * b;
                        const cutoff = 255 - (tolerance * 2.5); // scale 1-100 to 255
                        if (brightness > cutoff) {
                            if (feather > 0 && brightness < cutoff + (feather * 5)) {
                                const ratio = (brightness - cutoff) / (feather * 5);
                                alpha = Math.floor(a * ratio);
                            } else {
                                alpha = 0;
                            }
                        }
                    }
                    else if (mode === 'dark-threshold') {
                        const brightness = 0.299 * r + 0.587 * g + 0.114 * b;
                        const cutoff = tolerance * 2.5;
                        if (brightness < cutoff) {
                            if (feather > 0 && brightness > cutoff - (feather * 5)) {
                                const ratio = (cutoff - brightness) / (feather * 5);
                                alpha = Math.floor(a * ratio);
                            } else {
                                alpha = 0;
                            }
                        }
                    }

                    destData[i] = r;
                    destData[i+1] = g;
                    destData[i+2] = b;
                    destData[i+3] = alpha;
                }

                ctx.putImageData(outImageData, 0, 0);
            }

            function downloadPNG() {
                const link = document.createElement('a');
                link.download = 'nexus_no_bg.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            }
        </script>
        """
        
        st.components.v1.html(html_remover.replace("{data_url}", data_url), height=680)
    else:
        st.info("Please upload an image above to activate the Canvas Background Remover.")
