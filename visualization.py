import streamlit as st
import geopandas as gpd
import pandas as pd
from folium import Map, FeatureGroup, GeoJson, LayerControl, TileLayer, Popup
from streamlit_folium import folium_static
from folium.plugins import Fullscreen, LocateControl, MeasureControl
from db import get_connection

@st.cache_data(show_spinner=False)
def load_roads():
    try:
        conn = get_connection()
        query = """
            SELECT osm_id, name, fclass, geom_simplified AS geog
            FROM roads_geojson
            WHERE geom_simplified IS NOT NULL;
        """
        gdf = gpd.read_postgis(query, conn, geom_col='geog')
        conn.close()
        return gdf
    except Exception as e:
        st.error(f"Error loading road data: {e}")
        return gpd.GeoDataFrame(columns=['osm_id', 'name', 'fclass', 'geog'])

@st.cache_data(show_spinner=False)
def load_iri_segments(trigger):
    try:
        conn = get_connection()
        query = """
            SELECT id, avg_iri, condition, geom, length_m, project_name, file_name, avg_speed
            FROM iri_segments
            WHERE geom IS NOT NULL;
        """
        gdf = gpd.read_postgis(query, conn, geom_col='geom')
        conn.close()
        return gdf
    except Exception as e:
        st.error(f"Error loading IRI segments: {e}")
        return gpd.GeoDataFrame(columns=['avg_iri', 'condition', 'geom'])

def fclass_color(fclass):
    color_map = {
        'motorway': 'blue',
        'trunk': 'darkred',
        'primary': 'red',
        'secondary': 'orange',
        'tertiary': 'yellow',
        'residential': 'gray',
        'unclassified': 'black',
        'footway': 'green',
        'path': 'green',
        'pedestrian': 'green',
        'service': 'lightgray'
    }
    return color_map.get(fclass, 'purple')

def condition_color(condition):
    color_map = {
        'Very Good': 'green',
        'Good': 'lime',
        'Fair': 'orange',
        'Mediocre': 'orangered',
        'Poor': 'darkred',
        'Mixed': 'purple',
        'Unknown': 'gray'
    }
    return color_map.get(condition, 'black')

def data_visualization_page():
    st.title("Road & IRI Condition Map")

    if "iri_trigger" not in st.session_state:
        st.session_state.iri_trigger = 0

    if st.button("🔄 Refresh Map Data"):
        st.session_state.iri_trigger += 1

    gdf_roads = load_roads()
    gdf_segments = load_iri_segments(st.session_state.iri_trigger)

    if gdf_roads.empty and gdf_segments.empty:
        st.warning("No road or IRI data found.")
        return

    bounds = gdf_segments.total_bounds if not gdf_segments.empty else gdf_roads.total_bounds
    sw = [bounds[1], bounds[0]]
    ne = [bounds[3], bounds[2]]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = Map(location=[center_lat, center_lon], zoom_start=13)

    TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    TileLayer("CartoDB positron", name="Light Theme").add_to(m)
    TileLayer("Stamen Toner", name="Dark Theme").add_to(m)
    TileLayer("Stamen Terrain", name="Terrain").add_to(m)
    Fullscreen().add_to(m)
    m.options['zoomControl'] = True
    MeasureControl(primary_length_unit='meters').add_to(m)
    LocateControl(auto_start=False).add_to(m)

    important_classes = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'service', 'unclassified']
    for fclass, group in gdf_roads.groupby("fclass"):
        merged = group.dissolve(by="fclass")
        is_important = fclass in important_classes
        layer = FeatureGroup(name=fclass, show=is_important)
        GeoJson(
            data=merged["geog"].iloc[0].__geo_interface__,
            style_function=lambda _, color=fclass_color(fclass): {
                'color': color,
                'weight': 2
            },
            tooltip=fclass
        ).add_to(layer)
        layer.add_to(m)
        

    if not gdf_segments.empty:
        for condition, group in gdf_segments.groupby("condition"):
            layer = FeatureGroup(name=f"IRI: {condition}", show=True)
            for _, row in group.iterrows():
                segment_color = condition_color(row["condition"])
                popup_html = f"""
                <div style="font-size:13px; line-height:1.4;">
                    <b>IRI:</b> {row['avg_iri']:.2f}<br>
                    <b>Condition:</b> {row['condition']}<br>
                    <b>Speed:</b> {row['avg_speed']:.2f} km/h<br>
                    <b>Distance:</b> {row['length_m']:.2f} m<br>
                    <b>Project:</b> {row['project_name']}<br>
                    <b>File:</b> {row['file_name']}
                </div>
                """
                GeoJson(
                    data=row["geom"].__geo_interface__,
                    style_function=lambda _, seg_color=segment_color: {
                        'color': seg_color,
                        'weight': 5,
                        'opacity': 0.8
                    },
                    highlight_function=lambda _: {
                        'color': "black",
                        'weight': 7,
                        'opacity': 1.0
                    },
                    popup=Popup(popup_html, max_width=350)
                ).add_to(layer)
            layer.add_to(m)

    LayerControl(collapsed=True, position='topright').add_to(m)
    m.fit_bounds([sw, ne])
    folium_static(m, width=1000, height=600)
