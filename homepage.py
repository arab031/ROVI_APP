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
                padding: 12px;
                border-radius: 10px;
                border: 1px solid;
                text-align: center;
                height: 200px;
                width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                transition: all 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            .section-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
            }
            .section-wrapper {
                border: 1px solid;
                border-radius: 12px;
                padding: 2px;
                margin-top: 14px;
                width: 98%;
                margin-left: auto;
                margin-right: auto;
                height: 1px
            }
            @media (prefers-color-scheme: dark) {
                .metric-card {}
                .metric-card:hover {}
                .section-title {}
                .section-wrapper {}
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color: var(--text-color);'>Dashboard</h2>", unsafe_allow_html=True)

    # SECTION: System Database Status
    st.markdown("---------------------------------------", unsafe_allow_html=True)
    st.markdown('<div class="section-title">System Database Status</div>', unsafe_allow_html=True)

    try:
        conn = get_connection()
        conn_status = True
        conn_status_text = "<h2 style='color:lightgreen'>Online</h2>"
    except:
        conn_status = False
        conn_status_text = "<h2 style='color:red'>Offline</h2>"

    st.markdown("<div>", unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(f"<div class='metric-card'><h4>Database Connection</h4>{conn_status_text}</div>", unsafe_allow_html=True)

    with colB:
        if conn_status:
            df_logs = pd.read_sql("SELECT * FROM iri_data", conn)
            recent_count = len(df_logs)
            st.markdown(f"<div class='metric-card'><h4>Total Records</h4><h2>{recent_count}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-card'><h4>Total Records</h4><h2>—</h2></div>", unsafe_allow_html=True)

    with colC:
        if conn_status and not df_logs.empty:
            chart_data = df_logs[['iri']].dropna()
            chart_data['record_index'] = chart_data.index

            chart = (
                alt.Chart(chart_data)
                .mark_line()
                .encode(
                    x=alt.X("record_index", title="Record Index"),
                    y=alt.Y("iri", title="IRI Value")
                )
                .properties(height=200, width=200, title="IRI Trend")
            )

            st.altair_chart(chart, use_container_width=False)
        else:
            st.markdown(f"<div class='metric-card'><h4>IRI Trend</h4><h2>—</h2></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not conn_status:
        return

    df = pd.read_sql("SELECT * FROM iri_data", conn)
    conn.close()

    # SECTION: Key Metrics Overview
    st.markdown("---------------------------------------", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Key Metrics Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_iri = df['iri'].mean()
        st.markdown(f"<div class='metric-card'><h4>Average IRI</h4><h2>{avg_iri:.2f}</h2></div>", unsafe_allow_html=True)

    with col2:
        avg_speed = df['speed'].mean()
        st.markdown(f"<div class='metric-card'><h4>Average Speed</h4><h2>{avg_speed:.2f} km/h</h2></div>", unsafe_allow_html=True)

    with col3:
        total_distance = df['travel_distance'].sum()
        st.markdown(f"<div class='metric-card'><h4>Total Distance</h4><h2>{total_distance:.2f} m</h2></div>", unsafe_allow_html=True)

    with col4:
        avg_displacement = df['vert_displacement'].mean()
        st.markdown(f"<div class='metric-card'><h4>Avg Displacement</h4><h2>{avg_displacement:.2f} mm</h2></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # SECTION: Quick Map Preview
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
