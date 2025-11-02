# home.py

import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from PIL import Image
from streamlit_option_menu import option_menu
import time
import streamlit as st
from navigation import make_sidebar

# --- PAGE CONFIG (WAJIB PALING ATAS) ---
st.set_page_config(
    page_title="Personal Fitness Guide",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
     # Bikin sidebar kebuka by default
)

# Simpan nama halaman ke session (buat tracking)
st.session_state["_current_page"] = "home"  # Ganti sesuai nama file halamannya



# --- CSS STYLING ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        
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

        /* --- HALAMAN UTAMA & JUDUL GRADASI --- 
         .stApp {
             background: var(--cream-bg-light); 
         }
         .main .block-container { padding: 1rem 2rem; }*/

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
           /* background-color: var(--cream-bg-dark);*/ 
            border-right: 1px solid #DCDCDC; 
        }
            
        [data-testid="stSidebarNav"] {
            display: none !important;
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
            position: flex;
            bottom: 20px;
            width: 150%;
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

        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: var(--dark-purple-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- Load konfigurasi login ---
# --- AUTHENTICATOR (Tetap di-load ulang) ---
try:
    with open("config.yaml") as file: 
        config = yaml.load(file, Loader=yaml.SafeLoader)
except FileNotFoundError:
    st.error("FATAL ERROR: config.yaml tidak ditemukan.")
    st.stop()
except Exception as e:
    st.error(f"Error loading config: {e}")
    st.stop()

authenticator = Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

from navigation import make_sidebar

# (setelah authenticator diinisialisasi)
make_sidebar(authenticator)

# --- KONTEN HALAMAN UTAMA (BAHASA "AKU-KAMU") ---

# Hero Section
st.markdown("<h1 class='header-title'>🏋️‍♀️ Your Personal Fitness Guide</h1>", unsafe_allow_html=True)
st.write("""
Selamat datang di **Exercise Recommendation App**! Lupakan bingung mau latihan apa atau makan apa hari ini.
Aplikasi ini adalah *coach* digital kamu, memberikan rekomendasi olahraga dan nutrisi yang dibuat khusus buat kamu. 
*No more guesswork, just results*. 💪
""")

st.markdown("---")

# --- FEATURE HIGHLIGHTS (BAHASA "AKU-KAMU") ---
st.subheader("✨ Apa yang Bisa Kamu Lakuin di Sini?")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### ⚙️ Rekomendasi Personal")
    st.write("Dapetkan saran latihan berdasarkan kondisi tubuh (BMI), tujuan, dan riwayat kesehatan kamu. *Pure science*, bukan kira-kira.")

with col2:
    st.markdown("### 🥗 Panduan Asupan")
    st.write("Bukan cuma latihan, aplikasi ini juga memberikan panduan makanan yang sudah divalidasi ahli. *Eat smart, train smart*.")

with col3:
    st.markdown("### 💾 Simpan Rencana Kamu")
    st.write("Nemu *workout plan* yang kamu suka? Simpen ke Profile. Favoritin *exercise* atau makanan spesifik agar gampang di-cek lagi nanti.")

st.markdown("---")
# --- AKHIR PERUBAHAN ---


# --- CTA / MOTIVATIONAL SECTION (BAHASA "AKU-KAMU") ---
with st.container():
    st.markdown("""
    <div style="
        background: var(--soft-purple-bg);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    ">
        <h2 style="color: var(--soft-purple-text); font-family: 'Poppins', sans-serif;">🔥 “Your body can stand almost anything. It’s your mind you have to convince.” 🔥</h2>
        <p style="font-size: 1.1rem; color: #555;">Mulai dari langkah kecil hari ini — klik tab <b>Recommendation</b> di sidebar dan dapetin latihan terbaik buat kamu.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tampilkan form login HANYA JIKA BELUM LOGIN
# if not st.session_state.get("authentication_status"):
#     st.markdown("---")
#     st.subheader("Login atau Daftar untuk Mengakses Fitur Profile")
    
#     login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])
    
#     with login_tab:
#         authenticator.login("main", key="login_form")
#         auth_state = st.session_state.get("authentication_status")
#         if auth_state:
#             st.success("Login berhasil! 🚀")
#             time.sleep(1)
#             st.rerun() 
#         elif auth_state is False:
#             st.error("Username / password salah.")
#         # (Gak perlu 'elif auth_state is None')
            
#     with signup_tab:
#         try:
#             registered = authenticator.register_user(location="main", key="signup_form")
#             if registered:
#                 st.success("Pendaftaran berhasil! Menyimpan config...")
#                 with open("config.yaml", "w") as file:
#                     yaml.dump(config, file, default_flow_style=False)
#                 st.info("✅ Pendaftaran sukses! Silakan pindah ke tab 'Login'.")
#         except Exception as e:
#             st.error(f"Terjadi error waktu daftar: {e}")

# Kalo sudah login, bagian ini gak akan tampil