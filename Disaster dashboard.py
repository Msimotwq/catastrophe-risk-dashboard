import streamlit as st
import pandas as pd
from pathlib import Path

file_path = Path(__file__).parent / "emdat_disasters.xlsx"
df = pd.read_excel(file_path)

st.title("Global Disaster Risk Dashboard")

hazard = st.selectbox("Select Disaster Type", sorted(df["Disaster Type"].dropna().unique()))

filtered = df[df["Disaster Type"] == hazard]

st.bar_chart(filtered.groupby("Start Year").size().sort_index())