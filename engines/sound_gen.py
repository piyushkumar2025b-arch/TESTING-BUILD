import streamlit as st

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🎵 Interactive Sound Synth & SFX Forge</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Compose synth tracks and generate retro sound effects (SFX) in real-time. Record and export your sounds as WAV files.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Embed the entire Web Audio Synthesizer in a custom component
    html_synth = """
    <div id="synth-container" style="
        font-family: 'Outfit', sans-serif;
        background: rgba(13, 16, 28, 0.95);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 25px;
        color: #f1f5f9;
        max-width: 900px;
        margin: 0 auto;
        box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    ">
        <!-- SFX Presets Panel -->
        <h3 style="margin-top:0; color:#818cf8; font-size:1.3rem;">⚡ RETRO SFX PRESETS</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: 25px;">
            <button onclick="playPreset('laser')" class="synth-btn sfx-btn" style="background:#ef4444;">💥 Laser</button>
            <button onclick="playPreset('coin')" class="synth-btn sfx-btn" style="background:#fbbf24; color:#000;">🪙 Coin</button>
            <button onclick="playPreset('jump')" class="synth-btn sfx-btn" style="background:#10b981;">🦘 Jump</button>
            <button onclick="playPreset('explosion')" class="synth-btn sfx-btn" style="background:#f97316;">🔥 Explosion</button>
            <button onclick="playPreset('powerup')" class="synth-btn sfx-btn" style="background:#8b5cf6;">⭐ Power-Up</button>
        </div>

        <!-- Custom Synth Parameters -->
        <h3 style="color:#f472b6; font-size:1.3rem; margin-top:20px;">🎛️ CUSTOM SYNTH ENGINE</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
            <!-- Waveform & Filter -->
            <div class="control-box" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:15px; border-radius:10px;">
                <label style="display:block; margin-bottom:12px; font-weight:600;">Oscillator Waveform</label>
                <div style="display:flex; gap:8px; margin-bottom:18px;">
                    <button onclick="setWaveform('sine')" id="wave-sine" class="wave-toggle active-wave">Sine</button>
                    <button onclick="setWaveform('square')" id="wave-square" class="wave-toggle">Square</button>
                    <button onclick="setWaveform('triangle')" id="wave-triangle" class="wave-toggle">Triangle</button>
                    <button onclick="setWaveform('sawtooth')" id="wave-sawtooth" class="wave-toggle">Sawtooth</button>
                </div>

                <label style="display:block; margin-bottom:5px; font-weight:600;">Lowpass Filter Cutoff</label>
                <input type="range" id="filter-cutoff" min="100" max="8000" value="2500" style="width:100%; accent-color:#818cf8;">
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#94a3b8; margin-top:3px;">
                    <span>100 Hz</span><span id="cutoff-val">2500 Hz</span><span>8 kHz</span>
                </div>
            </div>

            <!-- ADSR Envelope -->
            <div class="control-box" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:15px; border-radius:10px;">
                <label style="display:block; margin-bottom:10px; font-weight:600;">ADSR Envelope</label>
                
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                        <span>Attack (Rise time)</span><span id="attack-val">0.05s</span>
                    </div>
                    <input type="range" id="adsr-a" min="0.01" max="1" step="0.01" value="0.05" style="width:100%; accent-color:#f472b6;">
                </div>

                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                        <span>Decay (Fall time)</span><span id="decay-val">0.2s</span>
                    </div>
                    <input type="range" id="adsr-d" min="0.01" max="1" step="0.01" value="0.2" style="width:100%; accent-color:#f472b6;">
                </div>

                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                        <span>Sustain (Hold level)</span><span id="sustain-val">60%</span>
                    </div>
                    <input type="range" id="adsr-s" min="0" max="100" step="1" value="60" style="width:100%; accent-color:#f472b6;">
                </div>

                <div>
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                        <span>Release (Fade out)</span><span id="release-val">0.3s</span>
                    </div>
                    <input type="range" id="adsr-r" min="0.01" max="2" step="0.01" value="0.3" style="width:100%; accent-color:#f472b6;">
                </div>
            </div>
        </div>

        <!-- Recording section -->
        <div style="display:flex; align-items:center; justify-content:space-between; padding:12px 20px; background:rgba(99,102,241,0.08); border:1px dashed rgba(99,102,241,0.3); border-radius:10px; margin-bottom:25px;">
            <div>
                <span id="record-status" style="font-weight:600; color:#94a3b8;">🔴 RECORDER IDLE</span>
                <span id="record-timer" style="margin-left:15px; font-family:monospace; color:#818cf8;">00.00s</span>
            </div>
            <div style="display:flex; gap:10px;">
                <button onclick="startRecording()" id="rec-start" class="synth-btn" style="background:#dc2626; color:white; padding:5px 12px; font-size:0.9rem;">Record</button>
                <button onclick="stopRecording()" id="rec-stop" class="synth-btn" disabled style="background:rgba(255,255,255,0.1); color:#475569; padding:5px 12px; font-size:0.9rem; cursor:not-allowed;">Stop & Download</button>
            </div>
        </div>

        <!-- 1 Octave Keyboard -->
        <div class="keyboard" style="display:flex; justify-content:center; position:relative; background:#111; padding:15px; border-radius:12px; box-shadow:inset 0 0 10px rgba(0,0,0,0.8); height:200px;">
            <!-- White Keys -->
            <div onclick="playKey(261.63, 'c4')" id="key-c4" class="key white-key"><span>C</span></div>
            <div onclick="playKey(293.66, 'd4')" id="key-d4" class="key white-key"><span>D</span></div>
            <div onclick="playKey(329.63, 'e4')" id="key-e4" class="key white-key"><span>E</span></div>
            <div onclick="playKey(349.23, 'f4')" id="key-f4" class="key white-key"><span>F</span></div>
            <div onclick="playKey(392.00, 'g4')" id="key-g4" class="key white-key"><span>G</span></div>
            <div onclick="playKey(440.00, 'a4')" id="key-a4" class="key white-key"><span>A</span></div>
            <div onclick="playKey(493.88, 'b4')" id="key-b4" class="key white-key"><span>B</span></div>
            <div onclick="playKey(523.25, 'c5')" id="key-c5" class="key white-key"><span>C</span></div>
            
            <!-- Black Keys -->
            <div onclick="playKey(277.18, 'cs4')" id="key-cs4" class="key black-key" style="left: calc(50% - 150px);"><span>C#</span></div>
            <div onclick="playKey(311.13, 'ds4')" id="key-ds4" class="key black-key" style="left: calc(50% - 100px);"><span>D#</span></div>
            <div onclick="playKey(369.99, 'fs4')" id="key-fs4" class="key black-key" style="left: calc(50% - 0px);"><span>F#</span></div>
            <div onclick="playKey(415.30, 'gs4')" id="key-gs4" class="key black-key" style="left: calc(50% + 50px);"><span>G#</span></div>
            <div onclick="playKey(466.16, 'as4')" id="key-as4" class="key black-key" style="left: calc(50% + 100px);"><span>A#</span></div>
        </div>
    </div>

    <style>
        .synth-btn {
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .synth-btn:hover {
            transform: translateY(-2px);
            filter: brightness(1.1);
        }
        .synth-btn:active {
            transform: translateY(1px);
        }
        .sfx-btn {
            font-size: 1.1rem;
            padding: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .wave-toggle {
            flex: 1;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            color: #94a3b8;
            padding: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .wave-toggle:hover {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .active-wave {
            background: rgba(99, 102, 241, 0.2) !important;
            border-color: #818cf8 !important;
            color: #818cf8 !important;
            font-weight: 600;
        }
        .key {
            cursor: pointer;
            user-select: none;
            position: relative;
            transition: background 0.1s, transform 0.1s;
        }
        .white-key {
            width: 48px;
            height: 100%;
            background: #f8fafc;
            border: 1px solid #1e293b;
            border-radius: 0 0 6px 6px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            padding-bottom: 10px;
            color: #334155;
            font-weight: 600;
            margin: 0 2px;
            z-index: 1;
        }
        .white-key:hover {
            background: #f1f5f9;
        }
        .white-key:active, .white-key.active-key {
            background: #cbd5e1;
            transform: scaleY(0.98);
        }
        .black-key {
            width: 28px;
            height: 60%;
            background: #0f172a;
            border: 1px solid #000;
            border-radius: 0 0 4px 4px;
            position: absolute;
            z-index: 2;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            padding-bottom: 5px;
            color: #94a3b8;
            font-size: 0.75rem;
            margin: 0;
        }
        .black-key:hover {
            background: #1e293b;
        }
        .black-key:active, .black-key.active-key {
            background: #475569;
            transform: scaleY(0.97);
        }
    </style>

    <script>
        let audioCtx = null;
        let activeWaveform = 'sine';
        let isRecording = false;
        let recordStartTime = 0;
        let recordInterval = null;
        let audioChunks = [];
        let mediaRecorder = null;
        let destStreamNode = null;

        // Init Audio Context
        function getAudioContext() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            return audioCtx;
        }

        // Set active waveform UI
        function setWaveform(wave) {
            activeWaveform = wave;
            document.querySelectorAll('.wave-toggle').forEach(el => el.classList.remove('active-wave'));
            document.getElementById('wave-' + wave).classList.add('active-wave');
        }

        // Event listeners to update slider value previews
        document.getElementById('filter-cutoff').oninput = function() {
            document.getElementById('cutoff-val').innerText = this.value + " Hz";
        }
        document.getElementById('adsr-a').oninput = function() {
            document.getElementById('attack-val').innerText = this.value + "s";
        }
        document.getElementById('adsr-d').oninput = function() {
            document.getElementById('decay-val').innerText = this.value + "s";
        }
        document.getElementById('adsr-s').oninput = function() {
            document.getElementById('sustain-val').innerText = this.value + "%";
        }
        document.getElementById('adsr-r').oninput = function() {
            document.getElementById('release-val').innerText = this.value + "s";
        }

        // Setup Stream node for recording
        function setupRecordStream() {
            const ctx = getAudioContext();
            if (!destStreamNode) {
                destStreamNode = ctx.createMediaStreamAudioDestinationNode();
                // We'll wrap all output to connect to BOTH destination (speakers) and destStreamNode (recorder)
            }
        }

        // Play Custom Keyboard Key
        function playKey(frequency, keyId) {
            const ctx = getAudioContext();
            setupRecordStream();
            
            // Visual key press animation
            const keyEl = document.getElementById('key-' + keyId);
            if (keyEl) {
                keyEl.classList.add('active-key');
                setTimeout(() => keyEl.classList.remove('active-key'), 200);
            }

            // Read ADSR parameters
            const attack = parseFloat(document.getElementById('adsr-a').value);
            const decay = parseFloat(document.getElementById('adsr-d').value);
            const sustain = parseFloat(document.getElementById('adsr-s').value) / 100;
            const release = parseFloat(document.getElementById('adsr-r').value);
            const cutoff = parseFloat(document.getElementById('filter-cutoff').value);

            // Synth nodes
            const osc = ctx.createOscillator();
            const filter = ctx.createBiquadFilter();
            const gainNode = ctx.createGain();

            osc.type = activeWaveform;
            osc.frequency.setValueAtTime(frequency, ctx.currentTime);

            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(cutoff, ctx.currentTime);

            // Configure ADSR
            const now = ctx.currentTime;
            gainNode.gain.setValueAtTime(0, now);
            gainNode.gain.linearRampToValueAtTime(0.25, now + attack); // Attack
            gainNode.gain.setValueAtTime(0.25, now + attack);
            gainNode.gain.exponentialRampToValueAtTime(Math.max(sustain * 0.25, 0.001), now + attack + decay); // Decay -> Sustain

            // Wire connections
            osc.connect(filter);
            filter.connect(gainNode);
            gainNode.connect(ctx.destination); // output to speaker
            gainNode.connect(destStreamNode);  // output to recorder

            osc.start(now);
            
            // Release timing
            const noteDuration = attack + decay + 0.15; // default note press hold length
            const releaseStart = now + noteDuration;
            gainNode.gain.setValueAtTime(sustain * 0.25, releaseStart);
            gainNode.gain.exponentialRampToValueAtTime(0.0001, releaseStart + release); // Release

            osc.stop(releaseStart + release);
        }

        // Play SFX Presets
        function playPreset(type) {
            const ctx = getAudioContext();
            setupRecordStream();
            const now = ctx.currentTime;

            const osc = ctx.createOscillator();
            const osc2 = ctx.createOscillator(); // for composite sounds like coin
            const gain = ctx.createGain();
            const filter = ctx.createBiquadFilter();

            osc.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);
            gain.connect(destStreamNode);

            if (type === 'laser') {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(880, now);
                osc.frequency.exponentialRampToValueAtTime(80, now + 0.25);

                filter.type = 'lowpass';
                filter.frequency.setValueAtTime(2000, now);

                gain.gain.setValueAtTime(0.2, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

                osc.start(now);
                osc.stop(now + 0.26);
            }
            else if (type === 'coin') {
                // Classic ascending tone (e.g. B4 -> E5)
                osc.type = 'square';
                osc.frequency.setValueAtTime(987.77, now); // B5
                osc.frequency.setValueAtTime(1318.51, now + 0.08); // E6

                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

                osc.start(now);
                osc.stop(now + 0.46);
            }
            else if (type === 'jump') {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(150, now);
                osc.frequency.exponentialRampToValueAtTime(650, now + 0.18);

                gain.gain.setValueAtTime(0.2, now);
                gain.gain.linearRampToValueAtTime(0, now + 0.18);

                osc.start(now);
                osc.stop(now + 0.19);
            }
            else if (type === 'explosion') {
                // White noise simulation using random nodes
                const bufferSize = ctx.sampleRate * 0.5; // 0.5s explosion
                const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                const data = buffer.getChannelData(0);
                for (let i = 0; i < bufferSize; i++) {
                    data[i] = Math.random() * 2 - 1;
                }

                const noiseNode = ctx.createBufferSource();
                noiseNode.buffer = buffer;

                filter.type = 'bandpass';
                filter.frequency.setValueAtTime(1000, now);
                filter.frequency.exponentialRampToValueAtTime(80, now + 0.4);

                gain.gain.setValueAtTime(0.25, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);

                noiseNode.connect(filter);
                noiseNode.start(now);
                noiseNode.stop(now + 0.5);
            }
            else if (type === 'powerup') {
                osc.type = 'sine';
                const arpeggio = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50]; // C Major Chord sweep
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);

                arpeggio.forEach((freq, idx) => {
                    const stepTime = now + (idx * 0.07);
                    osc.frequency.setValueAtTime(freq, stepTime);
                });

                osc.start(now);
                osc.stop(now + 0.6);
            }
        }

        // Recorder APIs
        function startRecording() {
            const ctx = getAudioContext();
            setupRecordStream();

            audioChunks = [];
            try {
                mediaRecorder = new MediaRecorder(destStreamNode.stream);
                mediaRecorder.ondataavailable = function(e) {
                    if (e.data.size > 0) {
                        audioChunks.push(e.data);
                    }
                };

                mediaRecorder.onstop = function() {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    // Auto-trigger download file
                    const a = document.createElement('a');
                    a.href = audioUrl;
                    a.download = 'nexus_synth_creation.wav';
                    a.click();
                };

                mediaRecorder.start();
                isRecording = true;
                recordStartTime = Date.now();
                
                document.getElementById('rec-start').disabled = true;
                document.getElementById('rec-start').style.background = "#475569";
                document.getElementById('rec-start').style.cursor = "not-allowed";
                
                document.getElementById('rec-stop').disabled = false;
                document.getElementById('rec-stop').style.background = "#10b981";
                document.getElementById('rec-stop').style.color = "white";
                document.getElementById('rec-stop').style.cursor = "pointer";

                document.getElementById('record-status').innerText = "🟢 RECORDING LIVE...";
                document.getElementById('record-status').style.color = "#dc2626";

                recordInterval = setInterval(() => {
                    const elapsed = (Date.now() - recordStartTime) / 1000;
                    document.getElementById('record-timer').innerText = elapsed.toFixed(2) + "s";
                }, 50);

            } catch (e) {
                alert("MediaRecorder not supported on this browser context. Try Chrome/Firefox.");
            }
        }

        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                clearInterval(recordInterval);

                document.getElementById('rec-start').disabled = false;
                document.getElementById('rec-start').style.background = "#dc2626";
                document.getElementById('rec-start').style.cursor = "pointer";

                document.getElementById('rec-stop').disabled = true;
                document.getElementById('rec-stop').style.background = "rgba(255,255,255,0.1)";
                document.getElementById('rec-stop').style.color = "#475569";
                document.getElementById('rec-stop').style.cursor = "not-allowed";

                document.getElementById('record-status').innerText = "🔴 RECORDER IDLE";
                document.getElementById('record-status').style.color = "#94a3b8";
                document.getElementById('record-timer').innerText = "00.00s";
            }
        }
    </script>
    """
    st.components.v1.html(html_synth, height=580)
