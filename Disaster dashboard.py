import streamlit as st
import pandas as pd

df = pd.read_excel("emdat_disasters.xlsx")

losses = df["Total Damage ('000 US$)"].dropna()
losses = losses[losses > 0]

st.title("Global Disaster Risk Dashboard")

hazard = st.selectbox("Select Disaster Type", df["Disaster Type"].unique())

filtered = df[df["Disaster Type"] == hazard]

st.bar_chart(filtered.groupby("Start Year").size().sort_index())