import streamlit as st
import hashlib
from db import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_credentials(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s;", (username,))
        row = cur.fetchone()
        conn.close()
        return row and row[0] == hash_password(password)
    except Exception as e:
        st.error(f"Database error: {e}")
        return False


def register_user(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username = %s;", (username,))
        if cur.fetchone():
            st.error("Username already exists.")
            conn.close()
            return False
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s);",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False


def login_signup():
    st.markdown("""
        <style>
        * {
            margin: -1px;
            padding: 0px;
            align: center;}
                        
            .login-box h1 {
                font-size: 10000px;
                font-weight: bold;
                color: #FFCC00;
                margin-bottom: 10px;
            }
            .stTextInput, .stTextInput>div, .stTextInput>div>input,
            .stTextInput>div>div>input {
                width: 80%px !important;
                height: 70px !important;
                align: center !important;
                margin: 0 0 40px 0 !important;
                margin-right: -45px !important;
                padding: 30px
                background-color: transparent !important;
                color: #ffffff !important;
            }
            
            .stTextInput{
                padding-left: 2% !important;
            }
            
            .stPasswordInput input {
                width: 80% !important;
                height: 70px !important;
                margin: 0 0 60px 0 !important;
                padding: 20px
                background-color: blue !important;
                color: #ffffff !important;
                font-size: 16px !important;
            }

            .stButton > button {
                background: linear-gradient(90deg, #FF6F91, #FF9F1C) !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 15px !important;
                padding-left: 20px !important;
                width: 90px !important;
                font-weight: 1200 !important;
                margin-top: 5px !important;
            }

            .roadessy-title {
                font-size: 100px;
                font-weight: bold;
                color: #FFCC00;
                margin-top: 5px;
                text-align: left;
                position: left;
            }

            .stButton{
                padding-left: 50% !important;
            }

            .stTabs [data-baseweb="tab"] {
                font-weight: 1200px !important;
                font-size: 20px !important;
                padding: 20px 25% !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<h1 class="roadessy-title">ROADESSY</h1>', unsafe_allow_html=True)

    if "run_dashboard" not in st.session_state:
        st.session_state["run_dashboard"] = False

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            with st.spinner("Logging in..."):
                if check_credentials(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["page"] = "admin_dashboard"
                    st.session_state["run_dashboard"] = True
                else:
                    st.error("Invalid username or password.")

    with tab2:
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input("New Password", type="password", key="register_password")
        if st.button("Sign Up"):
            with st.spinner("Creating account..."):
                if not new_username or not new_password:
                    st.error("Username and password cannot be empty.")
                elif register_user(new_username, new_password):
                    st.session_state["authenticated"] = True
                    st.session_state["page"] = "admin_dashboard"
                    st.session_state["run_dashboard"] = True

    st.markdown('</div>', unsafe_allow_html=True)
