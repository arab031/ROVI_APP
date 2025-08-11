import streamlit as st
import numpy as np
import pandas as pd
import psycopg2
from db import get_connection, generate_iri_segments

def Upload_page():
    st.title("Upload IRI Data")
    st.write("Upload CSV files containing IRI readings and related metrics.")

    left_col, right_col = st.columns(2)

    if "final_file_label" not in st.session_state:
        st.session_state.final_file_label = ""

    with left_col:
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        initial_file_label = st.text_input("Enter a name for this file:", value=st.session_state.final_file_label, key="file_label")

        if "project_name_value" not in st.session_state:
            st.session_state.project_name_value = ""
        project_name_input = st.text_input("Enter project name:", value=st.session_state.project_name_value, key="project_name")
        st.session_state.project_name_value = project_name_input
        project_name = project_name_input

        df = None
        reset_triggered = False
        if 'reset_triggered' in st.session_state and st.session_state.reset_triggered:
            reset_triggered = True
            st.session_state.reset_triggered = False

        if uploaded_file is not None and not reset_triggered:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip().str.lower()
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())

            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT EXISTS (SELECT 1 FROM iri_data WHERE file_name = %s)", (initial_file_label,))
                exists = cur.fetchone()[0]
                cur.close()
                conn.close()

                if exists and st.session_state.final_file_label != initial_file_label:
                    st.warning("A file with this name already exists in the database.")
                    new_file_label = st.text_input("Rename the file to proceed:", key="rename_field")
                    if st.button("Confirm New Name") and new_file_label:
                        st.session_state.final_file_label = new_file_label
                        st.rerun()
                    st.stop()
                else:
                    st.session_state.final_file_label = initial_file_label

            except Exception as e:
                st.error(f"Error checking existing file: {e}")

            if st.button("Upload to Database"):
                if not st.session_state.final_file_label:
                    st.warning("Please enter a name for the file before uploading.")
                elif not project_name:
                    st.warning("Please enter the project name before uploading.")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        for _, row in df.iterrows():
                            cur.execute("""
                                INSERT INTO iri_data (
                                    iri, speed, vert_displacement, travel_distance,
                                    latitude, longitude, time, road_condition,
                                    file_name, project_name
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                float(row['iri']),
                                float(row['speed']),
                                float(row['vert_displacement']),
                                float(row['travel_distance']),
                                float(row['latitude']),
                                float(row['longitude']),
                                float(row['time']),
                                str(row['road condition']),
                                st.session_state.final_file_label,
                                project_name
                            ))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("Upload successful!")

                        with st.spinner("Generating IRI segments..."):
                            generate_iri_segments()
                        st.success("IRI segments have been generated and inserted.")

                    except Exception as e:
                        st.error(f"Error uploading data: {e}")

    with right_col:
        st.subheader("Recent Uploads")
        try:
            conn = get_connection()
            df_logs = pd.read_sql("""
                SELECT file_name, project_name, MAX(upload_time) AS upload_time, COUNT(*) AS row_count
                FROM iri_data
                GROUP BY file_name, project_name
                ORDER BY upload_time DESC
                LIMIT 10
            """, conn)
            conn.close()
            df_logs.columns = [col.replace("_", " ").title() for col in df_logs.columns]
            st.dataframe(df_logs)
        except Exception as e:
            st.error(f"Could not fetch recent data: {e}")

        st.subheader("Summary of Uploaded File")
        if uploaded_file is not None and df is not None:
            try:
                st.write(f"Total Rows: {len(df)}")
                st.write(f"Average IRI: {df['iri'].mean():.2f}")
                st.write(f"Average Speed: {df['speed'].mean():.2f} km/h")
                st.write(f"Total Travel Distance: {df['travel_distance'].sum():.2f} km")
                st.write(f"Average Vertical Displacement: {df['vert_displacement'].mean():.2f} mm")
                if 'road condition' in df.columns:
                    condition_mode = df['road condition'].mode()
                    if not condition_mode.empty:
                        st.write(f"Most Common Road Condition: {condition_mode.iloc[0]}")
            except KeyError as e:
                st.warning(f"Missing expected column in uploaded CSV: {e}")
                st.write("Available columns:", list(df.columns))
        else:
            st.write("Total Rows: —")
            st.write("Average IRI: —")
            st.write("Average Speed: — km/h")
            st.write("Total Travel Distance: — km")
            st.write("Average Vertical Displacement: — mm")

        st.markdown("---")

        if st.button("Reset Upload Form"):
            keys_to_clear = ["file_label", "project_name", "rename_field", "final_file_label"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.project_name_value = ""
            st.session_state.reset_triggered = True
            st.rerun()

    # ================= ADMIN TOOLS SECTION =================
    st.markdown("---")
    st.subheader("Admin Tools (Database Manager)")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT file_name FROM iri_data ORDER BY file_name ASC;")
        all_files = [row[0] for row in cur.fetchall()]
        conn.close()

        selected_file = st.selectbox("Select a file to manage:", options=[""] + all_files, index=0)

        if selected_file:
            with st.expander(f"Preview: {selected_file}", expanded=False):
                try:
                    conn = get_connection()

                    df_data = pd.read_sql(f"""
                        SELECT * FROM iri_data WHERE file_name = %s;
                    """, conn, params=(selected_file,))

                    df_seg = pd.read_sql(f"""
                        SELECT * FROM iri_segments WHERE file_name = %s;
                    """, conn, params=(selected_file,))
                    conn.close()

                    st.write(f"**IRI Data Records** ({len(df_data)} rows)")
                    st.dataframe(df_data.head())

                    st.write(f"**IRI Segments** ({len(df_seg)} rows)")
                    st.dataframe(df_seg.head())

                except Exception as e:
                    st.error(f"Failed to preview file: {e}")

            st.warning("This action will backup the data and remove the original entries from `iri_data` and `iri_segments`.")

            if st.button(f"Delete File and Related Segments: {selected_file}"):
                try:
                    conn = get_connection()
                    cur = conn.cursor()

                    # Step 1: Backup iri_data
                    cur.execute("""
                        INSERT INTO iri_data_deleted SELECT * FROM iri_data WHERE file_name = %s;
                    """, (selected_file,))
                    # Step 2: Backup iri_segments
                    cur.execute("""
                        INSERT INTO iri_segments_deleted SELECT * FROM iri_segments WHERE file_name = %s;
                    """, (selected_file,))
                    # Step 3: Delete from original tables
                    cur.execute("DELETE FROM iri_data WHERE file_name = %s;", (selected_file,))
                    cur.execute("DELETE FROM iri_segments WHERE file_name = %s;", (selected_file,))

                    conn.commit()
                    conn.close()

                    st.success(f"Data for '{selected_file}' has been backed up and deleted.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to delete data: {e}")

    except Exception as e:
        st.error(f"Admin Tools initialization failed: {e}")
