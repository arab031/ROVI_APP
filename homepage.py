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
    
    st.title("ROADESSY VISUALIZATION WEBAPP")
    st.markdown("---")

    # Check and display database connection status
    st.markdown("### **Database Connection Status**")
    db_status, status_color = check_database_status()
    st.markdown(f"### **{db_status}**")
    st.markdown("---")

    # Fetch unique locations per file
    unique_locations_data = get_unique_locations_per_file()

    if unique_locations_data:
        st.markdown("## 📌 Unique Locations Per File")
        
        # Convert results to DataFrame
        df_unique_locations = pd.DataFrame(unique_locations_data, columns=["File Name", "Unique Locations"])
        
        # Display Table with better styling
        st.dataframe(df_unique_locations.style.set_properties(
            **{"background-color": "#1E1E2F", "color": "white", "border-color": "#444"}), 
            use_container_width=True
        )

        # 📌 **Enhanced Bar Chart**
        fig = px.bar(df_unique_locations, x="File Name", y="Unique Locations",
                     title="📍 Unique Locations per Uploaded File",
                     labels={"Unique Locations": "Count", "File Name": "Uploaded File"},
                     color="Unique Locations",
                     color_continuous_scale="Plasma",
                     text="Unique Locations")  # Show count on bars

        # 🔹 **Chart Styling**
        fig.update_traces(
            marker=dict(line=dict(width=1.5, color="black")),  # Border for bars
            textposition="outside"  # Place text labels outside bars
        )
        fig.update_layout(
            plot_bgcolor="#1E1E2F",  
            paper_bgcolor="#1E1E2F",
            font_color="white",
            xaxis=dict(showgrid=False, tickangle=45),  
            yaxis=dict(showgrid=True, gridcolor="gray"),
            margin=dict(l=40, r=40, t=40, b=40)  # Reduce margin space
        )

        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No unique locations data available.")



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