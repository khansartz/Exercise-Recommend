# pages/3_About.py

import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from PIL import Image
from streamlit_option_menu import option_menu
import time
import os

# --- PAGE CONFIG ---
st.set_page_config(layout="wide")

# --- CSS (Copy-paste dari Home.py) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display.swap');
        
        :root {
            /* Warna Gradasi Tema */
            --theme-blue: #6495ED; 
            --theme-purple: #9370DB; 
            --theme-pink: #FF69B4; 
            --theme-gradient: linear-gradient(to right, var(--theme-blue), var(--theme-purple), var(--theme-pink));

            /* Warna Krem Latar */
            --cream-bg-light: #FAF9F6;  /* Halaman */
            --cream-bg-dark: #F0EFEA;   /* Sidebar */
            --dark-text: #333333;       
            --hover-cream: #E0DFD9;     
            
            /* Warna Baru (Soft Purple Theme) */
            --soft-purple-bg: #E8E2F7;    /* Latar tombol aktif */
            --soft-purple-text: #5D3B9C; /* Teks tombol aktif */
            --soft-purple-hover: #D8CCF2;  
            --dark-purple-solid: #5D3B9C; /* Tombol logout */
            --dark-purple-hover: #4A2E7E; /* Hover tombol logout */
        }

        /* --- HALAMAN UTAMA & JUDUL GRADASI --- */
        .stApp {
            background: var(--cream-bg-light); 
        }
        .main .block-container { padding: 1rem 2rem; }

        .header-title {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 2.75rem;
            margin-bottom: 1rem;
            background: var(--theme-gradient);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-fill-color: transparent;
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: var(--cream-bg-dark); 
            border-right: 1px solid #DCDCDC; 
        }
        [data-testid="stSidebar"] .stSuccess {
             color: var(--dark-text); 
        }
        
        /* --- TULISAN "Menu Bar" (Lebih subtle) --- */
        [data-testid="stSidebar"] .option-menu-container h2 {
            color: #999; /* Lebih abu-abu/muda */
            font-size: 0.8rem; /* Lebih kecil */
            font-weight: 600;
            text-transform: uppercase;
            padding: 0 1.25rem;
            letter-spacing: 0.5px;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        /* --- STYLING NAVIGASI --- */
        [data-testid="stSidebar"] .nav-link {
            font-size: 1rem;
            color: #555 !important; 
            border-radius: 8px;
            margin: 4px 10px;
            padding: 10px 15px;
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .nav-link:hover {
            background-color: var(--hover-cream) !important; 
            color: #000 !important;
        }
        [data-testid="stSidebar"] .nav-link svg {
            font-size: 1.2rem;
            margin-right: 8px;
            color: #555; 
        }

        /* Item AKTIF (Soft Purple) */
        [data-testid="stSidebar"] .nav-link-selected {
            background-color: var(--soft-purple-bg) !important; 
            color: var(--soft-purple-text) !important;
            font-weight: 600;
            border-left: 4px solid var(--theme-purple); 
        }
        [data-testid="stSidebar"] .nav-link-selected:hover {
             background-color: var(--soft-purple-hover) !important;
             color: var(--soft-purple-text) !important;
        }
        [data-testid="stSidebar"] .nav-link-selected svg {
            color: var(--soft-purple-text) !important; 
        }

        /* --- LOGOUT BUTTON (FIXED) --- */
        [data-testid="stSidebar"] .stButton {
            position: absolute;
            bottom: 20px;
            width: 90%;
            margin: 0 5%;
        }
        [data-testid="stSidebar"] .stButton button {
            background: var(--dark-purple-solid); 
            color: white;
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
            
            /* --- INI FIX-NYA --- */
            height: 45px; /* Set tinggi manual */
            padding: 8px 0 !important; /* Paksa padding vertikal */
            line-height: 1.5; /* Jaga teks tetap di tengah */
        }
        [data-testid="stSidebar"] .stButton button:hover {
             background: var(--dark-purple-hover); 
             transform: translateY(-2px);
             box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)


# Dapatkan path ke folder root (satu level di atas folder 'pages')
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.yaml')

# --- AUTHENTICATOR (Buat Ulang Setiap Kali) ---
try:
    with open(CONFIG_PATH) as file: # Buka file pake path absolut
        config = yaml.load(file, Loader=yaml.SafeLoader)
except FileNotFoundError:
    st.error(f"FATAL ERROR: config.yaml tidak ditemukan di {CONFIG_PATH}. Harap login dari Halaman Utama.")
    st.stop()
except Exception as e:
    st.error(f"Error loading config: {e}")
    st.stop()

# Inisialisasi ulang authenticator di SETIAP rerun
# Ini adalah cara library-nya membaca cookie & me-refresh session state
authenticator = Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# --- FUNGSI SIDEBAR (Sekarang GAK PERLU argumen lagi) ---
def show_sidebar():
    with st.sidebar:
        try:
            # --- FIX PATH UNTUK LOGO ---
            LOGO_PATH = os.path.join(ROOT_DIR, 'logo.jpg') 
            logo = Image.open(LOGO_PATH)
            st.image(logo, width=100)
        except FileNotFoundError:
            st.sidebar.title("🏋️ Exercise App")

        # Cek status login (library sudah me-refresh-nya)
        if st.session_state.get("authentication_status"):
            st.success(f"Welcome, {st.session_state['name']} 👋")
            selected = option_menu(
                menu_title="Menu Bar",
                options=["Home", "Recommendation", "Profile", "About"],
                icons=["house-fill", "clipboard-data-fill", "person-fill", "info-circle-fill"],
                menu_icon="list-task",
                default_index=3, # <-- INDEX 1
                orientation="vertical",
                key="sidebar_menu"
            )
            # Panggil logout di object 'authenticator' yang baru
            authenticator.logout("Logout", "sidebar", key="logout_sidebar") 
            return selected
        else:
            st.info("Please login to access the menu.")
            return None

# Panggil sidebar (tanpa argumen)
selected_page = show_sidebar()


# --- KONTEN HALAMAN ABOUT ---

# --- KONTEN HALAMAN ABOUT (DIPERBARUI & BISA DIAKSES SEMUA USER) ---

st.markdown("<h1 class='header-title'>About This App</h1>", unsafe_allow_html=True)

# --- INTRO SECTION ---
st.markdown("""
<div style='font-size:17px; line-height:1.8;'>
    Halo! 👋 <br>
    Ini adalah <b>Exercise Recommendation App</b> — aplikasi yang dirancang buat bantu lo dapetin <b>rekomendasi olahraga</b> yang sesuai sama kebutuhan tubuh lo.  
    Kami percaya setiap orang punya ritme dan tujuan kebugarannya masing-masing 💪  
    Makanya, aplikasi ini dibikin buat bantu lo latihan lebih <b>cerdas, konsisten, dan efisien</b>.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- FEATURE GRID / VISI MISI ---
st.subheader("🎯 Apa Tujuan Kami?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💡 Simpel Tapi Powerful")
    st.write("Tampilan minimalis, hasil maksimal. Semua fitur dibuat biar user gak ribet tapi tetap dapet insight penting.")

with col2:
    st.markdown("### 🤖 Rekomendasi Cerdas")
    st.write("Model machine learning bantu nentuin latihan terbaik berdasarkan preferensi dan kondisi tiap pengguna.")

with col3:
    st.markdown("### 🧠 Edukatif & Motivasional")
    st.write("Bukan cuma rekomendasi — kami juga bantu lo paham kenapa latihan tertentu cocok buat lo.")

st.markdown("---")

# --- TECH STACK / DEVELOPMENT SECTION ---
st.subheader("🛠️ Dibangun Dengan")
st.markdown("""
<div style='
    background-color: var(--soft-purple-bg);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
'>
    <p style='font-size: 1.05rem; color: #333;'>
        🚀 <b>Streamlit</b> untuk antarmuka interaktif <br>
        🧠 <b>Python + Scikit-learn / TensorFlow</b> untuk sistem rekomendasi <br>
        🎨 <b>Custom CSS</b> buat nuansa UI yang lembut & clean <br>
        🔐 <b>streamlit-authenticator</b> buat sistem login & registrasi
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- TEAM / DEVELOPER SECTION ---
st.subheader("👨‍💻 Tentang Pengembang")
col1, col2 = st.columns([1, 3])

with col1:
    try:
        dev_img = Image.open(os.path.join(ROOT_DIR, "profile.jpg"))
        st.image(dev_img, width=180)
    except FileNotFoundError:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=180)

with col2:
    st.markdown("""
    <div style='font-size:16px; line-height:1.7;'>
        Hai! Aku <b>[NAMA LO]</b> — pengembang dari aplikasi ini.  
        Aku tertarik sama <b>data analysis</b> & <b>machine learning</b>, dan lewat project ini, 
        aku pengen nunjukin gimana teknologi bisa bantu gaya hidup sehat.  
        <br><br>
        Kalau lo punya ide atau saran buat ngembangin app ini, feel free buat reach out 🙌  
        <br><br>
        <a href='mailto:your.email@example.com' style='color: var(--soft-purple-text); font-weight:600;'>📩 your.email@example.com</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- FUN FACT / QUOTE SECTION ---
st.markdown("""
<div style="
    background: var(--theme-gradient);
    padding: 1.8rem;
    border-radius: 12px;
    text-align: center;
    color: white;
    font-size: 1.2rem;
    font-family: 'Poppins', sans-serif;
">
    “Consistency beats intensity — stay moving, stay growing.” 🌱
</div>
""", unsafe_allow_html=True)
