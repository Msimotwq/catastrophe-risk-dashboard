import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Global Disaster Risk Dashboard", layout="wide")

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "emdat_disasters.xlsx"
    df = pd.read_excel(file_path)

    numeric_cols = [
        "Start Year",
        "Total Damage ('000 US$)",
        "Insured Damage ('000 US$)",
        "Total Deaths",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

st.title("Global Disaster Risk Dashboard")
st.markdown("Interactive catastrophe risk dashboard using full EM-DAT disaster data.")

# Cleaning core fields
data = df.copy()
data = data.dropna(subset=["Start Year"])
data["Start Year"] = data["Start Year"].astype(int)

if data.empty:
    st.warning("No valid data available.")
    st.stop()

# Metrics
total_events = len(data)
total_loss = data["Total Damage ('000 US$)"].sum(skipna=True)
total_deaths = data["Total Deaths"].sum(skipna=True)
avg_loss = data["Total Damage ('000 US$)"].mean(skipna=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", f"{total_events:,}")
col2.metric("Total Economic Loss ('000 US$)", f"{total_loss:,.0f}" if pd.notna(total_loss) else "N/A")
col3.metric("Total Deaths", f"{total_deaths:,.0f}" if pd.notna(total_deaths) else "N/A")
col4.metric("Average Loss per Event ('000 US$)", f"{avg_loss:,.0f}" if pd.notna(avg_loss) else "N/A")

#Number of Disasters Per Type
st.subheader("Number of Disasters by Type")

events_by_type = (
    data.groupby("Disaster Type")
    .size()
    .sort_values(ascending=False)
    .head(10)
)

fig_type_events = px.bar(
    x=events_by_type.index,
    y=events_by_type.values,
    labels={"x": "Disaster Type", "y": "Number of Events"},
    title="Top 10 Disaster Types by Frequency"
)

st.plotly_chart(fig_type_events, use_container_width=True)

# Events per year
st.subheader("Number of Disasters Per Year")
events_per_year = data.groupby("Start Year").size().sort_index()
st.bar_chart(events_per_year)

# Economic loss by year
st.subheader("Economic Loss by Year")
loss_by_year = (
    data.groupby("Start Year")["Total Damage ('000 US$)"]
    .sum()
    .sort_index()
)

if not loss_by_year.empty:
    fig_loss_year = px.line(
        x=loss_by_year.index,
        y=loss_by_year.values,
        labels={"x": "Year", "y": "Total Damage ('000 US$)"},
        title="Total Economic Loss by Year",
    )
    st.plotly_chart(fig_loss_year, use_container_width=True)

# Top disaster types by loss
st.subheader("Top 10 Disaster Types by Economic Loss")
loss_by_type = (
    data.groupby("Disaster Type")["Total Damage ('000 US$)"]
    .sum(min_count=1)
    .dropna()
    .sort_values(ascending=False)
    .head(10)
)

if not loss_by_type.empty:
    fig_type = px.bar(
        x=loss_by_type.index,
        y=loss_by_type.values,
        labels={"x": "Disaster Type", "y": "Total Damage ('000 US$)"},
        title="Top 10 Disaster Types by Economic Loss",
    )
    st.plotly_chart(fig_type, use_container_width=True)

# Top countries
st.subheader("Top 10 Countries by Disaster Loss")
loss_by_country = (
    data.groupby("Country")["Total Damage ('000 US$)"]
    .sum(min_count=1)
    .dropna()
    .sort_values(ascending=False)
    .head(10)
)

if not loss_by_country.empty:
    fig_country = px.bar(
        x=loss_by_country.index,
        y=loss_by_country.values,
        labels={"x": "Country", "y": "Total Damage ('000 US$)"},
        title="Top 10 Countries by Disaster Loss",
    )
    st.plotly_chart(fig_country, use_container_width=True)

# Distribution of losses
st.subheader("Distribution of Disaster Losses")
losses = data["Total Damage ('000 US$)"].dropna()
losses = losses[losses > 0]

if len(losses) >= 10:
    fig_hist = px.histogram(
        x=np.log10(losses),
        nbins=30,
        title="Distribution of Disaster Losses, Log10 Scale"
    )
    fig_hist.update_layout(
        xaxis_title="Log10 Total Damage ('000 US$)",
        yaxis_title="Frequency"
    )
    st.plotly_chart(fig_hist, use_container_width=True)
elif len(losses) > 0:
    st.info("Only a few positive loss records are available, so the loss distribution chart is limited.")
else:
    st.info("No positive loss data available in the dataset.")

# Monte Carlo simulation
st.subheader("Monte Carlo Catastrophe Loss Simulation")
if len(losses) > 0:
    np.random.seed(42)
    simulated_losses = np.random.choice(losses, size=1000, replace=True)
    average_simulated_loss = simulated_losses.mean()
    var_99 = np.percentile(simulated_losses, 99)

    sim1, sim2 = st.columns(2)
    sim1.metric("Average Simulated Loss ('000 US$)", f"{average_simulated_loss:,.0f}")
    sim2.metric("99% Simulated Loss VaR ('000 US$)", f"{var_99:,.0f}")

    fig_sim = px.histogram(
        x=simulated_losses,
        nbins=40,
        title="Simulated Loss Distribution"
    )
    fig_sim.update_layout(
        xaxis_title="Simulated Loss ('000 US$)",
        yaxis_title="Frequency"
    )
    st.plotly_chart(fig_sim, use_container_width=True)
else:
    st.info("Not enough loss data available for simulation.")

# Data preview
st.subheader("Data Preview")

columns_to_show = [
    "Country",
    "Disaster Type",
    "Start Year",
    "Total Damage ('000 US$)",
    "Insured Damage ('000 US$)",
    "Total Deaths",
]

available_columns = [col for col in columns_to_show if col in data.columns]

st.dataframe(
    data[available_columns].sort_values("Start Year"),
    use_container_width=True,
)