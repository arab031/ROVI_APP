import streamlit as st
import pandas as pd
import numpy as np
import io
from db import get_connection

def check_file_exists(file_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM road_data WHERE file_name = %s;", (file_name,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count > 0

def upload_csv_to_db(uploaded_file):
    if uploaded_file is not None:
        file_name = uploaded_file.name
        st.success(f"File '{file_name}' uploaded successfully! Processing...")

        try:
            conn = get_connection()
            cur = conn.cursor()

            if check_file_exists(file_name):
                st.warning(f"⚠️ A file named '{file_name}' already exists in the database!")
                action = st.radio("Choose an action:", ["Override", "Rename File"])
                if action == "Override":
                    cur.execute("DELETE FROM road_data WHERE file_name = %s;", (file_name,))
                    conn.commit()
                    st.success("✅ Previous data overridden successfully.")
                elif action == "Rename File":
                    new_file_name = st.text_input("Enter a new file name:")
                    if new_file_name:
                        file_name = new_file_name

            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
            df["file_name"] = file_name

            st.write("🔍 **Preview of Uploaded Data:**")
            st.dataframe(df.head())

            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'road_data' AND column_name != 'id';
            """)
            db_columns = [row[0].lower() for row in cur.fetchall()]
            matching_columns = [col for col in df.columns if col in db_columns]

            if not matching_columns:
                st.error("❌ No matching columns found. Please check your CSV headers.")
                return

            output = io.StringIO()
            df[matching_columns].to_csv(output, index=False, header=False)
            output.seek(0)

            copy_command = f"""
            COPY road_data ({', '.join(matching_columns)}) FROM STDIN WITH CSV;
            """
            cur.copy_expert(copy_command, output)
            conn.commit()

            st.success("✅ Data uploaded and inserted into database successfully!")

            st.session_state['last_uploaded_file'] = file_name

            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ Error inserting data: {e}")

def Upload_page():
    st.title("Upload & Compute Road Data")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload CSV")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            upload_csv_to_db(uploaded_file)

    with col2:
        st.subheader("IRI & Condition Computation")

        if 'last_uploaded_file' in st.session_state:
            file_name = st.session_state['last_uploaded_file']

            try:
                conn = get_connection()
                df = pd.read_sql("SELECT * FROM road_data WHERE file_name = %s", conn, params=(file_name,))
                conn.close()

                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.sort_values(by='timestamp').reset_index(drop=True)

                df['prev_lat'] = df['latitude'].shift().astype(float)
                df['prev_lon'] = df['longitude'].shift().astype(float)
                df['lat'] = df['latitude'].astype(float)
                df['lon'] = df['longitude'].astype(float)
                df['delta_t'] = df['timestamp'].diff().dt.total_seconds().fillna(0)

                def haversine(lat1, lon1, lat2, lon2):
                    R = 6371000
                    phi1, phi2 = np.radians(lat1), np.radians(lat2)
                    dphi = np.radians(lat2 - lat1)
                    dlambda = np.radians(lon2 - lon1)
                    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
                    return 2 * R * np.arcsin(np.sqrt(a))

                df['distance'] = haversine(df['prev_lat'], df['prev_lon'], df['lat'], df['lon']).fillna(0)
                df['a_v'] = np.sqrt(df['accelx']**2 + df['accely']**2 + df['accelz']**2)
                df['iri'] = (np.abs(df['a_v']) * (df['delta_t'] ** 2)) / df['distance'].replace(0, np.nan)

                def classify_iri(val):
                    if np.isnan(val): return "Unknown"
                    elif val < 2: return "Good"
                    elif val < 4: return "Fair"
                    else: return "Poor"

                df['road_condition'] = df['iri'].apply(classify_iri)

                st.dataframe(df[['timestamp', 'latitude', 'longitude', 'iri', 'road_condition']].dropna())

                if st.button("Update IRI and Condition in Database"):
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        for _, row in df.iterrows():
                            cur.execute("""
                                UPDATE road_data
                                SET iri = %s, road_condition = %s
                                WHERE file_name = %s AND timestamp = %s
                            """, (row['iri'], row['road_condition'], file_name, row['timestamp']))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ IRI and condition updated successfully in the database.")
                    except Exception as e:
                        st.error(f"❌ Database update failed: {e}")

            except Exception as e:
                st.error(f"❌ Computation error: {e}")
        else:
            st.info("Upload a file first to enable IRI computation.")