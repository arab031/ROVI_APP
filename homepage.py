import streamlit as st
import pandas as pd
import altair as alt
from db import get_connection
from streamlit_option_menu import option_menu
from upload import Upload_page
from about import About_page
from settings import settings_page
from visualization import data_visualization_page
from folium import Map, CircleMarker
from streamlit_folium import folium_static
from folium.plugins import MiniMap

def home_page():
    st.markdown("""
        <style>
            .metric-card {
                background-color: var(--secondary-background, #2c2c2c);
                padding: 12px;
                border-radius: 10px;
                color: var(--text-color, #ffffff);
                border: 1px solid var(--primary-color, #888);
                text-align: center;
                height: 200px;
                width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                transition: all 0.3s ease;
            }
            .metric-card:hover {
                background-color: var(--background-color, #1a1a1a);
                transform: translateY(-3px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            .section-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
                color: var(--text-color, #ffffff);
            }
            .section-wrapper {
                border: 1px solid var(--primary-color, #888);
                border-radius: 12px;
                padding: 16px;
                margin-top: 24px;
                background-color: var(--secondary-background, #2c2c2c);
            }
            @media (prefers-color-scheme: dark) {
                .metric-card {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border-color: #333333;
                }
                .metric-card:hover {
                    background-color: #292929;
                }
                .section-title {
                    color: #FFCC00;
                }
                .section-wrapper {
                    background-color: #121212;
                    border-color: #333333;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color: var(--text-color);'>Dashboard</h2>", unsafe_allow_html=True)

    st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">System Database Status</div>', unsafe_allow_html=True)

    try:
        conn = get_connection()
        conn_status = True
        conn_status_text = "<h2 style='color:lightgreen'>Online</h2>"
    except:
        conn_status = False
        conn_status_text = "<h2 style='color:red'>Offline</h2>"

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(f"<div class='metric-card'><h4>Database Connection</h4>{conn_status_text}</div>", unsafe_allow_html=True)

    with colB:
        if conn_status:
            df_logs = pd.read_sql("SELECT timestamp FROM road_data", conn)
            df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"], errors="coerce")
            recent_count = df_logs[df_logs["timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=1)].shape[0]
            st.markdown(f"<div class='metric-card'><h4>Recent Uploads (24h)</h4><h2>{recent_count}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-card'><h4>Recent Uploads (24h)</h4><h2>—</h2></div>", unsafe_allow_html=True)

    with colC:
        if conn_status and not df_logs.empty:
            df_logs = df_logs.dropna()
            df_logs["upload_hour"] = df_logs["timestamp"].dt.floor("H")
            df_plot = df_logs.groupby("upload_hour").size().reset_index(name="uploads")

            chart = (
                alt.Chart(df_plot)
                .mark_bar(size=8, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("upload_hour:T", title="Upload Hour", axis=alt.Axis(format="%H:%M", labelAngle=0)),
                    y=alt.Y("uploads:Q", title="Count")
                )
                .properties(height=200, width=200, title="Upload Activity by Hour")
            )

            st.altair_chart(chart, use_container_width=False)
        else:
            st.markdown(f"<div class='metric-card'><h4>Upload Activity</h4><h2>—</h2></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if not conn_status:
        return

    df = pd.read_sql("SELECT * FROM road_data", conn)
    conn.close()

    st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Key Metrics Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_roads = df['road_id'].nunique()
        st.markdown(f"<div class='metric-card'><h4>Total Roads</h4><h2>{total_roads}</h2></div>", unsafe_allow_html=True)

    with col2:
        condition_counts = df['road_condition'].value_counts(normalize=True) * 100
        good = condition_counts.get('Good', 0)
        bad = condition_counts.get('Bad', 0)
        st.markdown(f"<div class='metric-card'><h4>Condition</h4><p>Good: {good:.1f}%<br>Bad: {bad:.1f}%</p></div>", unsafe_allow_html=True)

    with col3:
        avg_iri = df['iri'].mean() if 'iri' in df.columns else df['speedkmh'].mean()
        st.markdown(f"<div class='metric-card'><h4>Average IRI</h4><h2>{avg_iri:.2f}</h2></div>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"<div class='metric-card'><h4>Maintenance</h4><p>Planned</p></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Road Specific Metrics</div>', unsafe_allow_html=True)

    col0, col5, col6, col7, col8 = st.columns([1, 2, 2, 2, 2])

    selection_type = col0.radio("Group by", ["Project Name", "File Name"], index=0, key="select_group")

    if selection_type == "File Name":
        selector_values = df['file_name'].dropna().unique().tolist()
        selected_value = col5.selectbox("Select File", selector_values, key="file_selector")
        road_df = df[df['file_name'] == selected_value]
    else:
        selector_values = df['project_name'].dropna().unique().tolist()
        selected_value = col5.selectbox("Select Project", selector_values, key="project_selector")
        road_df = df[df['project_name'] == selected_value]

    with col6:
        road_iri = road_df['iri'].mean() if 'iri' in road_df else road_df['speedkmh'].mean()
        st.markdown(f"<div class='metric-card'><h4>Avg IRI</h4><h2>{road_iri:.2f}</h2></div>", unsafe_allow_html=True)

    with col7:
        rc = road_df['road_condition'].mode()
        condition = rc.iloc[0] if not rc.empty else "Unknown"
        st.markdown(f"<div class='metric-card'><h4>Condition</h4><p>{condition}</p></div>", unsafe_allow_html=True)

    with col8:
        length = road_df.get('length', pd.Series([0])).iloc[0]
        width = road_df.get('width', pd.Series([0])).iloc[0]
        st.markdown(f"<div class='metric-card'><h4>Details</h4><p>Length: {length}m<br>Width: {width}m</p></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Quick Map Preview</div>', unsafe_allow_html=True)

    m = Map(location=[6.6885, -1.6244], zoom_start=13, tiles="OpenStreetMap")
    MiniMap(position="bottomright").add_to(m)

    CircleMarker(
        location=[6.6885, -1.6244],
        radius=8,
        color="#FF6F61",
        fill=True,
        fill_opacity=0.9,
        popup="Sample Road Location",
        tooltip="IRI Point"
    ).add_to(m)

    folium_static(m, width=900, height=400)
    st.markdown("</div>", unsafe_allow_html=True)

def admin_dashboard():
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Upload Data", "Data Visualization", "Settings", "About"],
            icons=["house", "upload", "bar-chart", "gear", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

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
