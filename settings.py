import streamlit as st


def settings_page():
    """Settings page where users can configure app settings."""
    st.title("Settings")
    st.markdown("---")
    st.warning("This page will be used to configure app settings.")

    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["page"] = "login"  # Redirect to login page
        st.success("You have been logged out successfully.")