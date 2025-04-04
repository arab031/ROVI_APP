import streamlit as st
from db import check_database_status
from upload import Upload_page
from about import About_page
from settings import settings_page
from visualization import data_visualization_page
import pandas as pd
import plotly.express as px
from db import check_database_status, get_unique_locations_per_file
from streamlit_option_menu import option_menu 




# ----------------------
# Home Page Function
# ----------------------
def home_page():
    # Welcome Section (Hero)
    st.markdown("""
        <div style='background-color: #FF4B4B; padding: 40px; border-radius: 15px; text-align: center;'>
            <h1 style='color: white;'>Welcome to the Roadessy Visualization WebApp</h1>
            <p style='color: white; font-size: 20px;'>Analyze and visualize road data effectively.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Check and display database connection status
    st.markdown("### **Database Connection Status**")
    db_status, status_color = check_database_status()
    st.markdown(f"### **{db_status}**")
    st.markdown("---")

    # -------------------------
    # Dividing the space into three columns using st.columns()
    # -------------------------
    col1, col2, col3 = st.columns(3)

    # First column - add content or metrics related to the first column here
    with col1:
        pass  # Placeholder for the first column

    # Second column - add content or metrics related to the second column here
    with col2:
        pass  # Placeholder for the second column

    # Third column - add content or metrics related to the third column here
    with col3:
        pass  # Placeholder for the third column

    # -------------------------
    # End of column layout
    # -------------------------


# ----------------------
# Admin Dashboard
# ----------------------
def admin_dashboard():
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",  # Sidebar Title
            options=["Home", "Upload Data", "Data Visualization", "Settings", "About"],  # Menu Items
            icons=["house", "upload", "bar-chart", "gear", "info-circle"],  # Icons for Each Item
            menu_icon="cast",  # Sidebar Icon
            default_index=0,  # Default Selection
        )

    # Call the corresponding page function based on selection
    if selected == "Home":
        home_page()
    elif selected == "Upload Data":
        Upload_page()
    elif selected == "Data Visualization":
        data_visualization_page()
    elif selected == "Settings":
        settings_page()
    elif selected == "About":
        About_page()