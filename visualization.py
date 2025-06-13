import streamlit as st
import plotly.express as px
from folium import Map, CircleMarker
from streamlit_folium import folium_static
from folium.plugins import MiniMap



def data_visualization_page():
         
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