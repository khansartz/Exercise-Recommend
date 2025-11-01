import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
import time
from navigation import make_sidebar, hide_default_sidebar
st.set_page_config(page_title="Login", page_icon="🔐")


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
            height: 45px; /* Set tinggi manual */
            padding: 8px 0 !important; /* Paksa padding vertikal */
            line-height: 1.5; /* Jaga teks tetap di tengah */
        }
            
            [data-testid="stSidebar"] button[kind="secondary"] {
            width: 70% !important;          /* Lebar tombol */
            display: block !important;
            background-color: var(--dark-purple-solid);
            color: white;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: var(--dark-purple-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Load config
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

make_sidebar(authenticator)

st.title("🔐 Login / Sign Up")
st.write("Masuk ke akun lo buat akses semua fitur! 🚀")

login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

with login_tab:
    authenticator.login("main", key="login_page")
    auth_state = st.session_state.get("authentication_status")

    if auth_state:
        st.success("Login berhasil! 🚀")
        time.sleep(1)
        st.switch_page("home.py")
    elif auth_state is False:
        st.error("Username / password salah.")

with signup_tab:
    try:
        registered = authenticator.register_user(location="main", key="signup_page")
        if registered:
            st.success("Pendaftaran berhasil! Menyimpan config...")
            with open("config.yaml", "w") as file:
                yaml.dump(config, file, default_flow_style=False)
            st.info("✅ Silakan login lewat tab Login.")
    except Exception as e:
        st.error(f"Terjadi error waktu daftar: {e}")
