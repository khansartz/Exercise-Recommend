# pages/Profile.py

import streamlit as st
import os
import yaml
from PIL import Image
import json
import time
from streamlit_authenticator import Authenticate
from navigation import make_sidebar, hide_default_sidebar

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")

hide_default_sidebar()

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
            --cream-bg-light: #FAF9F6;  
            --cream-bg-dark: #F0EFEA;   
            --dark-text: #333333;       
            --hover-cream: #E0DFD9;     
            
            /* Warna Baru (Soft Purple Theme) */
            --soft-purple-bg: #E8E2F7;    /* Latar tombol aktif */
            --soft-purple-text: #5D3B9C; /* Teks tombol aktif */
            --soft-purple-hover: #D8CCF2;  
            --dark-purple-solid: #5D3B9C; /* Tombol logout */
            --dark-purple-hover: #4A2E7E; /* Hover tombol logout */
        }
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
        [data-testid="stSidebar"] .stButton {
            position: flex;
            bottom: 20px;
            width: 200%;
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
            height: 45px; 
            padding: 8px 0 !important; 
            line-height: 1.5; 
        }
            [data-testid="stSidebar"] .stButton button:hover {
            background: var(--dark-purple-hover); 
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }
    </style>
""", unsafe_allow_html=True)

# PATH SETUP 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FOLDER = os.path.join(ROOT_DIR, "data")
USER_DATA_FILE = os.path.join(DATA_FOLDER, "user_data.json")
CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")


os.makedirs(DATA_FOLDER, exist_ok=True)

# LOAD CONFIG & AUTH 
try:
    with open(CONFIG_PATH) as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
except Exception as e:
    st.error(f"FATAL ERROR: config.yaml tidak ditemukan atau error: {e}")
    st.stop()

authenticator = Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

make_sidebar(authenticator)

# JUDUL HALAMAN 
st.markdown("<h1 class='header-title'>👤 Profil Pengguna</h1>", unsafe_allow_html=True)

# HELPER FUNGS 
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Error load user data:", e)
            return {"saved_recommendations": {}, "favorites": {}}
    else:
        return {"saved_recommendations": {}, "favorites": {}}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving user data:", e)

# AUTH CHECK 
if not st.session_state.get("authentication_status"):
    st.error("Login dulu biar bisa liat profil kamu 😎")
    st.info("Kembali ke Home untuk login.")
    if st.button("Kembali ke Home"):
        st.switch_page("home.py")
    st.stop()

# LOAD USER DATA 
username = st.session_state.get("username")
name = st.session_state.get("name", username)
user_data = load_user_data()
saved_recs = user_data.get("saved_recommendations", {}).get(username, [])
favorites = user_data.get("favorites", {}).get(username, [])

# PROFILE HEADER 
st.markdown(f"""
<div style='
    background-color: #E8E2F7; 
    padding: 1.5rem 2rem; 
    border-radius: 12px; 
    margin-bottom: 1.5rem;
    display: flex; 
    align-items: center;
'>
    <img src='https://cdn-icons-png.flaticon.com/512/149/149071.png' width='80' style='margin-right: 20px;'>
    <div>
        <h2 style='margin-bottom:0;'>{name}</h2>
        <p style='margin-top:4px; color:#5D3B9C;'>@{username}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# SECTION: REKOMENDASI DISIMPAN 
st.subheader("💾 Rekomendasi yang Kamu Simpan")
if saved_recs:
    for idx, rec in enumerate(reversed(saved_recs)):
        st.markdown(f"**{len(saved_recs)-idx}. {rec.get('pred_label','-')}** — Goal: {rec.get('goal','-')} — BMI: {rec.get('bmi','-')}")
        with st.expander("Lihat detail rekomendasi"):
            best_row = rec.get("best_row", {})
            st.write("**Latihan (ringkasan):**")
            st.write(best_row.get("Exercises", "-"))
            st.write("**Alat (ringkasan):**")
            st.write(best_row.get("Equipment", "-"))
            st.write("**Diet (ringkasan):**")
            st.write(best_row.get("Diet", "-"))
            if st.button(f"Hapus rekomendasi ini", key=f"delrec_{idx}"):
                saved_list = user_data.get("saved_recommendations", {}).get(username, [])
                real_idx = len(saved_list) - 1 - idx
                saved_list.pop(real_idx)
                user_data["saved_recommendations"][username] = saved_list
                save_user_data(user_data)
                st.rerun()
else:
    st.info("Belum ada rekomendasi yang kamu simpen 😅")

st.markdown("---")

# SECTION: FAVORIT 
st.subheader("❤️ Favorit Kamu")
if favorites:
    cols = st.columns(3)
    for i, fav in enumerate(favorites):
        with cols[i % 3]:
            st.markdown(f"<div style='background:#F9F9FB;padding:1rem;border-radius:10px;margin-bottom:1rem;text-align:center;'>"
                        f"🌟 <b>{fav}</b></div>", unsafe_allow_html=True)
    if st.button("Hapus Semua Favorit"):
        user_data.setdefault("favorites", {})[username] = []
        save_user_data(user_data)
        st.success("Semua favorit berhasil dihapus.")
        st.rerun()
else:
    st.info("Belum ada item yang kamu favoritkan.")

st.markdown("---")

# SECTION: UBAH PASSWORD 
st.subheader("🔐 Ubah Password")
st.write("Ganti password kamu di sini biar akun makin aman 🔒")

try:
    if authenticator.reset_password(username, location="main"):
        # 1. Tampilkan notifikasi dulu
        st.success("Password berhasil diubah! Menyimpan konfigurasi...")
        st.info("Silakan login kembali dengan password baru kamu...")

        # 2. Simpan config (ini udah bener)
        with open(CONFIG_PATH, "w") as file:
            yaml.dump(config, file, default_flow_style=False)

        # 3. KASIH JEDA WAKTU (misal 3 detik)
        time.sleep(3) # <-- INI BAGIAN PENTINGNYA

        # 4. Baru logout dan rerun
        authenticator.logout("Logout", "main", key="logout_after_reset")
        st.rerun()

except Exception as e:
    st.error(f"Terjadi error saat ubah password: {e}")

st.markdown("---")