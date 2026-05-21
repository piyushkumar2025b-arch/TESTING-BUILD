import streamlit as st
import requests
import datetime

# Helper to fetch Codeforces User info
def fetch_cf_user(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    try:
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "OK" and len(data.get("result", [])) > 0:
                return data["result"][0]
    except:
        pass
    return None

# Helper to fetch Codeforces Rating Changes
def fetch_cf_ratings(handle):
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    try:
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "OK":
                return data["result"]
    except:
        pass
    return []

# Helper to fetch LeetCode Stats
def fetch_leetcode_stats(username):
    # Try multiple public proxies for high availability
    urls = [
        f"https://alfa-leetcode-api.onrender.com/{username}",
        f"https://leetcode-api-faisalshohag.vercel.app/{username}"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=7)
            if res.status_code == 200:
                data = res.json()
                # Check different API shapes returned by the proxies
                if "totalSolved" in data or "matchedUser" in data or "ranking" in data:
                    return data
        except:
            continue
    return None

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>📊 Competitive Programming Stats Hub</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Track live ratings, rankings, and solved problems directly from Codeforces and LeetCode APIs. No pre-saved data, fetches in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_cf, tab_lc = st.tabs(["Codeforces Tracker", "LeetCode Tracker"])

    # Codeforces Section
    with tab_cf:
        st.markdown("### Codeforces Handle Search")
        cf_handle = st.text_input("Enter Codeforces Handle", "tourist")
        
        if st.button("Fetch Codeforces Stats"):
            with st.spinner(f"Contacting Codeforces API for '{cf_handle}'..."):
                user_info = fetch_cf_user(cf_handle)
                ratings = fetch_cf_ratings(cf_handle)
                
                if user_info:
                    # Renders beautiful glass card with stats
                    rank = user_info.get("rank", "unrated").capitalize()
                    max_rank = user_info.get("maxRank", "unrated").capitalize()
                    rating = user_info.get("rating", 0)
                    max_rating = user_info.get("maxRating", 0)
                    contrib = user_info.get("contribution", 0)
                    org = user_info.get("organization", "No Organization")
                    avatar = user_info.get("titlePhoto", "https://codeforces.org/s/80518/images/codeforces-logo-with-telegram.png")

                    # Rank color coding mapping
                    rank_colors = {
                        "newbie": "#808080", "pupil": "#008000", "specialist": "#03a89e",
                        "expert": "#0000ff", "candidate master": "#aa00aa", "master": "#ff8c00",
                        "international master": "#ff8c00", "grandmaster": "#ff0000",
                        "international grandmaster": "#ff0000", "legendary grandmaster": "#ff0000"
                    }
                    user_rank_lower = user_info.get("rank", "newbie").lower()
                    color_hex = rank_colors.get(user_rank_lower, "#818cf8")

                    col_prof, col_info = st.columns([1, 3])
                    
                    with col_prof:
                        st.markdown(f"""
                        <div style='text-align:center; padding:15px; background:rgba(255,255,255,0.02); border-radius:12px; border:1px solid rgba(255,255,255,0.05);'>
                            <img src='{avatar}' style='width:120px; border-radius:50%; border:3px solid {color_hex}; box-shadow:0 0 15px {color_hex}40;' />
                            <h4 style='margin:10px 0 2px 0; color:#fff;'>{cf_handle}</h4>
                            <span style='color:{color_hex}; font-weight:bold; font-size:0.9rem;'>{rank}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col_info:
                        st.markdown(f"""
                        <div class='glass-card' style='margin:0;'>
                            <div style='display:grid; grid-template-columns:1fr 1fr; gap:15px;'>
                                <div>
                                    <p style='color:#94a3b8; margin:0; font-size:0.85rem;'>Current Rating</p>
                                    <h3 style='margin:5px 0 0 0; color:{color_hex}; font-size:1.8rem;'>{rating}</h3>
                                </div>
                                <div>
                                    <p style='color:#94a3b8; margin:0; font-size:0.85rem;'>Max Rating</p>
                                    <h3 style='margin:5px 0 0 0; color:#fff; font-size:1.8rem;'>{max_rating} <span style='font-size:0.85rem; color:#94a3b8;'>({max_rank})</span></h3>
                                </div>
                                <div>
                                    <p style='color:#94a3b8; margin:0; font-size:0.85rem;'>Contribution</p>
                                    <h3 style='margin:5px 0 0 0; color:#10b981; font-size:1.5rem;'>{contrib:+}</h3>
                                </div>
                                <div>
                                    <p style='color:#94a3b8; margin:0; font-size:0.85rem;'>Organization</p>
                                    <h4 style='margin:5px 0 0 0; color:#fff;'>{org}</h4>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Draw rating progress SVG Chart
                    if ratings:
                        st.markdown("### 📈 Rating Progress Chart")
                        
                        # Generate SVG Line Chart path points
                        min_y = min([x.get("newRating", 0) for x in ratings])
                        max_y = max([x.get("newRating", 0) for x in ratings])
                        y_range = max_y - min_y if max_y != min_y else 1
                        
                        points_count = len(ratings)
                        width = 800
                        height = 200
                        margin = 25
                        
                        svg_points = ""
                        for idx, change in enumerate(ratings):
                            val = change.get("newRating", 0)
                            cx = margin + (idx / (points_count - 1 if points_count > 1 else 1)) * (width - 2 * margin)
                            cy = (height - margin) - ((val - min_y) / y_range) * (height - 2 * margin)
                            svg_points += f"{cx},{cy} "
                            
                        chart_html = f"""
                        <div style='background:rgba(8,10,20,0.6); padding:15px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); margin-top:10px;'>
                            <svg viewBox="0 0 {width} {height}" style="width:100%; height:auto;">
                                <!-- Grid Lines -->
                                <line x1="{margin}" y1="{margin}" x2="{width-margin}" y2="{margin}" stroke="rgba(255,255,255,0.03)" />
                                <line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="rgba(255,255,255,0.1)" />
                                
                                <!-- Rating Line -->
                                <polyline fill="none" stroke="url(#line-glow)" stroke-width="3" points="{svg_points}" />
                                
                                <!-- Glow Definition -->
                                <defs>
                                    <linearGradient id="line-glow" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#818cf8" />
                                        <stop offset="100%" stop-color="#f472b6" />
                                    </linearGradient>
                                </defs>
                            </svg>
                            <div style='display:flex; justify-content:space-between; color:#64748b; font-size:0.75rem; margin-top:5px; padding:0 10px;'>
                                <span>First Contest ({ratings[0].get('contestId')})</span>
                                <span>Total Contests: {points_count}</span>
                                <span>Latest Rating ({ratings[-1].get('newRating')})</span>
                            </div>
                        </div>
                        """
                        st.components.v1.html(chart_html, height=225)
                    else:
                        st.info("No contest ratings found for this user.")
                else:
                    st.error("Handle not found or Codeforces API failed to resolve user handles.")

    # LeetCode Section
    with tab_lc:
        st.markdown("### LeetCode Username Search")
        lc_username = st.text_input("Enter LeetCode Username", "faisalshohag")
        
        if st.button("Fetch LeetCode Stats"):
            with st.spinner(f"Querying LeetCode API scraper for '{lc_username}'..."):
                lc_data = fetch_leetcode_stats(lc_username)
                
                if lc_data:
                    # Normalize JSON paths because proxy responses vary
                    solved = lc_data.get("totalSolved", lc_data.get("solvedProblems", 0))
                    total_q = lc_data.get("totalQuestions", 3200)
                    ranking = lc_data.get("ranking", lc_data.get("rank", "N/A"))
                    
                    easy = lc_data.get("easySolved", 0)
                    med = lc_data.get("mediumSolved", 0)
                    hard = lc_data.get("hardSolved", 0)
                    
                    total_easy = lc_data.get("totalEasy", 800)
                    total_med = lc_data.get("totalMedium", 1600)
                    total_hard = lc_data.get("totalHard", 800)

                    # Solve ratio calculations
                    ratio = (solved / total_q) * 100 if total_q > 0 else 0
                    
                    col_stats, col_ring = st.columns([2, 1])
                    
                    with col_stats:
                        st.markdown(f"""
                        <div class='glass-card' style='margin:0;'>
                            <h4 style='margin:0 0 15px 0; color:#fff;'>📊 Account Metrics: {lc_username}</h4>
                            <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:15px;'>
                                <div>
                                    <p style='color:#94a3b8; margin:0; font-size:0.8rem;'>Global Rank</p>
                                    <h4 style='margin:4px 0 0 0; color:#818cf8;'>{ranking:, if isinstance(ranking, int) else ranking}</h4>
                                </div>
                                <div>
                                    <p style='color:#94a3b8; margin:0; font-size:0.8rem;'>Solved Problems</p>
                                    <h4 style='margin:4px 0 0 0; color:#fff;'>{solved} / {total_q}</h4>
                                </div>
                            </div>
                            
                            <!-- Easy, Med, Hard breakdowns -->
                            <div style='margin-bottom:8px;'>
                                <div style='display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;'>
                                    <span style='color:#10b981; font-weight:600;'>Easy</span><span>{easy}/{total_easy}</span>
                                </div>
                                <div style='background:rgba(255,255,255,0.05); height:6px; border-radius:3px;'>
                                    <div style='background:#10b981; height:100%; border-radius:3px; width:{ (easy/total_easy)*100 if total_easy>0 else 0 }%;'></div>
                                </div>
                            </div>
                            
                            <div style='margin-bottom:8px;'>
                                <div style='display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;'>
                                    <span style='color:#fbbf24; font-weight:600;'>Medium</span><span>{med}/{total_med}</span>
                                </div>
                                <div style='background:rgba(255,255,255,0.05); height:6px; border-radius:3px;'>
                                    <div style='background:#fbbf24; height:100%; border-radius:3px; width:{ (med/total_med)*100 if total_med>0 else 0 }%;'></div>
                                </div>
                            </div>
                            
                            <div>
                                <div style='display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;'>
                                    <span style='color:#ef4444; font-weight:600;'>Hard</span><span>{hard}/{total_hard}</span>
                                </div>
                                <div style='background:rgba(255,255,255,0.05); height:6px; border-radius:3px;'>
                                    <div style='background:#ef4444; height:100%; border-radius:3px; width:{ (hard/total_hard)*100 if total_hard>0 else 0 }%;'></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col_ring:
                        # Renders dynamic SVG circular progress ring
                        dash_array = 2 * 3.14159 * 70 # Circumference
                        dash_offset = dash_array - (dash_array * ratio / 100)
                        
                        ring_html = f"""
                        <div style='display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; padding:15px; background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.05); border-radius:12px;'>
                            <svg viewBox="0 0 160 160" style="width:130px; height:130px;">
                                <!-- Inner bg ring -->
                                <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="8" />
                                
                                <!-- Progress ring -->
                                <circle cx="80" cy="80" r="70" fill="none" stroke="url(#progress-gradient)" stroke-width="8" 
                                    stroke-dasharray="{dash_array}" stroke-dashoffset="{dash_offset}" stroke-linecap="round" transform="rotate(-90 80 80)" />
                                
                                <!-- Centered stats text -->
                                <text x="50%" y="45%" text-anchor="middle" dominant-baseline="middle" fill="#fff" font-family="'Outfit', sans-serif;" font-weight="bold" font-size="1.4rem">{solved}</text>
                                <text x="50%" y="65%" text-anchor="middle" dominant-baseline="middle" fill="#64748b" font-family="'Inter', sans-serif;" font-size="0.75rem">Solved ({ratio:.1f}%)</text>
                                
                                <defs>
                                    <linearGradient id="progress-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stop-color="#818cf8" />
                                        <stop offset="100%" stop-color="#fbbf24" />
                                    </linearGradient>
                                </defs>
                            </svg>
                        </div>
                        """
                        st.components.v1.html(ring_html, height=180)
                else:
                    st.error("User stats not found. Make sure the Leetcode username is correct or try again shortly (proxies can sometimes be rate-limited).")
