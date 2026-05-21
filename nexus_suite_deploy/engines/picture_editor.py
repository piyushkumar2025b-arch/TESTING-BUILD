import streamlit as st
import base64
from PIL import Image
import io

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🖌️ AI Photo Studio Canvas</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Apply matrix filters, custom gradient mapping styles, draw overlays, and write annotations onto uploaded images in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Image to Edit (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key="photo_editor_upload")

    if uploaded_file is not None:
        # Load and encode base64
        image = Image.open(uploaded_file)
        
        # Limit sizing for canvas operations
        image.thumbnail((800, 800))
        
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        # HTML canvas editor component
        html_editor = """
        <div id="editor-container" style="
            font-family: 'Outfit', sans-serif;
            background: #0d101c;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 20px;
            max-width: 950px;
            margin: 0 auto;
            color: #f1f5f9;
        ">
            <div style="display:grid; grid-template-columns: 280px 1fr; gap: 20px;">
                <!-- Left Sidebar: Controls -->
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:15px; border-radius:10px; height: 500px; overflow-y: scroll;">
                    <h3 style="margin-top:0; color:#818cf8; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px;">🎛️ SLIDER FILTERS</h3>
                    
                    <div style="margin-bottom:12px;">
                        <label style="font-size:0.85rem; display:block;">Brightness</label>
                        <input type="range" id="val-bright" min="0" max="200" value="100" oninput="applyFilters()" style="width:100%; accent-color:#818cf8;">
                    </div>
                    <div style="margin-bottom:12px;">
                        <label style="font-size:0.85rem; display:block;">Contrast</label>
                        <input type="range" id="val-contrast" min="0" max="200" value="100" oninput="applyFilters()" style="width:100%; accent-color:#818cf8;">
                    </div>
                    <div style="margin-bottom:12px;">
                        <label style="font-size:0.85rem; display:block;">Saturation</label>
                        <input type="range" id="val-saturate" min="0" max="200" value="100" oninput="applyFilters()" style="width:100%; accent-color:#818cf8;">
                    </div>
                    <div style="margin-bottom:12px;">
                        <label style="font-size:0.85rem; display:block;">Blur (px)</label>
                        <input type="range" id="val-blur" min="0" max="10" value="0" oninput="applyFilters()" style="width:100%; accent-color:#818cf8;">
                    </div>
                    <div style="margin-bottom:12px;">
                        <label style="font-size:0.85rem; display:block;">Hue Rotate (deg)</label>
                        <input type="range" id="val-hue" min="0" max="360" value="0" oninput="applyFilters()" style="width:100%; accent-color:#818cf8;">
                    </div>
                    <div style="margin-bottom:18px;">
                        <label style="font-size:0.85rem; display:block;">Invert Color (%)</label>
                        <input type="range" id="val-invert" min="0" max="100" value="0" oninput="applyFilters()" style="width:100%; accent-color:#818cf8;">
                    </div>

                    <h3 style="color:#f472b6; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px; margin-top:20px;">🎨 ESTHETICS & CONVOLUTIONS</h3>
                    <div style="display:grid; grid-template-columns:1fr; gap:8px; margin-bottom:20px;">
                        <button onclick="setMatrixFilter('none')" class="style-btn active-style-btn" id="mat-none">Original</button>
                        <button onclick="setMatrixFilter('sharpen')" class="style-btn" id="mat-sharpen">Sharpen Image</button>
                        <button onclick="setMatrixFilter('edge')" class="style-btn" id="mat-edge">Edge Outlines</button>
                        <button onclick="setMatrixFilter('emboss')" class="style-btn" id="mat-emboss">3D Emboss</button>
                        <button onclick="setMatrixFilter('cyberpunk')" class="style-btn" id="mat-cyber">Cyberpunk (Cyan/Pink)</button>
                        <button onclick="setMatrixFilter('gameboy')" class="style-btn" id="mat-gb">Retro Gameboy (Green)</button>
                        <button onclick="setMatrixFilter('synthwave')" class="style-btn" id="mat-synth">Synthwave Glow</button>
                    </div>

                    <h3 style="color:#10b981; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px; margin-top:20px;">✏️ MARKUP TOOLS</h3>
                    <div style="margin-bottom:12px;">
                        <label style="font-size:0.85rem; display:block;">Brush Mode</label>
                        <div style="display:flex; gap:5px; margin-top:5px;">
                            <button onclick="setTool('draw')" class="tool-btn" id="tool-draw">🖌️ Draw</button>
                            <button onclick="setTool('view')" class="tool-btn active-tool-btn" id="tool-view">👁️ View</button>
                        </div>
                    </div>
                    <div style="margin-bottom:12px;">
                        <label style="font-size:0.85rem; display:block;">Brush Color</label>
                        <input type="color" id="brush-color" value="#f472b6" style="width:100%; border:none; height:30px; border-radius:4px; cursor:pointer; background:none;">
                    </div>
                    <div style="margin-bottom:18px;">
                        <label style="font-size:0.85rem; display:block;">Brush Size</label>
                        <input type="range" id="brush-size" min="2" max="30" value="8" style="width:100%; accent-color:#10b981;">
                    </div>

                    <h3 style="color:#e2e8f0; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px; margin-top:20px;">✍️ ADD TEXT OVERLAY</h3>
                    <div style="margin-bottom:10px;">
                        <input type="text" id="overlay-text" placeholder="Type meme text..." style="width:100%; background:#1e293b; border:1px solid #475569; border-radius:4px; padding:6px; color:#fff; font-size:0.85rem;">
                    </div>
                    <button onclick="addText()" style="background:#10b981; border:none; border-radius:4px; color:#fff; width:100%; padding:6px; font-weight:bold; cursor:pointer; font-size:0.85rem;">Add Caption Text</button>
                </div>

                <!-- Right Pane: Live Viewport Canvas -->
                <div style="display:flex; flex-direction:column; justify-content:space-between;">
                    <div style="
                        flex:1;
                        background:#000;
                        border-radius:10px;
                        border:1px solid rgba(255,255,255,0.05);
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        overflow:hidden;
                        position:relative;
                        min-height: 400px;
                    ">
                        <!-- Canvas -->
                        <canvas id="photo-canvas" style="display:block; max-height:480px; max-width:100%;"></canvas>
                    </div>

                    <!-- Action bottom bar -->
                    <div style="display:flex; justify-content:space-between; margin-top:15px; background:rgba(255,255,255,0.02); padding:10px 15px; border-radius:8px; align-items:center;">
                        <button onclick="resetEditor()" style="background:rgba(239,68,68,0.2); border:1px solid #ef4444; border-radius:6px; color:#f87171; cursor:pointer; padding:6px 14px; font-weight:bold;">RESET CHANGES</button>
                        <button onclick="downloadEdit()" style="background:linear-gradient(135deg,#818cf8,#f472b6); border:none; border-radius:6px; color:#fff; font-weight:bold; padding:8px 20px; cursor:pointer; box-shadow:0 4px 12px rgba(129,140,248,0.4);">EXPORT PNG</button>
                    </div>
                </div>
            </div>
        </div>

        <style>
            .style-btn {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                color: #94a3b8;
                padding: 6px;
                cursor: pointer;
                font-size: 0.85rem;
                transition: all 0.2s;
                text-align: left;
                padding-left: 10px;
            }
            .style-btn:hover {
                background: rgba(255,255,255,0.08);
                color: #fff;
            }
            .active-style-btn {
                background: rgba(244,114,182,0.15) !important;
                border-color: #f472b6 !important;
                color: #f472b6 !important;
                font-weight: 600;
            }
            .tool-btn {
                flex: 1;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                color: #94a3b8;
                padding: 6px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 0.85rem;
            }
            .tool-btn:hover {
                background: rgba(255,255,255,0.08);
                color: #fff;
            }
            .active-tool-btn {
                background: rgba(16,185,129,0.15) !important;
                border-color: #10b981 !important;
                color: #10b981 !important;
                font-weight: 600;
            }
            #editor-container::-webkit-scrollbar {
                width: 6px;
            }
            #editor-container::-webkit-scrollbar-thumb {
                background: rgba(255,255,255,0.1);
                border-radius: 3px;
            }
        </style>

        <script>
            const canvas = document.getElementById('photo-canvas');
            const ctx = canvas.getContext('2d');
            
            let img = new Image();
            let originalImageData = null;
            let activeMatrixFilter = 'none';
            let activeTool = 'view'; // view or draw
            let isDrawing = false;

            // Draw temp layer
            let drawingCanvas = null;
            let drawCtx = null;

            img.onload = function() {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                originalImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                
                // Initialize clean drawings secondary canvas
                drawingCanvas = document.createElement('canvas');
                drawingCanvas.width = canvas.width;
                drawingCanvas.height = canvas.height;
                drawCtx = drawingCanvas.getContext('2d');
                drawCtx.clearRect(0,0,drawingCanvas.width,drawingCanvas.height);

                applyFilters();
            };
            img.src = "{data_url}";

            function setMatrixFilter(filter) {
                activeMatrixFilter = filter;
                document.querySelectorAll('.style-btn').forEach(btn => btn.classList.remove('active-style-btn'));
                const btnIdMap = {
                    'none': 'mat-none', 'sharpen': 'mat-sharpen', 'edge': 'mat-edge',
                    'emboss': 'mat-emboss', 'cyberpunk': 'mat-cyber', 'gameboy': 'mat-gb',
                    'synthwave': 'mat-synth'
                };
                document.getElementById(btnIdMap[filter]).classList.add('active-style-btn');
                applyFilters();
            }

            function setTool(tool) {
                activeTool = tool;
                document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active-tool-btn'));
                if (tool === 'draw') {
                    document.getElementById('tool-draw').classList.add('active-tool-btn');
                } else {
                    document.getElementById('tool-view').classList.add('active-tool-btn');
                }
            }

            // Convolution kernel helper
            function convolve(pixels, weights, opaque) {
                const side = Math.round(Math.sqrt(weights.length));
                const halfSide = Math.floor(side/2);
                const src = pixels.data;
                const sw = pixels.width;
                const sh = pixels.height;
                
                const w = sw;
                const h = sh;
                const output = ctx.createImageData(w, h);
                const dst = output.data;
                
                const alphaFac = opaque ? 1 : 0;
                for (let y=0; y<h; y++) {
                    for (let x=0; x<w; x++) {
                        const sy = y;
                        const sx = x;
                        const dstOff = (y*w+x)*4;
                        
                        let r=0, g=0, b=0, a=0;
                        for (let cy=0; cy<side; cy++) {
                            for (let cx=0; cx<side; cx++) {
                                const scy = Math.min(sh-1, Math.max(0, sy + cy - halfSide));
                                const scx = Math.min(sw-1, Math.max(0, sx + cx - halfSide));
                                const srcOff = (scy*sw+scx)*4;
                                const wt = weights[cy*side+cx];
                                r += src[srcOff] * wt;
                                g += src[srcOff+1] * wt;
                                b += src[srcOff+2] * wt;
                                a += src[srcOff+3] * wt;
                            }
                        }
                        dst[dstOff] = r;
                        dst[dstOff+1] = g;
                        dst[dstOff+2] = b;
                        dst[dstOff+3] = a + alphaFac*(255-a);
                    }
                }
                return output;
            }

            // Canvas filters application pipeline
            function applyFilters() {
                if (!originalImageData) return;
                
                const bright = document.getElementById('val-bright').value;
                const contrast = document.getElementById('val-contrast').value;
                const saturate = document.getElementById('val-saturate').value;
                const blur = document.getElementById('val-blur').value;
                const hue = document.getElementById('val-hue').value;
                const invert = document.getElementById('val-invert').value;

                // 1. Render original image to temp canvas
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = canvas.width;
                tempCanvas.height = canvas.height;
                const tempCtx = tempCanvas.getContext('2d');
                tempCtx.putImageData(originalImageData, 0, 0);

                // 2. Apply base CSS slider filters
                ctx.clearRect(0,0,canvas.width,canvas.height);
                ctx.filter = `brightness(${bright}%) contrast(${contrast}%) saturate(${saturate}%) blur(${blur}px) hue-rotate(${hue}deg) invert(${invert}%)`;
                ctx.drawImage(tempCanvas, 0, 0);
                ctx.filter = 'none'; // reset filter

                // 3. Apply matrix operations
                if (activeMatrixFilter !== 'none') {
                    const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    let outPixels;

                    if (activeMatrixFilter === 'sharpen') {
                        outPixels = convolve(pixels, [
                             0, -1,  0,
                            -1,  5, -1,
                             0, -1,  0
                        ], true);
                        ctx.putImageData(outPixels, 0, 0);
                    } 
                    else if (activeMatrixFilter === 'edge') {
                        outPixels = convolve(pixels, [
                            -1, -1, -1,
                            -1,  8, -1,
                            -1, -1, -1
                        ], true);
                        ctx.putImageData(outPixels, 0, 0);
                    }
                    else if (activeMatrixFilter === 'emboss') {
                        outPixels = convolve(pixels, [
                            -2, -1,  0,
                            -1,  1,  1,
                             0,  1,  2
                        ], true);
                        ctx.putImageData(outPixels, 0, 0);
                    }
                    else if (activeMatrixFilter === 'cyberpunk') {
                        // Cyan/Pink overlay mapping
                        const d = pixels.data;
                        for (let i = 0; i < d.length; i += 4) {
                            const gray = 0.299*d[i] + 0.587*d[i+1] + 0.114*d[i+2];
                            d[i] = gray + 120;     // Boost Red (Pink)
                            d[i+1] = gray - 40;    // Reduce Green
                            d[i+2] = gray + 180;   // Boost Blue (Cyan)
                        }
                        ctx.putImageData(pixels, 0, 0);
                    }
                    else if (activeMatrixFilter === 'gameboy') {
                        // Green scale palette
                        const d = pixels.data;
                        for (let i = 0; i < d.length; i += 4) {
                            const gray = 0.299*d[i] + 0.587*d[i+1] + 0.114*d[i+2];
                            if (gray < 64) {
                                d[i] = 15; d[i+1] = 56; d[i+2] = 15; // Dark green
                            } else if (gray < 128) {
                                d[i] = 48; d[i+1] = 98; d[i+2] = 48; // Med dark green
                            } else if (gray < 192) {
                                d[i] = 139; d[i+1] = 172; d[i+2] = 15; // Med light green
                            } else {
                                d[i] = 155; d[i+1] = 188; d[i+2] = 15; // Light green
                            }
                        }
                        ctx.putImageData(pixels, 0, 0);
                    }
                    else if (activeMatrixFilter === 'synthwave') {
                        // Deep violet/sunset gradient overlay mapping
                        const d = pixels.data;
                        for (let i = 0; i < d.length; i += 4) {
                            const gray = 0.299*d[i] + 0.587*d[i+1] + 0.114*d[i+2];
                            d[i] = gray + 90;     // Red glow
                            d[i+1] = gray - 80;    // Deepen green
                            d[i+2] = gray + 100;   // Violet blue
                        }
                        ctx.putImageData(pixels, 0, 0);
                    }
                }

                // 4. Paint drawings on top
                if (drawingCanvas) {
                    ctx.drawImage(drawingCanvas, 0, 0);
                }
            }

            // Brush Drawings Events
            canvas.addEventListener('mousedown', function(e) {
                if (activeTool !== 'draw') return;
                isDrawing = true;
                draw(e);
            });
            canvas.addEventListener('mousemove', draw);
            canvas.addEventListener('mouseup', () => isDrawing = false);
            canvas.addEventListener('mouseout', () => isDrawing = false);

            function draw(e) {
                if (!isDrawing || activeTool !== 'draw') return;
                
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = (e.clientX - rect.left) * scaleX;
                const y = (e.clientY - rect.top) * scaleY;

                const color = document.getElementById('brush-color').value;
                const size = document.getElementById('brush-size').value;

                drawCtx.lineWidth = size;
                drawCtx.lineCap = 'round';
                drawCtx.strokeStyle = color;

                drawCtx.lineTo(x, y);
                drawCtx.stroke();
                drawCtx.beginPath();
                drawCtx.moveTo(x, y);

                applyFilters();
            }

            // Text Overlays
            function addText() {
                const text = document.getElementById('overlay-text').value;
                if (!text.trim()) return;

                drawCtx.font = 'bold 36px Outfit, Inter, sans-serif';
                drawCtx.fillStyle = '#ffffff';
                drawCtx.strokeStyle = '#000000';
                drawCtx.lineWidth = 4;
                drawCtx.textAlign = 'center';
                
                // Add text at center of canvas bottom
                const tx = canvas.width / 2;
                const ty = canvas.height - 40;
                
                drawCtx.strokeText(text, tx, ty);
                drawCtx.fillText(text, tx, ty);

                document.getElementById('overlay-text').value = '';
                applyFilters();
            }

            function resetEditor() {
                document.getElementById('val-bright').value = 100;
                document.getElementById('val-contrast').value = 100;
                document.getElementById('val-saturate').value = 100;
                document.getElementById('val-blur').value = 0;
                document.getElementById('val-hue').value = 0;
                document.getElementById('val-invert').value = 0;
                
                activeMatrixFilter = 'none';
                document.querySelectorAll('.style-btn').forEach(btn => btn.classList.remove('active-style-btn'));
                document.getElementById('mat-none').classList.add('active-style-btn');
                
                if (drawCtx) {
                    drawCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
                }
                
                applyFilters();
            }

            function downloadEdit() {
                const link = document.createElement('a');
                link.download = 'nexus_studio_edit.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            }
        </script>
        """
        st.components.v1.html(html_editor.replace("{data_url}", data_url), height=650)
    else:
        st.info("Upload an image above to unlock the Canvas AI Photo Studio.")
