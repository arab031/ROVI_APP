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
import geopandas as gpd
from folium import Map, FeatureGroup, GeoJson, LayerControl, TileLayer
#from folium.plugins import MiniMap
from streamlit_folium import folium_static
from visualization import condition_color

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
        st.markdown(f"<div class='metric-card'><h4>Total Distance</h4><h2>{total_distance:.2f} km</h2></div>", unsafe_allow_html=True)

    with col4:
        avg_displacement = df['vert_displacement'].mean()
        st.markdown(f"<div class='metric-card'><h4>Avg Displacement</h4><h2>{avg_displacement:.2f} mm</h2></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # SECTION: Road-Specific Metrics
    st.markdown("---------------------------------------", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Road-Specific Metrics</div>', unsafe_allow_html=True)

    selection_option = st.radio("Filter by:", ["Project Name", "File Name"], horizontal=True)

    unique_values = df['project_name'].unique() if selection_option == "Project Name" else df['file_name'].unique()
    selected_value = st.selectbox(f"Select {selection_option}:", unique_values)

    if selected_value:
        filtered_df = df[df['project_name'] == selected_value] if selection_option == "Project Name" else df[df['file_name'] == selected_value]

        col5, col6, col7, col8 = st.columns(4)

        with col5:
            avg_iri = filtered_df['iri'].mean()
            st.markdown(f"<div class='metric-card'><h4>Average IRI</h4><h2>{avg_iri:.2f}</h2></div>", unsafe_allow_html=True)

        with col6:
            avg_speed = filtered_df['speed'].mean()
            st.markdown(f"<div class='metric-card'><h4>Average Speed</h4><h2>{avg_speed:.2f} km/h</h2></div>", unsafe_allow_html=True)

        with col7:
            total_distance = filtered_df['travel_distance'].sum()
            st.markdown(f"<div class='metric-card'><h4>Total Distance</h4><h2>{total_distance:.2f} km</h2></div>", unsafe_allow_html=True)

        with col8:
            avg_displacement = filtered_df['vert_displacement'].mean()
            st.markdown(f"<div class='metric-card'><h4>Avg Displacement</h4><h2>{avg_displacement:.2f} mm</h2></div>", unsafe_allow_html=True)

    # SECTION: Quick Map Preview
    st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Quick Map Preview</div>', unsafe_allow_html=True)

    if selected_value:
        try:
            conn = get_connection()
            query = f"""
                SELECT avg_iri, condition, geom
                FROM iri_segments
                WHERE geom IS NOT NULL
                AND {"project_name" if selection_option == "Project Name" else "file_name"} = %s;
            """
            gdf_segments = gpd.read_postgis(query, conn, geom_col="geom", params=(selected_value,))
            conn.close()

            if gdf_segments.empty:
                st.warning("No segment data found for the selected road.")
            else:
                bounds = gdf_segments.total_bounds
                sw = [bounds[1], bounds[0]]
                ne = [bounds[3], bounds[2]]
                center_lat = (bounds[1] + bounds[3]) / 2
                center_lon = (bounds[0] + bounds[2]) / 2

                m = Map(location=[center_lat, center_lon], zoom_start=14, width="100%", position="relative")
                TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
                TileLayer("CartoDB positron", name="Light Theme").add_to(m)
                TileLayer("Stamen Toner", name="Dark Theme").add_to(m)
                TileLayer("Stamen Terrain", name="Terrain").add_to(m)
                #MiniMap().add_to(m)

                for condition, group in gdf_segments.groupby("condition"):
                    layer = FeatureGroup(name=f"IRI: {condition}", show=True)
                    for _, row in group.iterrows():
                        GeoJson(
                            data=row["geom"].__geo_interface__,
                            style_function=lambda _, color=condition_color(condition): {
                                'color': color,
                                'weight': 5,
                                'opacity': 0.8
                            },
                            tooltip=f"{condition} (IRI: {round(row['avg_iri'], 2) if row['avg_iri'] else 'N/A'})"
                        ).add_to(layer)
                    layer.add_to(m)

                LayerControl(collapsed=True, position='topright').add_to(m)
                m.fit_bounds([sw, ne])
                folium_static(m, width=1200, height=400)
                
                # MINI REPORT BUTTON
                with st.container():
                    st.markdown('<div class="section-title">Generate Road Report</div>', unsafe_allow_html=True)
                    if st.button("Generate Mini Report"):
                        st.markdown(f"### Summary for: `{selected_value}`")
                        st.markdown(f"- **Average IRI:** {avg_iri:.2f}")
                        st.markdown(f"- **Average Speed:** {avg_speed:.2f} km/h")
                        st.markdown(f"- **Total Distance:** {total_distance:.2f} km")
                        st.markdown(f"- **Average Vertical Displacement:** {avg_displacement:.2f} mm")


        except Exception as e:
            st.error(f"Error generating map: {e}")
    else:
        st.info("Select a project or file to preview its segments.")

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
