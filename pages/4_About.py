# pages/4_About.py

import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from PIL import Image
from streamlit_option_menu import option_menu
import time
import os

# --- PAGE CONFIG ---
from navigation import make_sidebar, hide_default_sidebar

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

hide_default_sidebar()

 


# --- CSS (Copy-paste dari Home.py) ---
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

        /* --- HALAMAN UTAMA & JUDUL GRADASI --- */
        /*.stApp {
            background: var(--cream-bg-light); 
        }*/
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
          /* background-color: var(--cream-bg-dark);*/ 
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
    
    /* Box untuk Tech Stack */
    .tech-stack-box {
        background-color: var(--soft-purple-bg);
        padding: 1.5rem;
        border-radius: 12px;
        /* text-align: center; */ /* Kita buat rata kiri */
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        height: 100%; /* Bikin tingginya sama */
    }
    .tech-stack-box p {
        font-size: 1.05rem; 
        color: #333;
        line-height: 1.7;
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
authenticator = Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

make_sidebar(authenticator)

# --- KONTEN HALAMAN ABOUT (DIPERBARUI) ---

# --- HEADER DENGAN LOGO ---


st.markdown("<h1 class='header-title'>🖥️ Tentang Aplikasi Ini</h1>", unsafe_allow_html=True)


# --- INTRO SECTION (BAHASA "AKU-KAMU") ---
st.markdown("""
<div style='font-size:17px; line-height:1.8;'>
    Selamat Datang! 👋 <br>
    Ini adalah <b>Exercise Recommendation App</b>, sebuah aplikasi yang <b>aku</b> rancang untuk membantu <b>kamu</b> mendapatkan <b>rekomendasi olahraga dan nutrisi</b> yang personal dan sesuai dengan kebutuhan tubuhmu.
    Aku percaya setiap orang punya ritme dan tujuan kebugaran yang unik. 💪<br>
    Oleh karena itu, aplikasi ini aku bangun untuk membantumu berlatih secara lebih <b>cerdas, konsisten, dan efisien</b>.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- FEATURE GRID / VISI MISI (DISESUAIKAN DENGAN FITUR ASLI) ---
st.subheader("🎯 Apa Tujuan Aplikasi Ini?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🤖 Rekomendasi Cerdas")
    st.write("Memberikan rekomendasi latihan yang dipersonalisasi menggunakan **Machine Learning**, berdasarkan data tubuh, tujuan, dan riwayat kesehatanmu.")

with col2:
    st.markdown("### 🥗 Panduan Gizi Tervalidasi")
    st.write("Menyajikan panduan nutrisi 'Isi Piringku' (Kemenkes & UNICEF) yang telah divalidasi oleh **Ahli Gizi** dan **Personal Trainer** profesional.")

with col3:
    st.markdown("### 💾 Rencana Personal Kamu")
    st.write("Membantumu menyimpan rencana latihan ke profil dan mem-favoritkan item-item spesifik (latihan/makanan) agar mudah diakses kembali.")

st.markdown("---")

# --- LAYOUT BARU (2 KOLOM: PENGEMBANG & TEKNOLOGI) ---
st.subheader("👨‍💻 Tentang Perancang & Teknologi di Baliknya")
col_dev, col_tech = st.columns(2)

# --- KIRI: TENTANG PENGEMBANG (KATA "AKU" DIUBAH JADI "PERANCANG") ---
with col_dev:
    st.markdown("#### **Perancang**")
    col_img, col_text = st.columns([1, 2]) # Kolom internal buat foto & teks
    
    with col_img:
        try:
            dev_img = Image.open(os.path.join(ROOT_DIR, "profile.jpg"))
            st.image(dev_img, width=150)
        except FileNotFoundError:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)

    with col_text:
        st.markdown("""
        <div style='font-size:16px; line-height:1.7;'>
            Hai! Aku <b>Khansa Maritza</b> sebagai perancang dari aplikasi ini. 
<br>
            Saat ini, aku adalah <b>mahasiswa semester 7</b> yang mengembangkan aplikasi ini sebagai proyek skripsi.        </div>
        """, unsafe_allow_html=True)
    
    # Teks di bawah foto & nama
    st.markdown("""
    <div style='font-size:16px; line-height:1.7; margin-top: 10px;'>
        Lewat proyek ini, aku (sebagai perancang) ingin menunjukkan bagaimana teknologi bisa mendukung gaya hidup sehat. 
        <br><br>
        Jika <b>kamu</b> punya ide atau saran, jangan ragu untuk menghubungi email di bawah ya! 🙌 
        <br>
        <a href='mailto:khansamaritzaar@gmail.com' style='color: var(--soft-purple-text); font-weight:600;'>📩 khansamaritzaar@gmail.com</a>
    </div>
    """, unsafe_allow_html=True) # Catatan: Aku tetep pake "aku" di sini biar personal, tapi "perancang" di judul

# --- KANAN: TEKNOLOGI (DIUBAH SESUAI REQUEST) ---
with col_tech:
    st.markdown("#### **Teknologi**")
    st.markdown("""
    <div class='tech-stack-box'>
        <p>
            Aplikasi ini dibangun menggunakan:<br><br>
            🐍 <b>Python</b><br>
            (Bahasa pemrograman utama)<br><br>
            🚀 <b>Streamlit</b><br>
            (Untuk membangun antarmuka web interaktif)<br><br>
            🧠 <b>KNN dan Content-Based Filtering</b><br>
            (Untuk model Machine Learning)
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- FUN FACT / QUOTE SECTION (TETAP SAMA) ---
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