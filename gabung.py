import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
import time
from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import pandas as pd
import joblib
import re
import warnings
from PIL import Image, ImageOps
import requests
from io import BytesIO
import base64
import time
import urllib.parse
# Import tambahan untuk hitung on-the-fly
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os # Untuk check folder models

# ------------------------
# FUNGSI BANTU (Tetap sama)
# ------------------------
def calculate_bmi(height_cm, weight_kg):
    if height_cm == 0: return 0
    height_m = height_cm / 100.0
    return weight_kg / (height_m ** 2)

def get_bmi_level(bmi):
    if bmi < 18.5: return "Underweight"
    elif 18.5 <= bmi < 24.9: return "Normal"
    elif 25.0 <= bmi < 29.9: return "Overweight"
    else: return "Obese"

def get_fitness_goal(level):
    if level in ["Underweight", "Normal"]: return "Weight Gain"
    elif level in ["Overweight", "Obese"]: return "Weight Loss"
    return None

def extract_diet_items(category_key, diet_string):
    if not isinstance(diet_string, str): return []
    match = re.search(fr'{category_key}:\s*\(([^)]*)\)', diet_string, re.IGNORECASE)
    if match:
        item_string = match.group(1)
        return clean_items(item_string)
    return []

def clean_items(text):
    if not isinstance(text, str): return []
    text = text.replace("(", "").replace(")", "").replace(";", "|")
    text = text.replace(" and ", "|").replace(" or ", "|").replace(",", "|")
    cleaned_list = [item.strip().title() for item in text.split('|') if item.strip() and item.strip().lower() not in ["and", "or"]]
    return list(dict.fromkeys(cleaned_list))

def render_recommendation_section(title, items_list):
    st.subheader(title)
    if items_list and isinstance(items_list, list):
        for i in range(0, len(items_list), 2):
            cols = st.columns(2)
            items_in_row = items_list[i:i+2]
            for idx, item in enumerate(items_in_row):
                if isinstance(item, str) and item:
                    with cols[idx]:
                        clickable_card(item)
            st.write("") # Jarak antar baris
    else:
        st.info(f"Tidak ada rekomendasi spesifik untuk {title.split(':')[0]}.")


# ------------------------
# FUNGSI INFERENSI (CBF Diubah)
# ------------------------
categorical_cols = ['Sex', 'Level', 'Fitness Goal']
numeric_cols = ['Age', 'Height', 'Weight', 'BMI']

def knn_predict_fitness(user_input_dict, le_dict, scaler, knn_model, le_target):
    # Fungsi ini tetap sama
    ordered_cols = ['Sex', 'Age', 'Height', 'Weight', 'BMI', 'Level', 'Fitness Goal']
    new_user = pd.DataFrame([user_input_dict])
    try:
        for col in categorical_cols:
            new_user.loc[:, col] = le_dict[col].transform(new_user[col])
    except Exception as e: return f"Error saat encoding: {e}."
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        new_user.loc[:, numeric_cols] = scaler.transform(new_user[numeric_cols])
    new_user = new_user[ordered_cols]
    pred_class = knn_model.predict(new_user)[0]
    return le_target.inverse_transform([pred_class])[0]

def clickable_card(label):
    if not label or not isinstance(label, str):
        print(f"DEBUG clickable_card: Label tidak valid: {label}")
        return
    key = label.lower().replace(" ", "_")
    print(f"DEBUG clickable_card: Received label='{label}', Generated key='{key}'")
    if key in media_dict:
        img64 = img_to_base64(media_dict[key])
        if img64:
            url = f"/?detail={urllib.parse.quote(key)}"
            # --- UBAH target="_blank" DI SINI ---
            st.markdown(
                f"""
                <a href="{url}" target="_blank" style="text-decoration:none;">
                    <div class="rec-card">
                    <img src="data:image/png;base64,{img64}" style="width:240px; height:170px; border-radius:8px; display:block; margin:auto;">
                    <p style="text-align:center; font-weight:bold; margin-top:6px; color:black;">{label}</p>
                    </div>
                </a>
                """, unsafe_allow_html=True
            )
            # --- BATAS PERUBAHAN ---
        else: st.markdown(f"**- {label}** (Error Gambar)")
    else: st.markdown(f"**- {label}** (Media key tidak ditemukan: '{key}')")

def img_to_base64(path_or_url, size=(250,180)):
    try:
        if path_or_url.startswith("http"): img = Image.open(BytesIO(requests.get(path_or_url).content))
        else: img = Image.open(path_or_url)
        img = img.convert("RGB").resize(size)
        img = ImageOps.expand(img, border=2, fill="#e6e6e6")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"Error img_to_base64 ({path_or_url}): {e}")
        return None
        
from media import get_media_dict
from media_info import get_media_info
media_dict = get_media_dict()
media_info = get_media_info()

def cbf_recommendations(fitness_type, hypertension, diabetes, top_n=5):
    """Fungsi CBF: Filter -> Hitung Sim ON-THE-FLY -> Top N -> Mode"""
    global preparation, tf # Akses preparation dan TF-IDF Vectorizer (BUKAN cosine_sim matrix)

    hypertension_clean = str(hypertension).strip().title()
    diabetes_clean = str(diabetes).strip().title()

    # 1. Filter data
    filtered_df = preparation[
        (preparation['Fitness Type'] == fitness_type) &
        (preparation['Hypertension'].str.strip().str.title() == hypertension_clean) &
        (preparation['Diabetes'].str.strip().str.title() == diabetes_clean)
    ].copy()

    if filtered_df.empty:
        st.warning(f"Tidak ada data cocok DENGAN. Fallback...")
        filtered_df = preparation[preparation['Fitness Type'] == fitness_type].copy()
        if filtered_df.empty: return {"Error": f"Tidak ada data untuk Tipe Fitness: {fitness_type}."}

    current_top_n = min(top_n, len(filtered_df))
    if current_top_n == 0: return {"Error": "Tidak ada data cocok sama sekali."}

    # --- HITUNG SIMILARITY ON-THE-FLY ---
    if len(filtered_df) <= 1: # <= 1 karena kalau cuma 1, mode() nya langsung item itu sendiri
         # Jika hanya <= 1 data cocok, tidak perlu similarity
         top_n_indices = filtered_df.index.tolist()
         print("\nWarning: Hanya <= 1 data cocok, similarity tidak dihitung.")
    else:
        # 2. Ambil 'content' dari data terfilter (pastikan kolom 'content' ada di preparation.pkl)
        if 'content' not in filtered_df.columns:
             # Fallback jika kolom 'content' tidak ada (seharusnya tidak terjadi jika pkl benar)
             st.error("Kolom 'content' tidak ditemukan di data preparation!")
             filtered_df['content'] = (
                filtered_df['Exercises'].fillna('') + ' ' +
                filtered_df['Equipment'].fillna('') + ' ' +
                filtered_df['Diet'].fillna('')
             ).str.strip()
             print("Warning: Kolom 'content' dibuat ulang secara on-the-fly.")

        filtered_content = filtered_df['content'].fillna('')

        # 3. Transform HANYA content terfilter pake TF-IDF Vectorizer
        try:
             tfidf_matrix_filtered = tf.transform(filtered_content)
             print(f"TF-IDF matrix (filtered) shape: {tfidf_matrix_filtered.shape}")
        except Exception as tf_err:
             return {"Error": f"Gagal transform TF-IDF: {tf_err}"}


        # 4. Hitung Cosine Similarity HANYA untuk data terfilter
        try:
             # cosine_similarity butuh minimal 2 sampel jika Y=None (membandingkan X dengan dirinya sendiri)
             if tfidf_matrix_filtered.shape[0] > 1:
                  cosine_sim_filtered = cosine_similarity(tfidf_matrix_filtered)
             else: # Jika hanya 1 sampel setelah filter, similarity matrixnya cuma [[1.]]
                  cosine_sim_filtered = np.array([[1.0]])

             print(f"Cosine Sim matrix (filtered) shape: {cosine_sim_filtered.shape}")
        except Exception as cs_err:
             return {"Error": f"Gagal hitung Cosine Sim: {cs_err}"}


        # 5. Hitung skor rata-rata kemiripan
        avg_sim_scores = cosine_sim_filtered.mean(axis=1)

        # 6. Buat series pandas untuk sorting (index = index asli dataframe)
        sim_scores_series = pd.Series(avg_sim_scores, index=filtered_df.index)

        # 7. Dapatkan index dari top N item PALING MIRIP
        top_n_indices = sim_scores_series.nlargest(current_top_n).index.tolist()
    # --- BATAS HITUNG ON-THE-FLY ---

    # 8. Ambil baris data dari top N item terpilih
    topN_df = preparation.loc[top_n_indices]
    print(f"\nTop {current_top_n} item terpilih (berdasarkan konten jika > 1):")
    print(topN_df[['Exercises', 'Equipment', 'Diet']])

    # 9. Voting (mode) dari top N item terpilih
    try:
        final_exercise = topN_df['Exercises'].mode()[0]
        final_equipment = topN_df['Equipment'].mode()[0]
        final_diet = topN_df['Diet'].mode()[0]
    except Exception as e: return {"Error": f"Gagal voting: {e}"}

    return {'Exercises': final_exercise, 'Equipment': final_equipment, 'Diet': final_diet}

def load_models_assets():
    print("Memuat model dan aset...")
    try:
        models_folder = "models" # Definisikan nama folder
        knn = joblib.load(os.path.join(models_folder, "knn_model.pkl"))
        le_dict = joblib.load(os.path.join(models_folder, "label_encoders.pkl"))
        le_target = joblib.load(os.path.join(models_folder, "target_encoder.pkl"))
        scaler = joblib.load(os.path.join(models_folder, "scaler.pkl"))
        preparation = joblib.load(os.path.join(models_folder, "preparation_data.pkl"))
        # --- MUAT TF-IDF VECTORIZER ---
        tf = joblib.load(os.path.join(models_folder, "tfidf_vectorizer.pkl"))
    except FileNotFoundError as e:
        st.error(f"ERROR: File model tidak ditemukan ({e}). Pastikan semua file .pkl ada di folder '{models_folder}'.")
        st.stop()
    except Exception as e:
        st.error(f"Error saat memuat model/aset: {e}")
        st.stop()


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Exercise Recommendation App",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Load konfigurasi login ---
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# --- SESSION STATE INIT ---
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = "guest"
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"
if "fade_state" not in st.session_state:
    st.session_state["fade_state"] = True
# --- State baru untuk form ---
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False


auth_status = st.session_state.get("authentication_status")

# --- CSS STYLING ---
st.markdown("""
    <style>
        /* ... (CSS lo yang keren itu tetep di sini, gak gue ubah) ... */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        body, div, p, h1, h2, h3 {
            font-family: 'Poppins', sans-serif;
            color: #333; /* Default text color */
        }

        /* Gradient Colors from Logo */
        :root {
            --primary-blue: #6495ED; 
            --primary-pink: #FF69B4; 
            --primary-purple: #9370DB; 
            --gradient-main: linear-gradient(to right, #6495ED, #9370DB, #FF69B4);
            --gradient-hover: linear-gradient(to right, #FF69B4, #9370DB, #6495ED);
        }

        /* Animasi fade-in */
        .fade-in {
            animation: fadeIn 0.8s ease;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(8px);}
            to {opacity: 1; transform: translateY(0);}
        }

        /* --- STYLING MINIMALIS --- */

        /* Set background jadi putih bersih */
        .stApp {
            background: #ffffff; 
        }
        
        /* Hapus box-in-box style, biarkan flat */
        .main .block-container {
            background-color: transparent;
            box-shadow: none;
            padding: 1rem 2rem;
        }

        /* Header */
        .header-container {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        /* --- GRADIENT DI TEKS JUDUL --- */
        .header-title {
            font-weight: 700;
            font-size: 2.5rem;
            margin-top: 10px;
            
            /* Magic buat bikin teks jadi gradient */
            background: var(--gradient-main);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-fill-color: transparent;
            padding-bottom: 5px; /* Kasih nafas dikit */
        }

        /* Logo */
        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 0.5rem;
            padding-top: 20px;
        }

        /* Sidebar Styling */
        .st-emotion-cache-16txt4v { /* Sidebar class */
            background-color: #f8f9fa; /* Abu-abu super muda */
            border-right: 1px solid rgba(0,0,0,0.05);
        }
        .st-emotion-cache-16txt4v .st-emotion-cache-vk336y { /* Sidebar content padding */
             padding-top: 2rem;
        }

        /* Streamlit Button Styling (Tetap keren dengan gradient hover) */
        .stButton button {
            background-color: var(--primary-purple);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .stButton button:hover {
            background: var(--gradient-hover);
            background-size: 200% auto;
            color: white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            transform: translateY(-2px);
        }
        .stButton button:active {
            transform: translateY(0);
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }

        /* Info box dibikin lebih soft */
        .st-emotion-cache-h6g92 { 
            background-color: #e7f0fe !important; /* Biru muda soft */
            color: #333 !important; /* Teks gelap biar kebaca */
            border: 1px solid var(--primary-blue) !important;
            border-left-width: 5px !important; /* Highlight di kiri */
        }
    </style>
""", unsafe_allow_html=True)


# --- HEADER SECTION (LOGO + NAVBAR BARU) ---
def show_header(active_page):
    # Logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        logo = Image.open("logo.jpg")
        st.image(logo, width=80)
    except FileNotFoundError:
        st.error("File logo.jpg tidak ditemukan. Pastikan file ada di folder yang sama.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Judul Aplikasi (sekarang di atas navbar)
    st.markdown(f"""
        <div class='header-container'>
            <h1 class='header-title'>Exercise Recommendation App</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- NAVBAR ---
    pages = ["home", "recommendation", "history", "about"]
    try:
        default_idx = pages.index(active_page)
    except ValueError:
        default_idx = 0

    selected = option_menu(
        menu_title=None,
        options=["Home", "Recommendation", "History", "About"],
        icons=["house", "clipboard-data", "clock-history", "info-circle"],
        menu_icon="cast",
        default_index=default_idx,
        orientation="horizontal",
        styles={
            # ... (Semua style navbar lo tetap di sini) ...
             "container": {
                "padding": "12px 25px",
                "background-color": "#ffffff",
                "border-radius": "40px",
                "width": "fit-content",
                "margin": "0 auto 20px auto",  # biar deket dikit sama judul
                "box-shadow": "0 2px 10px rgba(0,0,0,0.08)"
            },
            "nav-link": {
                "font-size": "15px",
                "font-weight": "500",
                "color": "#444",
                "border-radius": "20px",
                "padding": "7px 20px",
                "transition": "all 0.25s ease",
            },
            "nav-link:hover": {
                "background": "var(--gradient-hover)",
                "background-size": "200% auto",
                "color": "white",
                "box-shadow": "0 2px 8px rgba(0,0,0,0.15)",
                "transform": "translateY(-1px)"
            },
            "nav-link-selected": {
                "background": "#f3efff",
                "color": "var(--primary-purple)",
                "font-weight": "600"
            },
        }
    )

    # Logic ganti page
    links = {
        "Home": "home",
        "Recommendation": "recommendation",
        "History": "history",
        "About": "about"
    }
    new_page = links[selected]
    if new_page != st.session_state["current_page"]:
        st.session_state["current_page"] = new_page
        st.session_state["fade_state"] = False
        
        # --- PERUBAHAN: Reset flag form kalo ganti page ---
        st.session_state["show_login"] = False
        st.session_state["show_signup"] = False
        
        st.rerun()


# --- SIDEBAR AUTH (DIRUBAH) ---
st.sidebar.title("🏋️ Exercise Recommender")

if st.session_state["auth_status"] == "guest" or not auth_status:
    st.sidebar.write("Mode: 👤 Guest")
    
    # --- PERUBAHAN: Tombol ini sekarang set flag, bukan ganti page ---
    if st.sidebar.button("🔐 Login", key="login_sidebar"):
        st.session_state["show_login"] = True
        st.session_state["show_signup"] = False
        st.session_state["current_page"] = "home" # Paksa ke home
        st.rerun()
        
    if st.sidebar.button("📝 Sign Up", key="signup_sidebar"):
        st.session_state["show_signup"] = True
        st.session_state["show_login"] = False
        st.session_state["current_page"] = "home" # Paksa ke home
        st.rerun()

elif st.session_state["auth_status"] == "logged_in" and auth_status:
    try:
        authenticator.logout("🚪 Logout", "sidebar", key="logout_sidebar")
        st.sidebar.success(f"Halo, {st.session_state['name']} 👋")
        
        # --- PERUBAHAN: Reset flag kalo logout/ganti mode ---
        if st.sidebar.button("👤 Ganti ke Guest Mode", key="guest_switch"):
            st.session_state["auth_status"] = "guest"
            st.session_state["current_page"] = "home"
            st.session_state["authentication_status"] = None
            st.session_state["show_login"] = False
            st.session_state["show_signup"] = False
            st.rerun()
            
    except Exception as e:
        st.sidebar.button("🚪 Logout", key="logout_fallback")
        if st.session_state.get("logout_fallback"):
            st.session_state["auth_status"] = "guest"
            st.session_state["authentication_status"] = None
            st.session_state["current_page"] = "home"
            st.session_state["show_login"] = False
            st.session_state["show_signup"] = False
            st.rerun()


# --- MAIN CONTENT ---
page = st.session_state["current_page"]
fade_class = "fade-in" if st.session_state["fade_state"] else ""
st.session_state["fade_state"] = True  # set animasi on lagi

# HOME PAGE (DIRUBAH)
if page == "home":
    show_header("home") # Panggil header dengan pageaktif
    st.markdown(f"<div class='{fade_class}'>", unsafe_allow_html=True)
    
    # --- Konten Home Tetap Ada ---
    if not st.session_state["show_login"] and not st.session_state["show_signup"]:
        st.write("Selamat datang di **Exercise Recommendation App** 💪")
        st.info("Temukan rekomendasi latihan terbaik sesuai kebutuhan kamu!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- INJEK FORM SIGNUP DARI LOGIKA BARU ---
    if st.session_state.get("show_signup"):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("📝 Sign Up")
        try:
            registered = authenticator.register_user(location="main", key="signup_form")
            if registered:
                st.success("Pendaftaran berhasil! Menyimpan config...")
                # Tulis ke config.yaml
                with open("config.yaml", "w") as file:
                    yaml.dump(config, file, default_flow_style=False)

                # PENTING: Bikin ulang object authenticator
                authenticator = Authenticate(
                    config["credentials"],
                    config["cookie"]["name"],
                    config["cookie"]["key"],
                    config["cookie"]["expiry_days"]
                )
                
                st.info("✅ Pendaftaran sukses! Silakan login di bawah.")
                st.session_state["show_signup"] = False
                st.session_state["show_login"] = True
                st.rerun() # Rerun biar pakai authenticator baru

        except Exception as e:
            st.error(f"Terjadi error waktu daftar: {e}")

    # --- INJEK FORM LOGIN DARI LOGIKA BARU ---
    if st.session_state.get("show_login"):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🔐 Login")
        authenticator.login("main", key="login_form")
        auth_state = st.session_state.get("authentication_status")

        if auth_state:
            st.session_state["auth_status"] = "logged_in"
            st.session_state["name"] = st.session_state.get("name")
            st.session_state["username"] = st.session_state.get("username")
            st.success("Login berhasil! 🚀")
            st.session_state["show_login"] = False # Sembunyikan form
            st.rerun() # Rerun buat update sidebar & sembunyikan form
        elif auth_state is False:
            st.error("Username / password salah.")
        elif auth_state is None:
            st.info("Masukkan username & password kamu dulu.")


# RECOMMENDATION PAGE
# --- RECOMMENDATION PAGE (UPDATE) ---
# --- RECOMMENDATION PAGE ---

elif page == "recommendation":
    show_header("recommendation")  # header + navbar
    
    fade_class = "fade-in" if st.session_state["fade_state"] else ""
    st.session_state["fade_state"] = True
    
    st.markdown(f"<div class='{fade_class}'>", unsafe_allow_html=True)
    
    # --- Hero Section ---
    st.markdown(
        '<div class="hero"><h1>💪 Pelatih Kebugaran Pribadi Anda</h1>'
        '<p>Rekomendasi cerdas untuk latihan, alat, dan nutrisi harian Anda.</p></div>', 
        unsafe_allow_html=True
    )
    
    st.header("Masukkan Data Anda untuk Mendapatkan Rekomendasi")
    
    # --- Form Input User (di halaman) ---
    with st.form("user_input_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Usia", 10, 100, 25, 1)
            height_cm = st.number_input("Tinggi Badan (cm)", 100, 250, 170, 1)
            weight = st.number_input("Berat Badan (kg)", 30, 200, 70, 1)
        with col2:
            sex_display = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            hypertension_display = st.selectbox("Riwayat Hipertensi", ["Tidak", "Ada"])
            diabetes_display = st.selectbox("Riwayat Diabetes", ["Tidak", "Ada"])
        submitted = st.form_submit_button("Dapatkan Rekomendasi")
    
    # --- Logic Submit ---
    if submitted:
        sex = "Male" if sex_display == "Laki-laki" else "Female"
        hypertension = "Yes" if hypertension_display == "Ada" else "No"
        diabetes = "Yes" if diabetes_display == "Ada" else "No"
        
        with st.spinner("Mencari rekomendasi terbaik..."):
            bmi = calculate_bmi(height_cm, weight)
            level = get_bmi_level(bmi)
            goal = get_fitness_goal(level)
            
            knn_input = {"Sex": sex, "Age": age, "Height": height_cm, 
                         "Weight": weight, "BMI": bmi, "Level": level, "Fitness Goal": goal}
            
            pred_label = knn_predict_fitness(knn_input, le_dict, scaler, knn, le_target)
            
            if "Error" in pred_label:
                st.error(f"Prediksi KNN Gagal: {pred_label}")
            else:
                cbf_result = cbf_recommendations(fitness_type=pred_label, hypertension=hypertension, diabetes=diabetes, top_n=5)
                if "Error" in cbf_result:
                    st.error(f"Rekomendasi CBF Gagal: {cbf_result['Error']}")
                else:
                    st.session_state["recommendation_data"] = {
                        "pred_label": pred_label,
                        "level": level,
                        "goal": goal,
                        "bmi": bmi,
                        "best_row": cbf_result,
                        "hypertension": hypertension,
                        "diabetes": diabetes
                    }
                    st.rerun()
    
    # --- Render Hasil Rekomendasi ---
    if st.session_state.get("recommendation_data"):
        data = st.session_state["recommendation_data"]
        best_row = data["best_row"]
        
        st.success(f"Rekomendasi tipe latihan: **{data['pred_label']}**", icon="✅")
        st.markdown(f"Status Anda: **{data['level']}** (BMI: `{data['bmi']:.2f}`), tujuan yang direkomendasikan adalah **{data['goal']}**.")
        
        st.header("Rekomendasi Untuk Anda 👇")
        
        # Latihan
        exercise_list = clean_items(best_row.get("Exercises", ""))
        render_recommendation_section("🏋️ Latihan", exercise_list)
        
        # Alat
        equipment_list = clean_items(best_row.get("Equipment", ""))
        render_recommendation_section("🧰 Alat", equipment_list)
        
        # Diet
        st.subheader("🥗 Pola Makan (Tumpeng Gizi Seimbang)")
        raw_diet_string = best_row.get("Diet", "")
        if raw_diet_string:
            karbohidrat = extract_diet_items("Karbohidrat", raw_diet_string)
            mineral_serat = extract_diet_items("Mineral & Serat", raw_diet_string)
            protein = extract_diet_items("Protein", raw_diet_string)
            if karbohidrat: render_recommendation_section("Sumber Karbohidrat (3-4 porsi/hari):", karbohidrat)
            if mineral_serat: render_recommendation_section("Sumber Mineral & Serat (Sayur 3-4 porsi/hari, Buah 2-3 porsi/hari):", mineral_serat)
            if protein: render_recommendation_section("Sumber Protein (Total 2-4 porsi/hari):", protein)
        
        st.markdown("---")
        st.subheader("⚠️ Catatan Penting:")
        if data["diabetes"] == "Yes":
            st.warning("**Penderita Diabetes:** Batasi atau hindari makanan/minuman manis.")
        if data["hypertension"] == "Yes":
            st.warning("**Penderita Hipertensi:** Batasi garam/natrium dan makanan olahan.")
        if data["diabetes"] == "No" and data["hypertension"] == "No":
            st.info("Jaga pola makan seimbang, batasi gula, garam, dan lemak berlebih untuk kesehatan optimal.")
        
        if st.button("🧼 Reset Data"):
            st.session_state.pop("recommendation_data", None)
            st.rerun()
    
    else:
        st.info("👈 Silakan isi data Anda di atas, lalu klik tombol **'Dapatkan Rekomendasi'** untuk melihat saran latihan, alat, dan diet yang cocok untuk Anda!", icon="ℹ️")
    
    st.markdown("</div>", unsafe_allow_html=True)


# HISTORY PAGE
elif page == "history":
    show_header("history") # Panggil header dengan page aktif
    st.markdown(f"<div class='{fade_class}'>", unsafe_allow_html=True)
    st.subheader("🧾 History")
    st.write("Riwayat latihan kamu akan muncul di sini.")
    st.markdown("</div>", unsafe_allow_html=True)

# ABOUT PAGE
elif page == "about":
    show_header("about") # Panggil header dengan page aktif
    st.markdown(f"<div class='{fade_class}'>", unsafe_allow_html=True)
    st.subheader("⚙️ About This App")
    st.markdown("""
    <div style='font-size:16px; line-height:1.7;'>
    Hai! 👋 <br>
    Aku <b>XXX</b>, pengembang dari aplikasi <b>Exercise Recommendation App</b>.  
    Aplikasi ini dibuat buat bantu pengguna dapetin rekomendasi latihan 
    berdasarkan kebutuhan dan preferensi mereka.  
    Tujuannya? Biar lo bisa jaga kebugaran, dapet hasil maksimal, dan tetep termotivasi olahraga 💪  
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGE "LOGIN" DAN "SIGNUP" YANG LAMA DIHAPUS ---