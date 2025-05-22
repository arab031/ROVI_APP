import streamlit as st
import plotly.express as px

def data_visualization_page():
    st.title("Data Visualization")
    df = px.data.gapminder()
    fig = px.line(df, x="year", y="gdpPercap", title="Sample Data")
    st.plotly_chart(fig)

from folium import Map, CircleMarker
from streamlit_folium import folium_static
from folium.plugins import MiniMap
from geopy.geocoders import Nominatim

def data_visualization_page():
    # Custom CSS for the box
    st.markdown(
        """
        <style>
        .map-card {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #ddd;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize geocoder
    geolocator = Nominatim(user_agent="my_streamlit_app")

    # Search input
    search_query = st.text_input("Search for a location or road (e.g., 'Kumasi, Ghana' or 'Main Street, Kumasi')")

    # Default map location
    map_center = [6.6885, -1.6244]  # Kumasi, Ghana
    zoom_start = 13

    # Geocode the search query if provided
    if search_query:
        try:
            location = geolocator.geocode(search_query)
            if location:
                map_center = [location.latitude, location.longitude]
                zoom_start = 15  # Zoom in more for searched location
            else:
                st.warning("Location not found. Using default location.")
        except Exception as e:
            st.warning("Error geocoding location. Using default location.")
            st.write(f"Error: {e}")

    # Create map
    m = Map(location=map_center, zoom_start=zoom_start, tiles="OpenStreetMap")
    MiniMap(position="bottomright").add_to(m)

    # Add marker for the searched or default location
    CircleMarker(
        location=map_center,
        radius=8,
        color="#FF6F61",
        fill=True,
        fill_opacity=0.9,
        popup=search_query if search_query else "Sample Road Location",
        tooltip="Searched Location"
    ).add_to(m)

    # Wrap the map in a custom box
    st.markdown("<div class='map-card'><h4>Data Visualization</h4>", unsafe_allow_html=True)
    folium_static(m, width=900, height=400)
    st.markdown("</div>", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    data_visualization_page()
