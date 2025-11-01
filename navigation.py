import streamlit as st
from time import sleep


# def make_sidebar(authenticator=None):
#     """Bikin sidebar navigasi custom (login-aware)."""
#     with st.sidebar:
#         # --- Header Sidebar ---
#         try:
#             st.image("logo.jpg", width=500)
#         except Exception:
#             st.title("🏋️ Exercise App")

#         st.markdown("## 🏋️ Exercise Recommendation App")
#         st.markdown("---")

#         # --- Kalau udah login ---
#         if st.session_state.get("authentication_status"):
#             st.markdown(
#                 f"""
#                 <div style='
#                     background-color: #dff0d8; 
#                     color: #2e7d32; 
#                     padding: 15px 20px; 
#                     border-radius: 10px; 
#                     font-size: 1.5rem; 
#                     font-weight: 100; 
#                     font-family: "Poppins", sans-serif;
#                     margin-bottom: 15px;
#                 '>
#                     Welcome, {st.session_state['name']} 👋
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )

#             st.page_link("home.py", label="🏠 Home")
#             st.page_link("pages/1_Recommendation.py", label="📋 Recommendation")
#             st.page_link("pages/2_Profile.py", label="👤 Profile")
#             st.page_link("pages/4_About.py", label="ℹ️ About")

#             st.markdown("---")

#             if authenticator:
#                 authenticator.logout("Logout", "sidebar")

#         # --- Kalau belum login ---
#         else:
#             st.info("Mode: 👤 Guest")
#             st.page_link("home.py", label="🏠 Home")
#             st.page_link("pages/1_Recommendation.py", label="📋 Recommendation")
#             st.page_link("pages/4_About.py", label="ℹ️ About")
#             st.warning("Silakan login untuk mengakses Profile.")

#             # Redirect manual kalau user buka halaman profile tanpa login
#             current_page = st.session_state.get("_current_page", "Home")
#             if current_page == "Profile":
#                 st.switch_page("home.py")

import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx

def make_sidebar(authenticator=None):
    with st.sidebar:
        try:
            st.image("logo.png", width=200)
        except Exception:
            st.title("🏋️ Exercise Recommendation App")

        st.markdown("## 🏋️ Exercise Recommendation App")
        st.markdown("---")

        # Kalau udah login
        if st.session_state.get("authentication_status"):
            st.markdown(
                f"<div style='font-size:1.3rem;font-weight:600;color:#4A2E7E;'>Halo, {st.session_state['name']} 👋</div>",
                unsafe_allow_html=True
            )

            st.page_link("Home.py", label="🏠 Home")
            st.page_link("pages/1_recommendation.py", label="📋 Recommendation")
            st.page_link("pages/2_profile.py", label="👤 Profile")
            st.page_link("pages/3_Works.py", label="✨ How it works")
            st.page_link("pages/4_About.py", label="ℹ️ About")

            st.markdown("---")
            if authenticator:
                authenticator.logout("Logout", "sidebar")

        # Kalau belum login
        else:
            st.info("Mode: 👤 Guest")
            st.page_link("Home.py", label="🏠 Home")
            st.page_link("pages/1_recommendation.py", label="📋 Recommendation")
            st.page_link("pages/3_Works.py", label="✨ How it works")
            st.page_link("pages/4_About.py", label="ℹ️ About")

            st.markdown("---")
            if st.button("🔐 Login / Sign Up"):
                st.switch_page("pages/login.py")

st.markdown("""
    <style>
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


def hide_default_sidebar():
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        [data-testid="stSidebarNavSeparator"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)



def logout():
    """Logout handler."""
    st.session_state["authentication_status"] = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("home.py")
