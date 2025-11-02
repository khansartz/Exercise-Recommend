# pages/3_Works.py

import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from PIL import Image
from streamlit_option_menu import option_menu
import time
import os
import textwrap

# --- PAGE CONFIG ---
from navigation import make_sidebar, hide_default_sidebar

st.set_page_config(page_title="How it works", page_icon="✨", layout="wide")


hide_default_sidebar()




# --- CSS (PENAMBAHAN CSS BARU) ---
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

        [data-testid="stSidebar"] {
            border-right: 1px solid #DCDCDC; 
        }

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
            padding: 8px 0 !important;
            line-height: 1.5; 
        }
        

        
        /* Kartu untuk setiap langkah */
        .step-card {
            background: var(--cream-bg-dark); 
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin-bottom: 0.5rem; 
            border-left: 5px solid var(--theme-purple); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        /* Judul di dalem kartu (Langkah 1, 2, 3) */
        .step-card h3 {
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            color: var(--dark-purple-solid); 
            margin-bottom: 0rem;
            margin-top: 0rem; 
            display: flex;
            align-items: center;
            justify-content: flex-start;
        }

        /* Lingkaran angka 1, 2, 3, 4 */
        .step-card h3 span { 
            background: var(--dark-purple-solid);
            color: white;
            border-radius: 50%;
            padding: 4px 12px; 
            margin-right: 12px;
            font-size: 1.1rem;
            line-height: 1.5rem;
        }
        
        .step-content {
            padding: 1rem 0rem 0rem 0.5rem;
        }
        .step-content p, .step-content li {
            font-size: 1.05rem;
            line-height: 1.7;
            color: var(--dark-text);
        }
        .step-content img {
            border-radius: 10px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        .step-divider {
            border-top: 2px solid var(--cream-bg-dark);
            margin: 2rem 0;
        }

        /* Kotak validasi */
        .validation-box {
            background: var(--soft-purple-bg);
            border: 2px solid var(--dark-purple-solid);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            /* text-align: center; */ 
            margin-top: 2rem;
        }
        .validation-box h3 {
            color: var(--dark-purple-text);
            margin-bottom: 0.5rem;
            font-family: 'Poppins', sans-serif;
        }
        .validation-box h4 {
            color: var(--dark-purple-text);
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            font-family: 'Poppins', sans-serif;
            border-bottom: 1px solid var(--dark-purple-hover);
            padding-bottom: 5px;
        }
        .validation-box p {
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

# --- KONTEN HALAMAN 'HOW IT WORKS' ---

st.markdown("<h1 class='header-title'>✨ Gimana Cara Kerjanya?</h1>", unsafe_allow_html=True)

st.markdown("""
<p style='font-size: 1.1rem; line-height: 1.7;'>
Kamu mungkin penasaran, "Kok aplikasi ini bisa 'nebak' latihan dan makanan yang pas buat aku?"
<br>
Jawabannya: Ini bukan sihir, tapi teknologi! 🤖 Aplikasi ini menggunakan <b>dua lapisan Model Machine Learning</b> untuk mengubah data mentah kamu (seperti tinggi dan berat badan) menjadi sebuah rencana yang spesifik dan personal.
</p>
""", unsafe_allow_html=True)

# --- GAMBAR FLOWCHART ---
st.image("media/flowchart.png",
         caption="Alur kerja sistem")

st.markdown("<hr class='step-divider'>", unsafe_allow_html=True)

st.subheader("Proses di Balik Layar")

# --- LANGKAH 1 ---
st.markdown("""
<div class="step-card">
    <h3><span>1</span>Langkah 1: Kamu Memberi Kami "Bahan Baku"</h3>
</div>
""", unsafe_allow_html=True)

col1_1, col1_2 = st.columns([2, 1])
with col1_1:
    st.markdown("""
    <div class="step-content">
        <p>Semua dimulai dari form di halaman Rekomendasi. Kamu masukin data seperti:</p>
        <ul>
            <li>Usia, Tinggi, dan Berat Badan (buat ngitung BMI kamu)</li>
            <li>Jenis Kelamin</li>
            <li>Riwayat Kesehatan (Hipertensi / Diabetes)</li>
        </ul>
        <p>Data ini adalah "bahan baku" paling penting yang jadi pondasi dari semua rekomendasi.</p>
    </div>
    """, unsafe_allow_html=True)
with col1_2:
    st.image("https://cdn.dribbble.com/users/24711/screenshots/3886002/falcon_persistent_connection_2x.gif", 
             use_container_width=True, 
             caption="Data kamu di-input ke sistem")

st.markdown("<hr class='step-divider'>", unsafe_allow_html=True)

# --- LANGKAH 2 (LAYOUT DIBALIK) ---
st.markdown("""
<div class="step-card">
    <h3><span>2</span>Langkah 2: Asisten Pertama Menemukan "Grup" Kamu</h3>
</div>
""", unsafe_allow_html=True)

col2_1, col2_2 = st.columns([1, 2])
with col2_1:
    st.image("https://user-images.githubusercontent.com/75358720/161425446-e086dc39-4683-4590-b6cb-9a96466bd589.gif", 
             use_container_width=True, 
             caption="Model 1 (KNN) mengklasifikasikan data kamu")
with col2_2:
    st.markdown("""
    <div class="step-content">
        <p>Setelah kamu klik submit, data kamu (terutama BMI dan tujuan umummu) langsung dikirim ke <b>Model Cerdas 1 (Klasifikasi KNN)</b>.</p>
        <ul>
            <li><b>Analoginya:</b> Anggap aja model ini seperti resepsionis di gym.</li>
            <li><b>Tugasnya:</b> Dia nggak milih latihan, tapi dia menganalisis profil kamu dan nentuin kamu itu masuk <b>"Tipe Kebutuhan"</b> yang mana.</li>
            <li><b>Contoh:</b> Dia bakal bilang, "Oke, kamu masuk grup <b>'Program Penurunan Berat Badan'</b>."</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='step-divider'>", unsafe_allow_html=True)

# --- LANGKAH 3 ---
st.markdown("""
<div class="step-card">
    <h3><span>3</span>Langkah 3: Asisten Kedua Memilihkan "Menu"</h3>
</div>
""", unsafe_allow_html=True)

col3_1, col3_2 = st.columns([2, 1])
with col3_1:
    st.markdown("""
    <div class="step-content">
        <p>Sekarang kita tahu "Tipe Kebutuhan" kamu. Tapi, orang di grup 'Weight Loss' yang punya hipertensi, latihannya pasti beda sama yang nggak. Di sinilah <b>Model Cerdas 2 (Content-Based Filtering)</b> masuk.</p>
        <ul>
            <li><b>Analoginya:</b> Kalo tadi resepsionis, yang ini adalah <b>Personal Trainer</b>-nya.</li>
            <li><b>Tugasnya:</b> Dia ngambil Tipe Kebutuhan kamu (dari Langkah 2) DAN data riwayat kesehatanmu.</li>
            <li>Dia lalu "menyaring" (<i>filtering</i>) ratusan database rencana latihan, alat, dan diet buat nemuin satu set yang paling cocok dan aman.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with col3_2:
    st.image("https://appinventiv.com/wp-content/uploads/2025/02/1_E8c4PEwsogQQWJPErGda2A-1-1.gif", 
             use_container_width=True, 
             caption="Model 2 (CBF) menyaring hasil")

st.markdown("<hr class='step-divider'>", unsafe_allow_html=True)

# --- LANGKAH 4 (LAYOUT DIBALIK) ---
st.markdown("""
<div class="step-card">
    <h3><span>4</span>Langkah 4: Voila! Rencana Personal Kamu Siap</h3>
</div>
""", unsafe_allow_html=True)

col4_1, col4_2 = st.columns([1, 2])
with col4_1:
    st.image("https://d2okq48tcg0bvb.cloudfront.net/Solution3.gif", 
             use_container_width=True, 
             caption="Rekomendasi final muncul di app kamu")
with col4_2:
    st.markdown("""
    <div class="step-content">
        <p>Hasil saringan dari Langkah 3 itulah yang kamu lihat di halaman Rekomendasi!</p>
        <ul>
            <li>Rekomendasi Latihan (Squats, Push-up, dll.)</li>
            <li>Rekomendasi Alat (Dumbbell, Matras, dll.)</li>
            <li>Panduan Diet (Karbohidrat, Protein, dll.)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# --- KOTAK VALIDASI (DIREVISI TOTAL) ---

st.markdown(textwrap.dedent("""
    <div class="validation-box">
        <h3>🧑‍⚕️ Ini yang Paling Penting: Data & Validasi Ahli</h3>
        <h4>Dari Mana Datanya?</h4>
        <p>
            Model Machine Learning ini nggak "ngarang". Perancang aplikasi ini dapetin 
            <b>dataset latihan dari  National Institute of Allergy and Infectious Diseases (NIAID) data dengan DOI:   <a href='https://data.mendeley.com/datasets/zw8mtbm5b9/1' style='color: var(--soft-purple-text); font-weight:600;'>
        10.17632/zw8mtbm5b9.1</a>
        </b>, yang merupakan sumber terpercaya. 
            Tugas perancang adalah mengolah dan "melatih" model ML untuk bisa mengenali pola dari data tersebut.
        </p>
        <h4>Validasi Latihan oleh Personal Trainer (PT)</h4>
        <p>
            Semua data latihan dan <b>pemilihan</b> di baliknya (termasuk pemilihan latihan, alat, dan kecocokannya dengan riwayat kesehatan) <b>bukan</b> cuma diambil  <b>mentah-mentah</b> dari dataset. 
            <br><br>
            Seluruh datanya sudah di-review dan disesuaikan oleh <b>Personal Trainer (PT) profesional</b> untuk memastikan semua program latihannya efektif, aman, dan cocok untuk tiap level kebugaran.
        </p>
        <h4>Validasi Diet oleh Ahli Gizi (Studi Kasus)</h4>
        <p>
            Sebagai bukti kalo proses validasi ini beneran dilakukan, ini ada cerita kecil:
            <br><br>
            Awalnya perancang sudah bikin sistem rekomendasi makanan yang super spesifik dan kompleks. Tapi, setelah divalidasi, <b>Ahli Gizi</b> kami memberikan </b>insight</b> penting: "Ini terlalu rumit. Daripada ngasih rekomendasi spesifik yang belum tentu cocok, jauh lebih aman dan efektif kalo kita pake panduan <b>'Isi Piringku' dari Kemenkes</b>."
            <br><br>
            <b>Dan kami setuju.</b>
            <br>
            Makanya, rekomendasi asupan di aplikasi ini sengaja bersifat general (makanan apa yang bagus, dan apa yang harus dihindari penderita hipertensi atau diabetes). Ini adalah pilihan sadar untuk ngasih kamu rekomendasi yang <b>Aman, Terbukti, dan Tervalidasi Kemenkes.</b>
        </p>
    </div>
    """), unsafe_allow_html=True)


# --- LINK GITHUB (TAMBAHAN BARU) ---
st.markdown("<hr class='step-divider'>", unsafe_allow_html=True)
st.subheader("Masih Penasaran?")
st.markdown("""
<p style='font-size: 1.1rem; text-align: center;'>
Penasaran sama kode di baliknya? Kamu bisa cek semua kodenya, dari model ML sampai tampilan web-nya, langsung di link ini.    <br><br>
    <a href='https://github.com/khansartz/Exercise-Recommend' style='color: var(--soft-purple-text); font-weight:600; font-size: 1.2rem;'>
        [Klik di sini untuk melihat kode di GitHub ↗]
    </a>
</p>
""", unsafe_allow_html=True)