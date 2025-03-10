import streamlit as st
from auth import login_signup
from homepage import admin_dashboard
from upload import Upload_page
from visualization import data_visualization_page
from settings import settings_page
from about import About_page

st.set_page_config(page_title="RoVi-App", layout="wide", initial_sidebar_state="expanded")

def main():
    # Load stored session state from query parameters
    query_params = st.query_params

    # If session state is missing, restore it from URL params
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = query_params.get("authenticated", "False") == "True"
    if "page" not in st.session_state:
        st.session_state["page"] = query_params.get("page", "login")

    # Ensure valid page selection
    valid_pages = {
        "admin_dashboard": admin_dashboard,
        "Upload Data": Upload_page,
        "Data Visualization": data_visualization_page,
        "Settings": settings_page,
        "About": About_page
    }

    if not st.session_state["authenticated"]:
        login_signup()
    else:
        if st.session_state["page"] not in valid_pages:
            st.session_state["page"] = "admin_dashboard"

        # Store session state in URL
        st.query_params["authenticated"] = str(st.session_state["authenticated"])
        st.query_params["page"] = st.session_state["page"]

        # Call the selected page
        valid_pages[st.session_state["page"]]()

if __name__ == "__main__":
    main()