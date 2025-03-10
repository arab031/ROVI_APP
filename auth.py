import streamlit as st
import hashlib
from db import get_connection

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up(username, password):
    """Register a new user in the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s;", (username,))
        if cur.fetchone():
            st.error("Username already exists. Please choose a different one.")
            return False
        hashed_password = hash_password(password)
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, hashed_password))
        conn.commit()
        conn.close()
        st.success("Sign-up successful! You can now log in.")
        return True
    except Exception as e:
        st.error(f"Error during sign-up: {e}")
        return False

def authenticate(username, password):
    """Authenticate user against database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s;", (username,))
        result = cur.fetchone()
        conn.close()
        return result and result[0] == hash_password(password)
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

def login_signup():
    """Login and signup page."""
    st.title("Login / Sign Up")
    action = st.radio("Choose an action:", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if action == "Login":
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.session_state["role"] = "admin"
                st.session_state["page"] = "admin_dashboard"
                st.success("Login successful!")
            else:
                st.error("Invalid credentials")
    elif action == "Sign Up":
        if st.button("Sign Up"):
            if sign_up(username, password):
                st.session_state["authenticated"] = True
                st.session_state["role"] = "user"
                st.session_state["page"] = "admin_dashboard"