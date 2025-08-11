import streamlit as st



def About_page():
    """About page to display app details."""
    st.title("About RoVi-App")
    st.markdown("---")
    st.markdown("""
    **RoVi-App** is a **road condition visualization web application** designed to:
    
    -Upload and process road condition data**  
    -Visualize IRI and road conditions using interactive maps**  
    -Analyze accelerometer and gyroscope data**  
    -Enable administrators to manage and track road maintenance data efficiently**  

   Developed by: Julian and Abdul-Rahman  
   Database: PostgreSQL + PostGIS  
   Frontend: Streamlit  
   Backend: Python  
    """)