import streamlit as st
import plotly.express as px

def data_visualization_page():
    st.title("Data Visualization")
    df = px.data.gapminder()
    fig = px.line(df, x="year", y="gdpPercap", title="Sample Data")
    st.plotly_chart(fig)