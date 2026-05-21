import streamlit as st
import requests
import urllib.parse
import re

def search_youtube_piped(query):
    # Public piped instances list for high reliability
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://piped-api.garudalinux.org",
        "https://pipedapi.colby.land"
    ]
    
    for base_url in instances:
        try:
            url = f"{base_url}/search?q={urllib.parse.quote(query)}&filter=videos"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                results = []
                for item in data.get("items", [])[:5]:
                    if "videoId" in item:
                        results.append({
                            "title": item.get("title", "Unknown Title"),
                            "id": item.get("videoId"),
                            "uploader": item.get("uploaderName", "Unknown Channel"),
                            "duration": item.get("duration", 0)
                        })
                if results:
                    return results
        except:
            continue
    return []

def fetch_lrclib_lyrics(artist, track):
    url = f"https://lrclib.net/api/get?artist_name={urllib.parse.quote(artist)}&track_name={urllib.parse.quote(track)}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    
    # Try search query if direct get fails
    try:
        search_url = f"https://lrclib.net/api/search?q={urllib.parse.quote(f'{artist} {track}')}"
        search_res = requests.get(search_url, timeout=5)
        if search_res.status_code == 200:
            tracks = search_res.json()
            if tracks:
                return tracks[0]
    except:
        pass
    return None

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🎤 YouTube Synced Lyrics Player</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Search any track to fetch its synchronized lyrics (.lrc). Play the YouTube video and watch the lyrics scroll automatically in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initial state initialization
    if "selected_video_id" not in st.session_state:
        st.session_state.selected_video_id = None
    if "active_lyrics" not in st.session_state:
        st.session_state.active_lyrics = None

    search_input = st.text_input("Enter Track Name & Artist (e.g., 'Blinding Lights The Weeknd')", value="Blinding Lights The Weeknd")
    
    col_btn, col_fallback = st.columns([2, 3])
    with col_btn:
        trigger_search = st.button("Search Track & Lyrics")
    with col_fallback:
        direct_yt_id = st.text_input("OR Paste YouTube Video ID (e.g. 'fHI8X4OXluQ')", "")
        if direct_yt_id:
            st.session_state.selected_video_id = direct_yt_id.strip()

    if trigger_search:
        with st.spinner("Fetching music metadata..."):
            # Clean up search queries
            cleaned_query = search_input.strip()
            
            # Fetch YouTube videos
            videos = search_youtube_piped(cleaned_query)
            
            # Fetch Lyrics
            # Try splitting search query by space/hyphen to guess artist/track
            parts = re.split(r'\s+-\s+|\s+by\s+|\s+', cleaned_query, maxsplit=1)
            artist = parts[0]
            track = parts[1] if len(parts) > 1 else cleaned_query
            
            lyrics_data = fetch_lrclib_lyrics(artist, track)
            
            if videos:
                st.session_state.videos_list = videos
                st.session_state.selected_video_id = videos[0]["id"]
            else:
                st.warning("YouTube search failed. Using fallback video query...")
                st.session_state.selected_video_id = None
                
            if lyrics_data:
                st.session_state.active_lyrics = lyrics_data
            else:
                st.session_state.active_lyrics = None
                st.warning("Could not find synchronized lyrics for this song on LRCLib database.")

    # Display video selection dropdown if search was run
    if "videos_list" in st.session_state and st.session_state.videos_list:
        v_options = {f"{v['title']} ({v['uploader']})": v['id'] for v in st.session_state.videos_list}
        selected_v_name = st.selectbox("Select matching YouTube Video", list(v_options.keys()))
        st.session_state.selected_video_id = v_options[selected_v_name]

    # Render YouTube + Lyrics iframe component
    if st.session_state.selected_video_id:
        video_id = st.session_state.selected_video_id
        
        # Determine lyrics payload
        synced_lyrics = ""
        plain_lyrics = ""
        track_title = "Unknown Song"
        artist_name = "Unknown Artist"
        
        if st.session_state.active_lyrics:
            synced_lyrics = st.session_state.active_lyrics.get("syncedLyrics", "")
            plain_lyrics = st.session_state.active_lyrics.get("plainLyrics", "")
            track_title = st.session_state.active_lyrics.get("name", "Unknown Title")
            artist_name = st.session_state.active_lyrics.get("artistName", "Unknown Artist")
            
        if not synced_lyrics and plain_lyrics:
            # Format plain lyrics to match synced structure
            synced_lyrics = "[00:00.00] (Plain Lyrics Mode - No Sync Timestamps Available)\n"
            for idx, line in enumerate(plain_lyrics.split("\n")):
                synced_lyrics += f"[00:{idx*4:02d}.00] {line}\n"
        elif not synced_lyrics:
            synced_lyrics = "[00:00.00] (No lyrics found on LRCLib database for this song.)\n[00:05.00] Try entering a more specific artist name in your search query."

        # Double check newlines escaping for JS embedding
        escaped_lyrics = synced_lyrics.replace("`", "'").replace("\n", "\\n")

        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.02); padding:10px 15px; border-radius:10px; margin-bottom:15px; border:1px solid rgba(255,255,255,0.05);'>
            <h3 style='margin:0; font-size:1.1rem; color:#818cf8;'>Now Playing: <span style='color:#fff;'>{track_title}</span> by <span style='color:#fff;'>{artist_name}</span></h3>
        </div>
        """, unsafe_allow_html=True)

        html_player = f"""
        <div id="player-lyrics-container" style="
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            max-width: 980px;
            margin: 0 auto;
            font-family: 'Inter', sans-serif;
            color: #f1f5f9;
        ">
            <!-- Left Side: YouTube Embed -->
            <div style="background:#000; border-radius:12px; overflow:hidden; aspect-ratio:16/9; border:1px solid rgba(255,255,255,0.08); box-shadow:0 10px 30px rgba(0,0,0,0.6);">
                <div id="yt-player" style="width:100%; height:100%;"></div>
            </div>

            <!-- Right Side: Synced Lyrics Viewport -->
            <div id="lyrics-viewport" style="
                background: rgba(10,12,22,0.9);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                height: 275px;
                overflow-y: scroll;
                padding: 20px;
                box-sizing: border-box;
                position: relative;
                scroll-behavior: smooth;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
            ">
                <div id="lyrics-lines-container" style="padding-top: 100px; padding-bottom: 100px; text-align: center;">
                    <!-- Filled by JS -->
                </div>
            </div>
        </div>

        <style>
            .lyric-line {{
                font-size: 1.1rem;
                font-family: 'Outfit', sans-serif;
                margin: 18px 0;
                color: rgba(255,255,255,0.4);
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .lyric-line.active-line {{
                color: #f472b6 !important;
                font-weight: 700;
                transform: scale(1.1);
                text-shadow: 0 0 8px rgba(244, 114, 182, 0.4);
            }}
            #lyrics-viewport::-webkit-scrollbar {{
                width: 6px;
            }}
            #lyrics-viewport::-webkit-scrollbar-thumb {{
                background: rgba(99, 102, 241, 0.3);
                border-radius: 3px;
            }}
        </style>

        <script>
            // Load YouTube Iframe API
            var tag = document.createElement('script');
            tag.src = "https://www.youtube.com/iframe_api";
            var firstScriptTag = document.getElementsByTagName('script')[0];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

            var player;
            var parsedLyrics = [];
            var currentLineIndex = -1;

            // Raw lyric text
            const rawLyrics = `{escaped_lyrics}`;

            // Parse LRC lyrics format
            function parseLRC(lrcText) {{
                const lines = lrcText.split('\\n');
                const timeRegex = /\\[(\\d+):(\\d+)\\.(\\d+)\\](.*)/;
                const lyrics = [];

                for (let line of lines) {{
                    const match = timeRegex.exec(line);
                    if (match) {{
                        const min = parseInt(match[1]);
                        const sec = parseInt(match[2]);
                        const ms = parseInt(match[3]);
                        const time = min * 60 + sec + ms / 100;
                        const text = match[4].trim();
                        lyrics.push({{ time: time, text: text }});
                    }}
                }}
                
                // Sort by time
                lyrics.sort((a, b) => a.time - b.time);
                return lyrics;
            }}

            // Render Lyrics elements
            function renderLyrics() {{
                parsedLyrics = parseLRC(rawLyrics);
                const container = document.getElementById('lyrics-lines-container');
                container.innerHTML = '';

                parsedLyrics.forEach((line, index) => {{
                    const el = document.createElement('div');
                    el.className = 'lyric-line';
                    el.id = 'line-' + index;
                    el.innerText = line.text || "•••";
                    el.onclick = () => {{
                        if (player && player.seekTo) {{
                            player.seekTo(line.time, true);
                        }}
                    }};
                    container.appendChild(el);
                }});
            }}

            // YT IFrame Callback
            function onYouTubeIframeAPIReady() {{
                player = new YT.Player('yt-player', {{
                    videoId: '{video_id}',
                    playerVars: {{
                        'playsinline': 1,
                        'autoplay': 0,
                        'controls': 1
                    }},
                    events: {{
                        'onReady': onPlayerReady,
                        'onStateChange': onPlayerStateChange
                    }}
                }});
            }}

            function onPlayerReady(event) {{
                // Start sync loops
                setInterval(syncLyrics, 100);
            }}

            function onPlayerStateChange(event) {{
                // Nothing special needed
            }}

            // Sync Lyrics highlighting and scroll alignment
            function syncLyrics() {{
                if (!player || typeof player.getCurrentTime !== 'function') return;
                
                const currentTime = player.getCurrentTime();
                let activeIndex = -1;

                // Find active line matching current playback time
                for (let i = 0; i < parsedLyrics.length; i++) {{
                    if (currentTime >= parsedLyrics[i].time) {{
                        activeIndex = i;
                    }} else {{
                        break;
                    }}
                }}

                if (activeIndex !== currentLineIndex && activeIndex !== -1) {{
                    // Update active lines class
                    if (currentLineIndex !== -1) {{
                        const prevEl = document.getElementById('line-' + currentLineIndex);
                        if (prevEl) prevEl.classList.remove('active-line');
                    }}
                    
                    const activeEl = document.getElementById('line-' + activeIndex);
                    if (activeEl) {{
                        activeEl.classList.add('active-line');
                        
                        // Scroll active line to center
                        const viewport = document.getElementById('lyrics-viewport');
                        const lineOffset = activeEl.offsetTop;
                        const containerHeight = viewport.offsetHeight;
                        
                        viewport.scrollTop = lineOffset - (containerHeight / 2) + 30;
                    }}
                    currentLineIndex = activeIndex;
                }}
            }}

            // Initialize rendering
            renderLyrics();
        </script>
        """
        
        st.components.v1.html(html_player, height=310)
    else:
        st.info("Enter a song search query above or paste a video ID to boot the YouTube player.")
