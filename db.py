import psycopg2
import pandas as pd
import streamlit as st

import plotly.express as px

def get_connection():
    return psycopg2.connect(
        dbname="ROVI_APP",
        user="postgres",
        password="aisha2468",
        host="localhost",
        port="5432"
    )

def check_database_status():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")  
        conn.close()

        # Create a two-column layout with the status on the left
        col1, col2 = st.columns([1, 3])

        with col1:
            # Display the success message in a card-like structure
            st.markdown(
                """
                <div style='padding: 15px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 10px; width: 100%;'>
                    <strong style='color: #155724;'>🟢 Database Connected</strong>
                </div>
                """, 
                unsafe_allow_html=True
            )
        return "🟢 Database Connected", "success"
        
    except Exception:
        # Create a two-column layout with the status on the left
        col1, col2 = st.columns([1, 3])

        with col1:
            # Display the error message in a card-like structure
            st.markdown(
                """
                <div style='padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 10px; width: 100%;'>
                    <strong style='color: #721c24;'>🔴 Database Disconnected</strong>
                </div>
                """, 
                unsafe_allow_html=True
            )
        return "🔴 Database Disconnected", "error"
        

    
# Database connection
def get_connection():
    return psycopg2.connect(
        dbname="ROVI_APP",
        user="postgres",
        password="aisha2468",
        host="localhost",
        port="5432"
    )

def get_total_uploads():
    """Fetch total number of uploaded files."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT file_name) FROM road_data;")
    total_files = cur.fetchone()[0]
    conn.close()
    return total_files

def get_recent_upload_count():
    """Fetch count of files uploaded in the last 7 days."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT file_name) FROM road_data WHERE upload_date >= NOW() - INTERVAL '7 days';")
    recent_files = cur.fetchone()[0]
    conn.close()
    return recent_files

def get_unique_locations_count():
    """Fetch count of unique locations from uploaded data."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM (SELECT DISTINCT latitude, longitude FROM road_data) AS unique_locations;")
    unique_locations = cur.fetchone()[0]
    conn.close()
    return unique_locations

def get_recent_uploads():
    """Fetch last 5 uploaded files."""
    conn = get_connection()
    query = "SELECT file_name, upload_date FROM road_data ORDER BY upload_date DESC LIMIT 5;"
    recent_uploads = pd.read_sql(query, conn)
    conn.close()
    return recent_uploads

def get_unique_locations_per_file():
    """Fetch the count of unique locations per file."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
        SELECT file_name, COUNT(DISTINCT (latitude || ',' || longitude)) AS unique_locations
        FROM road_data 
        GROUP BY file_name
        ORDER BY unique_locations DESC;
        """

        cur.execute(query)
        results = cur.fetchall()

        conn.close()

        return results  # Returns a list of tuples [(file1, count1), (file2, count2), ...]
    
    except Exception as e:
        print(f"Error fetching unique locations per file: {e}")
        return []