import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="ROADESSY: IRI Revolution",
    page_icon= "./icon1.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)


from homepage import admin_dashboard
from upload import Upload_page
from visualization import data_visualization_page
from settings import settings_page
from about import About_page
from auth import login_signup

def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state.get("run_dashboard"):
        st.session_state["page"] = "admin_dashboard"
        st.session_state["run_dashboard"] = False

    valid_pages = {
        "login": login_signup,
        "admin_dashboard": admin_dashboard,
        "Upload Data": Upload_page,
        "Data Visualization": data_visualization_page,
        "Settings": settings_page,
        "About": About_page,
    }

    current = st.session_state["page"]
    if current in valid_pages:
        valid_pages[current]()
    else:
        login_signup()

if __name__ == "__main__":
    main()
