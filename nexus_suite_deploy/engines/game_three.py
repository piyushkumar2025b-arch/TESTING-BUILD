import streamlit as st

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🎮 3D Space Shooter (Three.js Arcade)</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Play an action-packed retro 3D space shooter built with WebGL (Three.js). Dodge asteroids, shoot targets, and aim for the high score!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Embed Three.js Game
    html_game = """
    <div id="game-wrapper" style="
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        overflow: hidden;
        position: relative;
        background: #000;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
    ">
        <!-- Game HUD -->
        <div id="hud" style="
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'Outfit', sans-serif;
            color: #fff;
            z-index: 10;
            pointer-events: none;
        ">
            <div style="background:rgba(0,0,0,0.6); padding:8px 15px; border-radius:6px; border:1px solid rgba(255,255,255,0.1);">
                SCORE: <span id="score-val" style="color:#f472b6; font-weight:bold;">0</span>
            </div>
            <div style="background:rgba(0,0,0,0.6); padding:8px 15px; border-radius:6px; border:1px solid rgba(255,255,255,0.1);">
                SHIELD: <span id="shield-val" style="color:#10b981; font-weight:bold;">100%</span>
            </div>
        </div>

        <!-- Start/Game Over Overlay -->
        <div id="menu-overlay" style="
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(5,6,11,0.85);
            backdrop-filter: blur(8px);
            z-index: 20;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: 'Outfit', sans-serif;
            color: #fff;
            text-align: center;
            padding: 20px;
            box-sizing: border-box;
        ">
            <h1 id="menu-title" style="margin:0 0 10px 0; font-size:2.5rem; background:linear-gradient(135deg, #a5b4fc, #f472b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">AETHER FIGHTER 3D</h1>
            <p id="menu-desc" style="color:#94a3b8; max-width:400px; margin:0 0 25px 0; font-size:0.95rem; line-height:1.5;">
                Fly through the asteroid belt. Use <b>A/D</b> or <b>Left/Right Arrows</b> to steer, and press <b>SPACEBAR</b> to fire plasma lasers.
            </p>
            <button onclick="startGame()" style="
                background: linear-gradient(135deg, #818cf8, #f472b6);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 12px 30px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(129, 140, 248, 0.4);
                transition: transform 0.2s;
            ">LAUNCH MISSION</button>
        </div>

        <!-- Canvas Container -->
        <div id="canvas-container" style="width:100%; height:450px; display:block;"></div>
    </div>

    <!-- Include Three.js via CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <script>
        let scene, camera, renderer, ship, starField;
        let obstacles = [];
        let lasers = [];
        let keys = {};
        
        let gameActive = false;
        let score = 0;
        let shield = 100;
        
        let lastObstacleSpawn = 0;
        let speedMultiplier = 1;
        
        // Procedural Audio Context
        let audioCtx = null;
        function playSound(type) {
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') audioCtx.resume();
                
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                
                const now = audioCtx.currentTime;
                
                if (type === 'laser') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(500, now);
                    osc.frequency.exponentialRampToValueAtTime(100, now + 0.15);
                    gain.gain.setValueAtTime(0.08, now);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
                    osc.start(now);
                    osc.stop(now + 0.16);
                } 
                else if (type === 'hit') {
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(120, now);
                    osc.frequency.linearRampToValueAtTime(30, now + 0.3);
                    gain.gain.setValueAtTime(0.2, now);
                    gain.gain.linearRampToValueAtTime(0, now + 0.3);
                    osc.start(now);
                    osc.stop(now + 0.31);
                }
                else if (type === 'explode') {
                    // White noise simulation
                    const bufferSize = audioCtx.sampleRate * 0.4;
                    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                    const data = buffer.getChannelData(0);
                    for (let i = 0; i < bufferSize; i++) {
                        data[i] = Math.random() * 2 - 1;
                    }
                    const noiseNode = audioCtx.createBufferSource();
                    noiseNode.buffer = buffer;
                    
                    const filter = audioCtx.createBiquadFilter();
                    filter.type = 'lowpass';
                    filter.frequency.setValueAtTime(400, now);
                    filter.frequency.exponentialRampToValueAtTime(10, now + 0.4);
                    
                    noiseNode.connect(filter);
                    filter.connect(gain);
                    gain.gain.setValueAtTime(0.25, now);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
                    noiseNode.start(now);
                    noiseNode.stop(now + 0.41);
                }
            } catch(e){}
        }

        // Initialize 3D Environment
        function initEngine() {
            const container = document.getElementById('canvas-container');
            const width = container.clientWidth;
            const height = container.clientHeight;

            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x05060b, 0.015);

            camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
            camera.position.set(0, 2, 8);

            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
            renderer.setSize(width, height);
            renderer.setClearColor(0x05060b, 1);
            container.appendChild(renderer.domElement);

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 2);
            dirLight.position.set(5, 10, 7);
            scene.add(dirLight);

            // Starfield Background Particle system
            const starGeo = new THREE.BufferGeometry();
            const starCount = 600;
            const starPositions = new Float32Array(starCount * 3);
            for(let i=0; i<starCount*3; i+=3) {
                starPositions[i] = (Math.random() - 0.5) * 80;
                starPositions[i+1] = (Math.random() - 0.5) * 80;
                starPositions[i+2] = -Math.random() * 200;
            }
            starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
            
            const starMat = new THREE.PointsMaterial({
                color: 0xffffff,
                size: 0.15,
                transparent: true,
                opacity: 0.8
            });
            starField = new THREE.Points(starGeo, starMat);
            scene.add(starField);

            // Build Player Ship (Metallic fighter geometry)
            const shipGroup = new THREE.Group();
            
            // Cockpit
            const cockpitGeo = new THREE.ConeGeometry(0.35, 1.5, 5);
            cockpitGeo.rotateX(Math.PI / 2);
            const cockpitMat = new THREE.MeshPhongMaterial({ color: 0x818cf8, shininess: 80 });
            const cockpit = new THREE.Mesh(cockpitGeo, cockpitMat);
            shipGroup.add(cockpit);

            // Wings
            const wingGeo = new THREE.BoxGeometry(2.2, 0.08, 0.6);
            const wingMat = new THREE.MeshPhongMaterial({ color: 0x312e81, metalness: 0.8 });
            const wings = new THREE.Mesh(wingGeo, wingMat);
            wings.position.set(0, -0.1, -0.2);
            shipGroup.add(wings);

            // Thruster glow indicators
            const thrusterGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.3, 8);
            thrusterGeo.rotateX(Math.PI/2);
            const thrusterMat = new THREE.MeshBasicMaterial({ color: 0xf472b6 });
            const thruster = new THREE.Mesh(thrusterGeo, thrusterMat);
            thruster.position.set(0, -0.05, 0.8);
            shipGroup.add(thruster);

            ship = shipGroup;
            ship.position.set(0, 0, 0);
            scene.add(ship);

            // Resize listeners
            window.addEventListener('resize', onWindowResize);
        }

        function onWindowResize() {
            const container = document.getElementById('canvas-container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }

        // Start gameplay
        function startGame() {
            document.getElementById('menu-overlay').style.display = 'none';
            playSound('explode');
            
            // Reset states
            score = 0;
            shield = 100;
            speedMultiplier = 1;
            gameActive = true;
            
            document.getElementById('score-val').innerText = score;
            document.getElementById('shield-val').innerText = shield + "%";
            document.getElementById('shield-val').style.color = '#10b981';

            // Clear obstacles
            for(let obs of obstacles) scene.remove(obs.mesh);
            obstacles = [];
            
            // Clear lasers
            for(let l of lasers) scene.remove(l.mesh);
            lasers = [];
            
            ship.position.set(0, 0, 0);
        }

        // Keyboard bindings
        window.addEventListener('keydown', e => {
            keys[e.code] = true;
            if (e.code === 'Space' && gameActive) {
                fireLaser();
                e.preventDefault();
            }
        });
        window.addEventListener('keyup', e => {
            keys[e.code] = false;
        });

        function fireLaser() {
            playSound('laser');
            
            const laserGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.8, 4);
            laserGeo.rotateX(Math.PI/2);
            const laserMat = new THREE.MeshBasicMaterial({ color: 0xf472b6 });
            
            // Spawn twin lasers from wings
            [-0.8, 0.8].forEach(offsetX => {
                const laserMesh = new THREE.Mesh(laserGeo, laserMat);
                laserMesh.position.set(ship.position.x + offsetX, ship.position.y - 0.1, ship.position.z - 0.8);
                scene.add(laserMesh);
                lasers.push({ mesh: laserMesh });
            });
        }

        // Obstacles generator (asteroids)
        function spawnObstacle(time) {
            if (time - lastObstacleSpawn > 1200 / speedMultiplier) {
                lastObstacleSpawn = time;

                // Sphere asteroid geometry
                const size = 0.6 + Math.random() * 0.9;
                const obsGeo = new THREE.DodecahedronGeometry(size, 1);
                
                // Color theme variation
                const obsMat = new THREE.MeshPhongMaterial({
                    color: 0x475569,
                    shininess: 10,
                    flatShading: true
                });
                const obsMesh = new THREE.Mesh(obsGeo, obsMat);
                
                // Position far off screen with random grid layout
                obsMesh.position.set(
                    (Math.random() - 0.5) * 12,
                    (Math.random() - 0.5) * 6,
                    -150
                );
                
                scene.add(obsMesh);
                obstacles.push({
                    mesh: obsMesh,
                    speed: 1.2 + Math.random() * 1.5,
                    rotSpeedX: Math.random() * 0.02,
                    rotSpeedY: Math.random() * 0.02,
                    radius: size
                });
            }
        }

        // Main Gameloop logic
        function animate(timestamp) {
            requestAnimationFrame(animate);
            if (!renderer) return;

            if (gameActive) {
                // Steering Controls (WSAD / ARROWS)
                const steerSpeed = 0.15;
                if (keys['KeyA'] || keys['ArrowLeft']) {
                    ship.position.x = Math.max(ship.position.x - steerSpeed, -6);
                    ship.rotation.z = Math.min(ship.rotation.z + 0.05, 0.4);
                } else if (keys['KeyD'] || keys['ArrowRight']) {
                    ship.position.x = Math.min(ship.position.x + steerSpeed, 6);
                    ship.rotation.z = Math.max(ship.rotation.z - 0.05, -0.4);
                } else {
                    ship.rotation.z *= 0.85; // return wing tilt
                }

                if (keys['KeyW'] || keys['ArrowUp']) {
                    ship.position.y = Math.min(ship.position.y + steerSpeed, 3.5);
                    ship.rotation.x = Math.max(ship.rotation.x - 0.04, -0.2);
                } else if (keys['KeyS'] || keys['ArrowDown']) {
                    ship.position.y = Math.max(ship.position.y - steerSpeed, -3.5);
                    ship.rotation.x = Math.min(ship.rotation.x + 0.04, 0.2);
                } else {
                    ship.rotation.x *= 0.85;
                }

                // Starfield motion
                const positions = starField.geometry.attributes.position.array;
                for(let i=2; i<positions.length; i+=3) {
                    positions[i] += 1.5 * speedMultiplier;
                    if (positions[i] > 5) {
                        positions[i] = -200; // reset stars behind fog
                    }
                }
                starField.geometry.attributes.position.needsUpdate = true;

                // Speed scale
                speedMultiplier = 1 + (score / 1500);

                // Spawn and move obstacles
                spawnObstacle(timestamp);
                
                for(let idx = obstacles.length - 1; idx >= 0; idx--) {
                    const obs = obstacles[idx];
                    obs.mesh.position.z += obs.speed * speedMultiplier;
                    
                    // Spin asteroid
                    obs.mesh.rotation.x += obs.rotSpeedX;
                    obs.mesh.rotation.y += obs.rotSpeedY;

                    // Evaluate player collision (sphere distance)
                    const distToPlayer = ship.position.distanceTo(obs.mesh.position);
                    if (distToPlayer < (obs.radius + 0.5)) {
                        // Impact!
                        playSound('hit');
                        shield -= 25;
                        document.getElementById('shield-val').innerText = shield + "%";
                        
                        if (shield <= 50) document.getElementById('shield-val').style.color = '#fbbf24';
                        if (shield <= 25) document.getElementById('shield-val').style.color = '#ef4444';

                        // Explode asteroid
                        scene.remove(obs.mesh);
                        obstacles.splice(idx, 1);

                        if (shield <= 0) {
                            endGame();
                        }
                        continue;
                    }

                    // Remove if passed behind ship
                    if (obs.mesh.position.z > 15) {
                        scene.remove(obs.mesh);
                        obstacles.splice(idx, 1);
                        score += 10;
                        document.getElementById('score-val').innerText = score;
                    }
                }

                // Process lasers
                for(let lIdx = lasers.length - 1; lIdx >= 0; lIdx--) {
                    const laser = lasers[lIdx];
                    laser.mesh.position.z -= 3.0; // flies fast down screen
                    
                    let hitDetected = false;

                    // Evaluate hit check with all active asteroids
                    for(let oIdx = obstacles.length - 1; oIdx >= 0; oIdx--) {
                        const obs = obstacles[oIdx];
                        const distToLaser = laser.mesh.position.distanceTo(obs.mesh.position);
                        
                        if (distToLaser < (obs.radius + 0.4)) {
                            // Target Down!
                            playSound('explode');
                            score += 50;
                            document.getElementById('score-val').innerText = score;

                            scene.remove(obs.mesh);
                            obstacles.splice(oIdx, 1);
                            
                            scene.remove(laser.mesh);
                            lasers.splice(lIdx, 1);
                            
                            hitDetected = true;
                            break;
                        }
                    }

                    if (hitDetected) continue;

                    // Clean out of bounds lasers
                    if (laser.mesh.position.z < -160) {
                        scene.remove(laser.mesh);
                        lasers.splice(lIdx, 1);
                    }
                }
            }

            renderer.render(scene, camera);
        }

        function endGame() {
            gameActive = false;
            playSound('explode');
            
            document.getElementById('menu-title').innerText = "MISSION COMPLETED";
            document.getElementById('menu-desc').innerHTML = `You crashed into the asteroid belt.<br><br><span style="font-size:1.6rem; color:#f472b6; font-weight:bold;">Final Score: ${score}</span>`;
            document.getElementById('menu-overlay').style.display = 'flex';
        }

        // Initialize WebGL engine window load
        window.onload = function() {
            initEngine();
            animate(0);
        }
    </script>
    """
    st.components.v1.html(html_game, height=480)

    from engines import database
    
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    col_submit, col_board = st.columns([1, 1])
    
    with col_submit:
        st.markdown("""
        <div class='glass-card' style='padding: 20px; border-radius: 12px;'>
            <h3 style='margin:0 0 10px 0; color:#f472b6;'>🏆 Log Mission Score</h3>
            <p style='color:#94a3b8; font-size:0.85rem; margin-bottom:15px;'>
                Log your final starship score to the local SQLite database!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("leaderboard_form", clear_on_submit=True):
            player_name = st.text_input("Pilot Codename", value="AETHER_PILOT", max_chars=20)
            logged_score = st.number_input("Arcade Score", min_value=0, step=10, value=0)
            
            submit_score = st.form_submit_button("LOG MISSION DATA")
            if submit_score:
                if player_name.strip() == "":
                    st.error("Please enter a valid codename!")
                else:
                    database.save_score(player_name.strip(), logged_score)
                    st.success(f"Logged score {logged_score} for {player_name.strip()}!")
                    st.rerun()

    with col_board:
        st.markdown("""
        <div class='glass-card' style='padding: 20px; border-radius: 12px;'>
            <h3 style='margin:0 0 15px 0; color:#818cf8;'>🌌 Top 10 Starship Pilots</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Load high scores
        leaderboard_data = database.get_leaderboard(limit=10)
        if leaderboard_data:
            rows_html = ""
            for rank, entry in enumerate(leaderboard_data):
                medal = "🥇" if rank == 0 else "🥈" if rank == 1 else "🥉" if rank == 2 else f"#{rank+1}"
                rows_html += f"""
                <tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>
                    <td style='padding:8px; font-weight:bold;'>{medal}</td>
                    <td style='padding:8px; font-family:monospace;'>{entry['player_name']}</td>
                    <td style='padding:8px; text-align:right; font-weight:bold; color:#f472b6;'>{entry['score']}</td>
                </tr>
                """
                
            table_html = f"""
            <table style='width:100%; border-collapse:collapse; color:#e2e8f0; font-size:0.9rem;'>
                <thead>
                    <tr style='border-bottom:1.5px solid rgba(255,255,255,0.1); text-align:left; color:#94a3b8;'>
                        <th style='padding:8px;'>Rank</th>
                        <th style='padding:8px;'>Pilot Name</th>
                        <th style='padding:8px; text-align:right;'>Score</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("Leaderboard is currently empty. Launch the first mission!")

