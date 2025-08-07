import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from src.utils import load_crime_data
from src.predictive_model import load_model, make_prediction

# --- Setup
st.set_page_config(page_title="Crime Analysis Dashboard", layout="wide")

# Inject custom CSS for beautiful fonts and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500&display=swap');

    body {
        font-family: 'Poppins', sans-serif;
        background-color: #f4f7fa;
        color: #333;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: #1a2a44;
    }
    .stMarkdown, .stText, .stSelectbox, .stSlider, .stButton > button {
        font-family: 'Poppins', sans-serif;
        color: white;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 20px;
    }
    .stMetric {
        background-color: cyan;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        text-align: center;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .stMetric label {
        font-size: 1.1rem;
        font-weight: 600;
        color: purple;
    }
    .stMetric .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: purple;
    }
    .stProgress > .stProgressBar {
        background-color: #007bff;
        border-radius: 5px;
    }
    .stPlotlyChart, .stPydeckChart {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .about-section {
        background-color: black;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .footer {
        text-align: center;
        font-family: 'Roboto Mono', monospace;
        color: #666;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Crime Analysis & Prediction Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #666;'>Explore Boston crime trends and predict incidents with advanced analytics</h4>", unsafe_allow_html=True)

# --- Load Data
@st.cache_data
def load_data():
    return load_crime_data()

crime_data = load_data()

# --- Sidebar Filters
st.sidebar.header("Data Filters")
districts = st.sidebar.multiselect("Select District(s):", sorted(crime_data['DISTRICT'].dropna().unique()))
offense_types = st.sidebar.multiselect("Select Crime Type(s):", sorted(crime_data['OFFENSE_CODE_GROUP'].dropna().unique()))
years = st.sidebar.multiselect("Select Year(s):", sorted(crime_data['YEAR'].dropna().unique()))
months = st.sidebar.multiselect("Select Month(s):", sorted(crime_data['MONTH'].dropna().unique()))

# --- Filter Logic
filtered_data = crime_data.copy()
if districts:
    filtered_data = filtered_data[filtered_data['DISTRICT'].isin(districts)]
if offense_types:
    filtered_data = filtered_data[filtered_data['OFFENSE_CODE_GROUP'].isin(offense_types)]
if years:
    filtered_data = filtered_data[filtered_data['YEAR'].isin(years)]
if months:
    filtered_data = filtered_data[filtered_data['MONTH'].isin(months)]

st.markdown("<hr style='border: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

# --- Main Metrics (Fixed for Visibility)
st.subheader("Key Statistics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Crimes", value=len(filtered_data))
with col2:
    most_common_crime = filtered_data['OFFENSE_CODE_GROUP'].mode()[0] if not filtered_data.empty else "No data"
    st.metric(label="Most Common Crime", value=most_common_crime)
with col3:
    busiest_month = filtered_data['MONTH'].mode()[0] if not filtered_data.empty else "No data"
    st.metric(label="Busiest Month", value=busiest_month)

# --- Heatmap Visualization
st.markdown("<hr style='border: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
st.subheader("Crime Risk Heatmap")

map_type = st.selectbox("Select Map Style:", ["Light", "Dark", "Satellite", "Streets"])
map_styles = {
    "Light": "mapbox://styles/mapbox/light-v10",
    "Dark": "mapbox://styles/mapbox/dark-v10",
    "Satellite": "mapbox://styles/mapbox/satellite-streets-v11",
    "Streets": "mapbox://styles/mapbox/streets-v11"
}
selected_map_style = map_styles.get(map_type, map_styles["Light"])

if not filtered_data.empty and {'Lat', 'Long'}.issubset(filtered_data.columns):
    filtered_data = filtered_data.dropna(subset=['Lat', 'Long'])

    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=filtered_data,
        get_position='[Long, Lat]',
        opacity=0.9,
        threshold=0.3,
        get_weight=1
    )
    view_state = pdk.ViewState(
        latitude=filtered_data['Lat'].mean(),
        longitude=filtered_data['Long'].mean(),
        zoom=11,
        pitch=50
    )
    heatmap = pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=view_state,
        map_style=selected_map_style,
        tooltip={"text": "Crime Hotspot"}
    )
    st.pydeck_chart(heatmap)
else:
    st.warning("No location data available to plot heatmap.")

# --- Crime Trend Over Time
st.markdown("<hr style='border: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
st.subheader("Crime Trends Over Time")
if not filtered_data.empty:
    trend_data = (
        filtered_data.groupby(["YEAR", "MONTH"]).size().reset_index(name="Crime Count")
    )
    trend_data["Date"] = pd.to_datetime(
        trend_data["YEAR"].astype(str) + "-" + trend_data["MONTH"].astype(str) + "-01"
    )
    fig = px.line(trend_data.sort_values("Date"), x="Date", y="Crime Count", title="Crime Trends", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data to display for trends.")

# --- Crime by Hour Heatmap
st.subheader("Crime Frequency by Hour and Day")
if not filtered_data.empty:
    pivot = pd.crosstab(filtered_data['DAY_OF_WEEK'], filtered_data['HOUR'])
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex(day_order)
    fig = px.imshow(
        pivot,
        labels=dict(x="Hour of Day", y="Day of Week", color="Crime Count"),
        x=pivot.columns,
        y=pivot.index,
        aspect="auto",
        color_continuous_scale="OrRd",
        title="Crime Frequency Heatmap"
    )
    st.plotly_chart(fig, use_container_width=True)

    max_count = pivot.values.max()
    max_idx = list(zip(*((pivot.values == max_count).nonzero())))[0]
    peak_day = pivot.index[max_idx[0]]
    peak_hour = pivot.columns[max_idx[1]]
    st.success(f"Peak Crime Time: {peak_day} at {peak_hour}:00 with {max_count} incidents.")
else:
    st.info("No data available to display hourly heatmap.")

# --- Top Offense Types
st.subheader("Top 10 Crime Types")
if not filtered_data.empty:
    top_offenses = filtered_data['OFFENSE_CODE_GROUP'].value_counts().head(10)
    st.bar_chart(top_offenses)
else:
    st.info("No data to display for top crimes.")

# --- Donut Chart for Crime Types
st.subheader("Crime Type Distribution (Top 5)")
if not filtered_data.empty:
    top5 = filtered_data['OFFENSE_CODE_GROUP'].value_counts().nlargest(5)
    fig = px.pie(
        names=top5.index,
        values=top5.values,
        hole=0.5,
        title="Top 5 Crime Types"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data to show donut chart.")

# --- Predictive Model Section
st.markdown("<hr style='border: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
st.subheader("Predict Crime Likelihood")

@st.cache_resource
def get_model():
    return load_model()

model = get_model()

with st.form("prediction_form"):
    st.write("Enter details to predict crime occurrence:")
    selected_district = st.selectbox("District:", sorted(crime_data['DISTRICT'].dropna().unique()))
    selected_day = st.selectbox("Day of Week:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    selected_hour = st.slider("Hour of the Day:", 0, 23, 12)
    predict_button = st.form_submit_button("Predict")

if predict_button:
    input_data = {
        "DISTRICT": selected_district,
        "DAY_OF_WEEK": selected_day,
        "HOUR": selected_hour
    }
    prediction = make_prediction(model, input_data)
    st.success(f"Prediction: {prediction}")
    st.progress(0.85)

# --- About Section
with st.expander("About this Dashboard", expanded=False):
    st.markdown("""
    <div class='about-section'>
        This interactive dashboard provides in-depth analysis of Boston crime data.
        <ul>
            <li>Filter by district, year, month, and crime type for customized insights.</li>
            <li>Visualize trends and patterns with interactive charts and heatmaps.</li>
            <li>Predict crime likelihood using a machine learning model based on location, day, and time.</li>
        </ul>
        <b>Data Source</b>: <a href="https://data.boston.gov/" target="_blank">Boston Open Data Portal</a>
    </div>
    """, unsafe_allow_html=True)

# --- Footer
st.markdown("<div class='footer'>Built by Falcons For the Future with the Past</div>", unsafe_allow_html=True)