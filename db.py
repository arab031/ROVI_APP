import psycopg2
import pandas as pd
import streamlit as st
import plotly.express as px
from shapely.geometry import LineString
from math import radians, cos, sin, sqrt, atan2

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

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
                <div style='padding: 15px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 10px; width: 100%;'>
                    <strong style='color: #155724;'>🟢 Database Connected</strong>
                </div>
            """, unsafe_allow_html=True)
        return "🟢 Database Connected", "success"

    except Exception:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
                <div style='padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 10px; width: 100%;'>
                    <strong style='color: #721c24;'>🔴 Database Disconnected</strong>
                </div>
            """, unsafe_allow_html=True)
        return "🔴 Database Disconnected", "error"

def get_total_uploads():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT file_name) FROM road_data;")
    total_files = cur.fetchone()[0]
    conn.close()
    return total_files

def get_recent_upload_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT file_name) FROM road_data WHERE upload_date >= NOW() - INTERVAL '7 days';")
    recent_files = cur.fetchone()[0]
    conn.close()
    return recent_files

def get_unique_locations_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM (SELECT DISTINCT latitude, longitude FROM road_data) AS unique_locations;")
    unique_locations = cur.fetchone()[0]
    conn.close()
    return unique_locations

def get_recent_uploads():
    conn = get_connection()
    query = "SELECT file_name, upload_date FROM road_data ORDER BY upload_date DESC LIMIT 5;"
    recent_uploads = pd.read_sql(query, conn)
    conn.close()
    return recent_uploads

def get_unique_locations_per_file():
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
        return results
    except Exception as e:
        print(f"Error fetching unique locations per file: {e}")
        return []

# ========== Haversine Distance Function ==========

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ========== IRI SEGMENT GENERATION ==========

def iri_condition_by_speed(iri, speed):
    if iri is None or speed is None:
        return "Unknown"

    # Match the speed class from the IRI table
    if speed >= 110:
        thresholds = [0.95, 1.49, 1.89, 2.70]  # 120 km/h
    elif speed >= 90:
        thresholds = [1.14, 1.79, 2.27, 3.24]  # 100 km/h
    elif speed >= 75:
        thresholds = [1.43, 2.24, 2.84, 4.05]  # 80 km/h
    elif speed >= 65:
        thresholds = [1.63, 2.57, 3.25, 4.63]  # 70 km/h
    elif speed >= 55:
        thresholds = [1.90, 2.99, 3.79, 5.50]  # 60 km/h
    elif speed >= 45:
        thresholds = [2.28, 3.59, 4.54, 6.25]  # 50 km/h
    elif speed >= 35:
        thresholds = [2.86, 4.49, 5.69, 8.08]  # 40 km/h
    elif speed >= 25:
        thresholds = [3.80, 5.99, 7.59, 10.80]  # 30 km/h
    elif speed >= 15:
        thresholds = [5.72, 8.99, 11.39, 16.16]  # 20 km/h
    else:
        thresholds = [11.44, 17.99, 22.79, 32.32]  # 10 km/h

    # Compare IRI against thresholds for the matched speed
    if iri < thresholds[0]:
        return "Very Good"
    elif iri < thresholds[1]:
        return "Good"
    elif iri < thresholds[2]:
        return "Fair"
    elif iri < thresholds[3]:
        return "Mediocre"
    else:
        return "Poor"


def generate_iri_segments():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT latitude, longitude, iri, speed, file_name, project_name, time
        FROM iri_data
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND iri IS NOT NULL
        ORDER BY file_name, time;
    """)
    rows = cur.fetchall()

    segment_coords = []
    iri_values = []
    speed_values = []
    total_distance = 0.0
    current_file = None
    current_project = None

    for i in range(1, len(rows)):
        lat1, lon1, iri1, speed1, file1, project1, _ = rows[i - 1]
        lat2, lon2, iri2, speed2, file2, project2, _ = rows[i]

        # Always track current file/project
        current_file = file1
        current_project = project1

        # Reset accumulators if switching files
        if file1 != file2:
            segment_coords = []
            iri_values = []
            speed_values = []
            total_distance = 0.0

        d = haversine_distance(lat1, lon1, lat2, lon2)
        total_distance += d

        if not segment_coords:
            segment_coords.append((lon1, lat1))
            iri_values.append(iri1)
            speed_values.append(speed1)

        segment_coords.append((lon2, lat2))
        iri_values.append(iri2)
        speed_values.append(speed2)

        if total_distance >= 100:
            line = LineString(segment_coords)
            avg_iri = sum(iri_values) / len(iri_values)
            avg_speed = sum(speed_values) / len(speed_values)
            condition = iri_condition_by_speed(avg_iri, avg_speed)

            cur.execute("""
                INSERT INTO iri_segments (avg_iri, condition, geom, length_m, project_name, file_name, avg_speed)
                VALUES (%s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326), %s, %s, %s, %s);
            """, (avg_iri, condition, line.wkt, total_distance, current_project, current_file, avg_speed))

            # Reset for next segment
            segment_coords = []
            iri_values = []
            speed_values = []
            total_distance = 0.0

    conn.commit()
    conn.close()
    print("✅ IRI Segments generated with length_m, project_name, file_name, and avg_speed.")
