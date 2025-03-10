import streamlit as st
import pandas as pd
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
            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ Error inserting data: {e}")

def Upload_page():
    st.title("Upload Your Data")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        upload_csv_to_db(uploaded_file)