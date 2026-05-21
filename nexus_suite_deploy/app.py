import streamlit as st

# Configure page metadata and layout
st.set_page_config(
    page_title="NexusSuite: All-in-One API & Creative Playground",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium glassmorphic CSS theme injection
st.markdown("""
<style>
    /* Import premium typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700&display=swap');

    /* Global styling */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #05060b;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
        background-attachment: fixed;
        color: #f1f5f9;
    }
    
    h1, h2, h3, [data-testid="stHeader"] {
        font-family: 'Outfit', sans-serif;
        color: #f8fafc;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
    }
    
    /* Hide default Streamlit header bar decoration */
    [data-testid="stHeader"] {
        background-color: rgba(5, 6, 11, 0.8);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Sidebar Glassmorphism styling */
    [data-testid="stSidebar"] {
        background: rgba(8, 10, 20, 0.7);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 5px 0 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Glassmorphic card components */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        transition: all 0.3s ease-in-out;
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }

    /* Glow highlights */
    .neon-text-indigo {
        color: #818cf8;
        text-shadow: 0 0 8px rgba(129, 140, 248, 0.5);
        font-family: 'Outfit', sans-serif;
    }
    .neon-text-pink {
        color: #f472b6;
        text-shadow: 0 0 8px rgba(244, 114, 182, 0.5);
        font-family: 'Outfit', sans-serif;
    }
    
    /* Styled buttons */
    .stButton>button {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(236, 72, 153, 0.8) 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.25s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.5) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
    
    .stButton>button:active {
        transform: translateY(1px) !important;
    }

    /* Input elements style override */
    input, textarea, select, div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }
    
    input:focus, textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 8px rgba(129, 140, 248, 0.4) !important;
    }

    /* Style blockquotes/alerts */
    div.stAlert {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px;
        color: #e2e8f0;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.4);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(236, 72, 153, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# Import module pages
from engines import (
    chatbot, image_gen, video_gen, sound_gen, lyrics_player,
    design_sandbox, humaniser, qr_generator, bg_remover,
    cv_maker, profile_stats, file_viewer, game_three, picture_editor,
    database
)

# Initialize local SQLite DB
database.init_db()

# Application Engine Catalog
ENGINES = {
    "🌌 AI Chatbot Assistant": chatbot,
    "🖼️ HD Image Generator": image_gen,
    "🎬 Cinematic Storyboard Video": video_gen,
    "🎵 Interactive Sound Synth": sound_gen,
    "🎤 YouTube Synced Lyrics": lyrics_player,
    "💻 HTML/CSS Design Sandbox": design_sandbox,
    "🧬 Text Humaniser": humaniser,
    "🎯 Custom QR Generator": qr_generator,
    "✂️ Background Remover": bg_remover,
    "📝 Pro CV & Profile Builder": cv_maker,
    "📊 LeetCode & Codeforces Hub": profile_stats,
    "📂 Universal Files Inspector": file_viewer,
    "🎮 3D Three.js Arcade Game": game_three,
    "🖌️ AI Photo Studio Canvas": picture_editor
}

# Sidebar dashboard branding
st.sidebar.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 2.2rem; margin-bottom: 5px; background: linear-gradient(135deg, #a5b4fc, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>NEXUS SUITE</h1>
    <p style='color: #94a3b8; font-size: 0.85rem; letter-spacing: 2px;'>ALL-IN-ONE API PORTAL</p>
    <div style='height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent); margin-top: 15px;'></div>
</div>
""", unsafe_allow_html=True)

# Search utility for engines
search_query = st.sidebar.text_input("🔍 Search Engines...", "").strip().lower()

# Filter active engines lists based on search
if search_query:
    filtered_engines = {k: v for k, v in ENGINES.items() if search_query in k.lower()}
    if not filtered_engines:
        st.sidebar.warning("No matches found!")
        filtered_engines = ENGINES
else:
    filtered_engines = ENGINES

# Selectbox navigation
selected_engine_name = st.sidebar.radio(
    "CHOOSE ENGINE", 
    options=list(filtered_engines.keys()),
    label_visibility="collapsed"
)

# Display sidebar info footer
st.sidebar.markdown("""
<div style='margin-top: 40px; padding: 15px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; font-size: 0.8rem; color: #64748b;'>
    <p style='margin: 0;'>⚙️ Version 1.0.0 (Streamlit Cloud)</p>
    <p style='margin: 3px 0 0 0;'>🔑 100% Free & Keyless APIs Only</p>
    <p style='margin: 3px 0 0 0;'>💻 Procedural HTML5 Elements</p>
</div>
""", unsafe_allow_html=True)

# Dispatch execution to selected engine
active_module = ENGINES[selected_engine_name]

# Main view container wrap
try:
    active_module.render()
except Exception as e:
    st.error(f"Engine Exception: {str(e)}")
    st.info("Check connections or API endpoints. This may be due to temporary network timeouts.")
