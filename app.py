# app.py
"""
Global COVID-19 Big Data Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global COVID-19 Big Data Analytics", layout="wide")
st.title("🌍 Global COVID-19 Big Data Analytics Dashboard")

# -----------------------------------------------------
# LARGE DATASET SOURCE (working URL)
# -----------------------------------------------------
URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"


# -----------------------------------------------------
# LOAD (cached)
# -----------------------------------------------------
@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_csv(URL, low_memory=False)
    df['date'] = pd.to_datetime(df['date'])
    return df


with st.spinner("Loading worldwide big dataset (be patient)…"):
    df = load_data()

st.success("Big dataset loaded successfully!")


# -----------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------
countries = sorted(df['location'].dropna().unique())

st.sidebar.header("Filters")
country = st.sidebar.selectbox("Choose country", countries)

min_date = df['date'].min()
max_date = df['date'].max()

date_range = st.sidebar.date_input(
    "Date range",
    (min_date.date(), max_date.date())
)

start_date, end_date = pd.to_datetime(date_range)

df_country = df[(df['location'] == country) &
                (df['date'] >= start_date) &
                (df['date'] <= end_date)]

# -----------------------------------------------------
# KPIs
# -----------------------------------------------------
latest = df_country.sort_values("date").iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Population", f"{int(latest['population']):,}" if pd.notna(latest['population']) else "N/A")
col2.metric("Total Cases", f"{int(latest['total_cases']):,}" if pd.notna(latest['total_cases']) else "N/A")
col3.metric("Total Deaths", f"{int(latest['total_deaths']):,}" if pd.notna(latest['total_deaths']) else "N/A")
col4.metric("Total Vaccinations",
            f"{int(latest['total_vaccinations']):,}" if pd.notna(latest['total_vaccinations']) else "N/A")


# -----------------------------------------------------
# Trend lines
# -----------------------------------------------------
st.subheader("📈 Cases & Deaths Over Time")
fig = px.line(df_country, x="date", y=["new_cases", "new_deaths"])
st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------
# Vaccination
# -----------------------------------------------------
st.subheader("💉 Vaccination Progress")
fig2 = px.line(df_country, x="date", y="new_vaccinations")
st.plotly_chart(fig2, use_container_width=True)


# -----------------------------------------------------
# Heatmap
# -----------------------------------------------------
st.subheader("🧊 Monthly Cases Heatmap (seasonal patterns)")

df_country['month'] = df_country['date'].dt.to_period('M')
heatmap = df_country.groupby("month")['new_cases'].sum().reset_index()
heatmap['month'] = heatmap['month'].astype(str)

fig3 = px.bar(heatmap, x="month", y="new_cases")
st.plotly_chart(fig3, use_container_width=True)


# -----------------------------------------------------
# Download
# -----------------------------------------------------
st.subheader("Download Filtered Data")
st.download_button(
    "Download CSV",
    df_country.to_csv(index=False).encode("utf-8"),
    "covid_big_data_filtered.csv",
    "text/csv",
)
