# pages/1_Recommendation.py

import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from PIL import Image, ImageOps
from streamlit_option_menu import option_menu
import pandas as pd
import joblib
import re
import warnings
import os
import numpy as np
import requests
from io import BytesIO
import base64
import time
import urllib.parse
import json
import streamlit as st
from navigation import make_sidebar, hide_default_sidebar
import plotly.express as px

st.set_page_config(page_title="Recommendation", page_icon="📋", layout="wide")

hide_default_sidebar()

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
            height: 45px; 
            padding: 8px 0 !important; 
            line-height: 1.5; 
        }

        
        [data-testid="stSidebar"] .stButton button:hover {
            background: var(--dark-purple-hover); 
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }

        /* Kustomisasi Tombol Primary & Secondary */

        
        [data-testid="stButton"] button[kind="primary"] {
            background-color: #FF69B4; 
            color: white;
            border: 1px solid #FF69B4;
        }

        [data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #D65A98; 
            border: 1px solid #D65A98;
            color: white; 
        }

        [data-testid="stButton"] button[kind="primary"]:focus {
            box-shadow: 0 0 0 0.2rem rgba(255, 105, 180, 0.5); 
        }

        
        .main [data-testid="stButton"] button[kind="secondary"] {
            background-color: var(--cream-bg-dark); 
            color: var(--dark-text); 
            border: 1px solid #DCDCDC; 
        }
        .main [data-testid="stButton"] button[kind="secondary"]:hover {
            background-color: var(--hover-cream); 
            border: 1px solid #C0C0C0;
            color: var(--dark-text);
        }
        .main [data-testid="stButton"] button[kind="secondary"]:focus {
            box-shadow: 0 0 0 0.2rem rgba(224, 223, 217, 0.5); 
        }
        .main [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: var(--dark-purple-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)


# untuk path root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FOLDER = os.path.join(ROOT_DIR, "data")
USER_DATA_FILE = os.path.join(DATA_FOLDER, "user_data.json")
MODELS_FOLDER = os.path.join(ROOT_DIR, "models")


os.makedirs(DATA_FOLDER, exist_ok=True)


# Utility: load / save user data (saved_recommendations & favorites)

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as f:
                data = json.load(f)
            
            if "saved_recommendations" not in st.session_state:
                st.session_state["saved_recommendations"] = data.get("saved_recommendations", {})
            if "favorites" not in st.session_state:
                st.session_state["favorites"] = data.get("favorites", {})
        except Exception as e:
            print("Error loading user data:", e)
            st.session_state.setdefault("saved_recommendations", {})
            st.session_state.setdefault("favorites", {})
    else:
        st.session_state.setdefault("saved_recommendations", {})
        st.session_state.setdefault("favorites", {})

def save_user_data():
    data = {
        "saved_recommendations": st.session_state.get("saved_recommendations", {}),
        "favorites": st.session_state.get("favorites", {})
    }
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving user data:", e)


load_user_data()


# Imports model & helpers 

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from media import get_media_dict
    from media_info import get_media_info
except Exception as e:
    print("Warning: media import gagal:", e)
    def get_media_dict(): return {}
    def get_media_info(): return {}



# fungsi load model/aset   
def load_all_models():
    try:
        assets = {}
        assets["knn"] = joblib.load(os.path.join(MODELS_FOLDER, "knn_model.pkl"))
        assets["le_dict"] = joblib.load(os.path.join(MODELS_FOLDER, "label_encoders.pkl"))
        assets["le_target"] = joblib.load(os.path.join(MODELS_FOLDER, "target_encoder.pkl"))
        assets["scaler"] = joblib.load(os.path.join(MODELS_FOLDER, "scaler.pkl"))
        assets["preparation"] = joblib.load(os.path.join(MODELS_FOLDER, "preparation_data.pkl"))
        assets["tf"] = joblib.load(os.path.join(MODELS_FOLDER, "tfidf_vectorizer.pkl"))
        assets["media_dict"] = get_media_dict()
        assets["media_info"] = get_media_info()
        return assets
    except FileNotFoundError as e:
        st.error(f"ERROR: File model tidak ditemukan ({e}). Pastikan semua file .pkl ada di folder '{MODELS_FOLDER}'.")
        st.stop()
    except Exception as e:
        st.error(f"Error saat memuat model/aset: {e}")
        st.stop()

# fungsi bantu (BMI, dll) 
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

# model inference functions   
categorical_cols = ['Sex', 'Level', 'Fitness Goal']
numeric_cols = ['Age', 'Height', 'Weight', 'BMI']

def knn_predict_fitness(user_input_dict, le_dict, scaler, knn_model, le_target):
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

from sklearn.metrics.pairwise import cosine_similarity

def cbf_recommendations(fitness_type, hypertension, diabetes, preparation_data, tfidf_vectorizer, top_n=5):
    hypertension_clean = str(hypertension).strip().title()
    diabetes_clean = str(diabetes).strip().title()

    filtered_df = preparation_data[
        (preparation_data['Fitness Type'] == fitness_type) & 
        (preparation_data['Hypertension'].str.strip().str.title() == hypertension_clean) &
        (preparation_data['Diabetes'].str.strip().str.title() == diabetes_clean)
    ].copy()

    if filtered_df.empty:
        filtered_df = preparation_data[preparation_data['Fitness Type'] == fitness_type].copy()
        if filtered_df.empty: return {"Error": f"Tidak ada data untuk Tipe Fitness: {fitness_type}."}

    current_top_n = min(top_n, len(filtered_df))
    if current_top_n == 0: return {"Error": "Tidak ada data cocok sama sekali."}

    if 'content' not in filtered_df.columns:
        filtered_df['content'] = (
            filtered_df['Exercises'].fillna('') + ' ' +
            filtered_df['Equipment'].fillna('') + ' ' +
            filtered_df['Diet'].fillna('')
        ).str.strip()

    filtered_content = filtered_df['content'].fillna('')
    try:
        tfidf_matrix_filtered = tfidf_vectorizer.transform(filtered_content)
    except Exception as tf_err:
        return {"Error": f"Gagal transform TF-IDF: {tf_err}"}

    try:
        if tfidf_matrix_filtered.shape[0] > 1:
            cosine_sim_filtered = cosine_similarity(tfidf_matrix_filtered)
        else:
            cosine_sim_filtered = np.array([[1.0]])
    except Exception as cs_err:
        return {"Error": f"Gagal hitung Cosine Sim: {cs_err}"}

    avg_sim_scores = cosine_sim_filtered.mean(axis=1)
    sim_scores_series = pd.Series(avg_sim_scores, index=filtered_df.index)
    top_n_indices = sim_scores_series.nlargest(current_top_n).index.tolist()

    topN_df = preparation_data.loc[top_n_indices]

    try:
        final_exercise = topN_df['Exercises'].mode()[0]
        final_equipment = topN_df['Equipment'].mode()[0]
        final_diet = topN_df['Diet'].mode()[0]
    except Exception as e: return {"Error": f"Gagal voting: {e}"}

    return {'Exercises': final_exercise, 'Equipment': final_equipment, 'Diet': final_diet}

# Helpers tampilan & media 
def img_to_base64(path_or_url, size=(250,180)):
    try:
        if isinstance(path_or_url, str) and path_or_url.startswith("http"):
            img = Image.open(BytesIO(requests.get(path_or_url).content))
        else:
            img = Image.open(path_or_url)
        img = img.convert("RGB").resize(size)
        img = ImageOps.expand(img, border=2, fill="#e6e6e6")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"Error img_to_base64 ({path_or_url}): {e}")
        return None

def clean_items(text):
    if not isinstance(text, str): return []
    text = text.replace("(", "").replace(")", "").replace(";", "|")
    text = text.replace(" and ", "|").replace(" or ", "|").replace(",", "|")
    cleaned_list = [item.strip().title() for item in text.split('|') if item.strip() and item.strip().lower() not in ["and", "or"]]
    return list(dict.fromkeys(cleaned_list))

#  FUNGSI CALLBACK BARU 
def set_detail_view(item_key):
    """Callback untuk set item apa yang mau diliat detailnya"""
    st.session_state["selected_detail"] = item_key

def add_to_favorites(item):
    """Callback untuk toggle (tambah/hapus) item ke favorit"""
    username = st.session_state.get("username")
    if not username:
        st.toast("Login dulu buat nambahin favorit.", icon="⚠️")
        return

    # Inisialisasi data favorit kalo belum ada
    st.session_state.setdefault("favorites", {})
    st.session_state["favorites"].setdefault(username, [])
    
    # LOGIKA TOGGLE 
    if item in st.session_state["favorites"][username]:
        # Kalo udah ada: Hapus item
        st.session_state["favorites"][username].remove(item)
        save_user_data() 
        # Toast notif sesuai request
        st.toast(f"{item} dihapus dari favorit.", icon="🗑️") 
    else:
        # Kalo BELUM ADA: Tambah item
        st.session_state["favorites"][username].append(item)
        save_user_data() 
        # Toast notif sesuai request
        st.toast(f"{item} ditambahin ke favorit!", icon="💖")

#  END FUNGSI CALLBACK BARU 

def extract_diet_items(category_key, diet_string):
    if not isinstance(diet_string, str): return []
    match = re.search(fr'{category_key}:\s*\(([^)]*)\)', diet_string, re.IGNORECASE)
    if match:
        item_string = match.group(1)
        return clean_items(item_string)
    return []

#  FUNGSI CARD DIPERBARUI (TANPA <a> tag) 
def render_card_html(label, media_dictionary):
    """render tampilan card-nya, TANPA link."""
    if not label or not isinstance(label, str):
        return None
    key = label.lower().replace(" ", "_")
    img64 = None
    if key in media_dictionary:
        img64 = img_to_base64(media_dictionary[key])
    
    img_html = ""
    if img64:
        img_html = f'<img src="data:image/png;base64,{img64}" style="width:100%; max-width:240px; height:170px; border-radius:8px; display:block; margin:auto; object-fit: cover;">'
    else:
        # Kalo tidak ada gambar, kasih placeholder agar tingginya sama
        img_html = '<div style="width:100%; max-width:240px; height:170px; border-radius:8px; background:#f0f0f0; display:flex; align-items:center; justify-content:center; color:#999;">No Image</div>'

    html = f"""
    <div class="rec-card">
        {img_html}
        <p style="text-align:center; font-weight:bold; margin-top:6px; color:black;">{label}</p>
    </div>
    """
    return html

#  FUNGSI RENDER SECTION 

def render_recommendation_section(title, items_list, media_dictionary):
    st.subheader(title)
    if items_list and isinstance(items_list, list):
        cols = st.columns(2)
        for i, item in enumerate(items_list):
            with cols[i % 2]:
                if isinstance(item, str) and item:
                    # Render card statis
                    html = render_card_html(item, media_dictionary) 
                    if html:
                        st.markdown(html, unsafe_allow_html=True)
                    
                    key_safe = item.lower().replace(" ", "_")
                    
                    col_btn1, col_btn2 = st.columns([1, 1]) 

                    # Tombol Detail di kolom kiri
                    with col_btn1:
                        st.button(
                            "Lihat Detail", 
                            key=f"detail_btn_{key_safe}",
                            on_click=set_detail_view,     
                            args=(key_safe,),
                            use_container_width=True 
                        )
                    
                    # Tombol Favorit di kolom kanan
                    with col_btn2:
                        user_logged = st.session_state.get("authentication_status", False)
                        if user_logged:
                            username = st.session_state.get("username")
                            
                            # Cek status favoritnya
                            is_favorite = False
                            if username and item in st.session_state.get("favorites", {}).get(username, []):
                                is_favorite = True
                            
                            # Ganti teks tombol & style
                            button_text = "🗑️ Hapus" if is_favorite else "❤️ Favorit"
                            button_type = "primary" if is_favorite else "secondary" 

                            st.button(
                                button_text,
                                key=f"fav_btn_{key_safe}",
                                on_click=add_to_favorites,
                                args=(item,),
                                use_container_width=True,
                                type=button_type 
                            )
                        else:
                            st.markdown("<div style='text-align: center; padding-top: 5px; height: 38px;'><i style='color:#666; font-size: 0.9em;'>Login untuk ❤️</i></div>", unsafe_allow_html=True)
        st.write("") 
    else:
        st.info(f"Tidak ada rekomendasi spesifik untuk {title.split(':')[0]}.")



# CSS singkat

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display.swap');
        :root {
            /* Warna Gradasi Tema */
            --theme-blue: #6495ED; 
            --theme-purple: #9370DB; 
            --theme-pink: #FF69B4; 
            --theme-gradient: linear-gradient(to right, var(--theme-blue), var(--theme-purple), var(--theme-pink));
            }    
            .rec-card { 
            background: white; 
            border-radius: 12px; 
            padding: 8px; 
            box-shadow: 0 6px 18px rgba(12,12,30,0.06); 
            transition: all 0.2s ease-in-out;
            margin-bottom: 8px;
            height: 240px;
        }
        .rec-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(12,12,30,0.1); }
        .hero { 
            background: var(--theme-gradient); 
            color: white; 
            padding: 24px; 
            border-radius: 12px; 
            margin-bottom: 12px; 
            box-shadow: 0 6px 30px rgba(59,24,120,0.18);

        [data-testid="stSidebar"] {
            background-color: var(--cream-bg-dark); 
            border-right: 1px solid #DCDCDC; 
        }
            
        [data-testid="stSidebarNav"] {
            display: none !important;
        }       
            
        [data-testid="stSidebar"] .stSuccess {
             color: var(--dark-text); 
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
        }
    </style>
""", unsafe_allow_html=True)


# Authenticator & Sidebar  

CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")
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



# Main: load assets & render form / results

assets = load_all_models()
knn = assets["knn"]
le_dict = assets["le_dict"]
le_target = assets["le_target"]
scaler = assets["scaler"]
preparation = assets["preparation"]
tf = assets["tf"]
media_dict = assets["media_dict"]
media_info = assets["media_info"]


#  LOGIKA DETAIL PAGE 

# Detail page logic
if "selected_detail" in st.session_state:
    st.markdown("<h1 class='header-title'>Detail</h1>", unsafe_allow_html=True)
    item_key = st.session_state["selected_detail"] 

    item_title = item_key.replace("_", " ").title()
    st.subheader(item_title)
    info = media_info.get(item_key, {})
    image_path = media_dict.get(item_key)
    if image_path:
        try: st.image(image_path, width=500)
        except Exception as e: st.error(f"Gagal memuat gambar: {e}")
    if "description" in info:
        st.subheader("📝 Penjelasan Singkat")
        st.write(info["description"])
    if "tips" in info:
        st.subheader("💡 Tips & Cara Pemakaian")
        for tip in info["tips"]: st.write(f"- {tip}")
    if "kandungan" in info:
        st.subheader("🔬 Kandungan Baik")
        for k in info["kandungan"]: st.write(f"- {k}")
    if "youtube" in info:
        st.subheader("📺 Video Panduan")
        st.video(info["youtube"])
    if not info:
        st.info(f"Belum ada info detail untuk item: `{item_key}`")
    
    # Tombol kembali yang dimodifikasi
    if st.button("Kembali ke Rekomendasi"):
        st.session_state.pop("selected_detail", None) 
        st.rerun()
    st.stop() 


# Main recommendation form
st.markdown('<div class="hero"><h1>💪 Program Latihan & Asupan Khusus Buat Kamu</h1><p>Mulai lihat rekomendasi latihan, alat, dan asupan yang pas sesuai tujuanmu.</p></div>', unsafe_allow_html=True)
st.header("Masukkan Data untuk Mendapatkan Rekomendasi")

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

        if isinstance(pred_label, str) and pred_label.startswith("Error"):
            st.error(f"Prediksi KNN Gagal: {pred_label}")
        else:
            cbf_result = cbf_recommendations(
                fitness_type=pred_label,
                hypertension=hypertension,
                diabetes=diabetes,
                preparation_data=preparation,
                tfidf_vectorizer=tf,
                top_n=5
            )
            if "Error" in cbf_result:
                st.error(f"Rekomendasi CBF Gagal: {cbf_result['Error']}")
            else:
                # simpan ke session_state recommendation_data
                st.session_state["recommendation_data"] = {
                    "pred_label": pred_label,
                    "level": level,
                    "goal": goal,
                    "bmi": bmi,
                    "best_row": cbf_result,
                    "hypertension": hypertension,
                    "diabetes": diabetes,
                    "timestamp": time.time()
                }
                st.rerun()

# Render hasil rekomendasi

if st.session_state.get("recommendation_data"):
    data = st.session_state["recommendation_data"]
    best_row = data["best_row"]

    st.success(f"Rekomendasi tipe latihan: **{data['pred_label']}**", icon="✅")
    st.markdown(f"Status Anda: **{data['level']}** (BMI: `{data['bmi']:.2f}`), Dominasi tujuan yang direkomendasikan adalah **{data['goal']}**.")
    st.header("Rekomendasi Untuk Anda 👇")

    #  LOGIKA TOMBOL SIMPAN/HAPUS PROFIL 
    if st.session_state.get("authentication_status"):
        username = st.session_state.get("username")
        
        # Buat summary
        current_rec_timestamp = data.get("timestamp")
        rec_summary = {
            "timestamp": current_rec_timestamp,
            "pred_label": data.get("pred_label"),
            "level": data.get("level"),
            "goal": data.get("goal"),
            "bmi": data.get("bmi"),
            "best_row": data.get("best_row")
        }

        # Inisialisasi list favorit user
        st.session_state.setdefault("saved_recommendations", {})
        st.session_state["saved_recommendations"].setdefault(username, [])
        
        # Cek apakah rekomendasi ini (berdasarkan timestamp) sudah ada
        is_saved = False
        existing_recs = st.session_state["saved_recommendations"][username]
        for rec in existing_recs:
            if rec.get("timestamp") == current_rec_timestamp:
                is_saved = True
                break
        
        # Set teks & style tombol secara dinamis
        button_text = "🗑️ Hapus Rekomendasi dari Profil" if is_saved else "⭐ Simpan Rekomendasi ke Profil"
        button_type = "primary" if is_saved else "secondary"

        # Render tombol
        if st.button(button_text, type=button_type, use_container_width=False):
            # Logika Toggle
            if is_saved:
                # Hapus
                new_recs_list = [rec for rec in existing_recs if rec.get("timestamp") != current_rec_timestamp]
                st.session_state["saved_recommendations"][username] = new_recs_list
                save_user_data()
                st.toast("Rekomendasi dihapus dari profil.", icon="🗑️")
            else:
                st.session_state["saved_recommendations"][username].append(rec_summary)
                save_user_data()
                st.toast("Rekomendasi disimpan ke profil!", icon="💾")
            
            # Rerun agar teks tombolnya update
            st.rerun() 
            
    else:
        st.info("Login dulu biar bisa nyimpen rekomendasi ya 😉")
        

     
    # 🏋️ Latihan
    exercise_list = clean_items(best_row.get("Exercises", ""))
    render_recommendation_section("🏋️ Latihan", exercise_list, media_dict)

     
    # 🧰 Alat
    equipment_list = clean_items(best_row.get("Equipment", ""))
    render_recommendation_section("🧰 Alat", equipment_list, media_dict)

     
    # 🥗 Pola Makan
     

    st.subheader("🥗 Pola Makan")

    # PIE CHART DENGAN 4 KATEGORI & CUSTOM HOVER 
    st.markdown("##### Panduan Porsi Ideal 'Isi Piringku' Per Satu Porsi")

    try:
        # Data berdasarkan 4 KATEGORI (Kemenkes) 
        data_porsi = {
            'Kategori': [
                'Mineral & Vitamin (Sayur)', 
                'Mineral & Vitamin (Buah)', 
                'Karbohidrat (Pokok)', 
                'Protein (Lauk Pauk)'
            ],
            'Persentase': [33.3, 16.7, 33.3, 16.7], 
            'Porsi': [
                '2/3 dari 1/2 Piring', # Porsi Sayur
                '1/3 dari 1/2 Piring', # Porsi Buah
                '2/3 dari 1/2 Piring', # Porsi Karbo
                '1/3 dari 1/2 Piring'  # Porsi Protein
            ]
        }
        df_porsi = pd.DataFrame(data_porsi)
        
        # Warna solid (4 Kategori) 
        colors = {
            'Mineral & Vitamin (Sayur)': "#6ADB6A", # Darker Green
            'Mineral & Vitamin (Buah)': "#D16DF8",  # Teal
            'Karbohidrat (Pokok)': "#1BC6F1",         # Gold
            'Protein (Lauk Pauk)': "#FFA844"          # Peach
        }

        fig = px.pie(df_porsi, 
                    values='Persentase', 
                    names='Kategori',
                    title='Visualisasi Porsi "Isi Piringku" per Satu Porsi',
                    color='Kategori', 
                    color_discrete_map=colors,
                    hole=0.4,
                    custom_data=['Porsi']  
                    )
        
        fig.update_traces(
            textinfo='none',
            hovertemplate="<b>%{label}</b><br>Porsi per Piring: %{customdata[0]}<extra></extra>",
            marker=dict(
                line=dict(color='#000000', width=1) 
            )
        )
        
        # Update layout: judul tengah, legend di bawah, background transparan
        fig.update_layout(
            title_x=0.30, # Judul di tengah
            legend=dict(
                orientation="h", # Horizontal legend
                yanchor="bottom",
                y=-0.2, 
                xanchor="center",
                x=0.5,
                traceorder='normal',
                font=dict(size=12, color='black')
            ),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',  
            margin=dict(t=50, b=100, l=0, r=0) 
        )
        
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Gagal memuat chart porsi: {e}")

    st.caption("""
    Sumber Panduan Gizi:
    - [Kemenkes: Isi Piringku](https://ayosehat.kemkes.go.id/isi-piringku-pedoman-makan-kekinian-orang-indonesia)
    - [UNICEF Indonesia: Panduan Gizi Seimbang](https://www.unicef.org/indonesia/id/media/19831/file)
    """)
    st.markdown("---")

    # Rekomendasi item diet berdasarkan kategori 
    raw_diet_string = best_row.get("Diet", "")
    if raw_diet_string:
        karbohidrat = extract_diet_items("Karbohidrat", raw_diet_string)
        mineral_serat = extract_diet_items("Mineral & Serat", raw_diet_string)
        protein = extract_diet_items("Protein", raw_diet_string)

        if karbohidrat:
            render_recommendation_section("🍚 Sumber Karbohidrat (3-4 porsi/hari):", karbohidrat, media_dict)
        if mineral_serat:
            render_recommendation_section("🥦 Sumber Mineral & Vitamin (Sayur 3-4 porsi/hari || Buah 2-3 porsi/hari):", mineral_serat, media_dict)
        if protein:
            render_recommendation_section("🍗 Sumber Protein (Total 2-4 porsi/hari):", protein, media_dict)

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
        st.session_state.pop("selected_detail", None)
        st.rerun()
else:
    st.info("👈 Silakan isi data Anda di atas, lalu klik tombol **'Dapatkan Rekomendasi'** untuk melihat saran latihan, alat, dan asupan yang cocok untuk Anda!")


st.markdown("---")
st.caption("⚠️ Perhatian: Rekomendasi ini bersifat umum. Untuk kondisi kesehatan spesifik, konsultasikan dengan dokter atau pelatih profesional.")