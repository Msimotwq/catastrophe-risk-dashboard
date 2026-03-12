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
st.markdown("Interactive catastrophe risk dashboard using EM-DAT disaster data.")

st.sidebar.header("Filters")

hazard_options = sorted(df["Disaster Type"].dropna().unique())
selected_hazard = st.sidebar.selectbox("Select Disaster Type", hazard_options)

filtered = df[df["Disaster Type"] == selected_hazard].copy()

# Clean Start Year before slider
filtered = filtered.dropna(subset=["Start Year"])
filtered["Start Year"] = filtered["Start Year"].astype(int)

if filtered.empty:
    st.warning("No valid data available for this disaster type.")
    st.stop()

year_min = int(filtered["Start Year"].min())
year_max = int(filtered["Start Year"].max())

# Handle single-year case safely
if year_min == year_max:
    st.sidebar.write(f"Only available year: {year_min}")
    selected_years = (year_min, year_max)
else:
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
    )

filtered = filtered[
    (filtered["Start Year"] >= selected_years[0]) &
    (filtered["Start Year"] <= selected_years[1])
]

if filtered.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# Metrics
total_events = len(filtered)
total_loss = filtered["Total Damage ('000 US$)"].sum(skipna=True)
total_deaths = filtered["Total Deaths"].sum(skipna=True)
avg_loss = filtered["Total Damage ('000 US$)"].mean(skipna=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", f"{total_events:,}")
col2.metric("Total Economic Loss ('000 US$)", f"{total_loss:,.0f}" if pd.notna(total_loss) else "N/A")
col3.metric("Total Deaths", f"{total_deaths:,.0f}" if pd.notna(total_deaths) else "N/A")
col4.metric("Average Loss per Event ('000 US$)", f"{avg_loss:,.0f}" if pd.notna(avg_loss) else "N/A")

# Events per year
st.subheader(f"Number of {selected_hazard} Disasters Per Year")
events_per_year = filtered.groupby("Start Year").size().sort_index()
st.bar_chart(events_per_year)

# Economic loss by year
st.subheader(f"Economic Loss by Year, {selected_hazard}")
loss_by_year = (
    filtered.groupby("Start Year")["Total Damage ('000 US$)"]
    .sum()
    .sort_index()
)

if not loss_by_year.empty:
    fig_loss_year = px.line(
        x=loss_by_year.index,
        y=loss_by_year.values,
        labels={"x": "Year", "y": "Total Damage ('000 US$)"},
        title=f"Total Economic Loss by Year, {selected_hazard}",
    )
    st.plotly_chart(fig_loss_year, use_container_width=True)

# Top countries
st.subheader(f"Top 10 Countries by {selected_hazard} Loss")
loss_by_country = (
    filtered.groupby("Country")["Total Damage ('000 US$)"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

if not loss_by_country.empty:
    fig_country = px.bar(
        x=loss_by_country.index,
        y=loss_by_country.values,
        labels={"x": "Country", "y": "Total Damage ('000 US$)"},
        title=f"Top 10 Countries by {selected_hazard} Loss",
    )
    st.plotly_chart(fig_country, use_container_width=True)

# Distribution of losses
st.subheader("Distribution of Disaster Losses")
losses = filtered["Total Damage ('000 US$)"].dropna()
losses = losses[losses > 0]

if len(losses) > 0:
    fig_hist = px.histogram(
        filtered[filtered["Total Damage ('000 US$)"] > 0],
        x="Total Damage ('000 US$)",
        nbins=40,
        log_x=True,
        title="Distribution of Disaster Losses, Log Scale",
    )
    st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.info("No positive loss data available for this selection.")

# Monte Carlo simulation
st.subheader("Monte Carlo Catastrophe Loss Simulation")
if len(losses) > 0:
    np.random.seed(42)
    simulated_losses = np.random.choice(losses, size=1000, replace=True)
    expected_loss = simulated_losses.mean()
    var_99 = np.percentile(simulated_losses, 99)

    sim1, sim2 = st.columns(2)
    sim1.metric("Expected Annual Loss ('000 US$)", f"{expected_loss:,.0f}")
    sim2.metric("99% Value at Risk ('000 US$)", f"{var_99:,.0f}")

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
st.subheader("Filtered Data Preview")

columns_to_show = [
    "Country",
    "Disaster Type",
    "Start Year",
    "Total Damage ('000 US$)",
    "Insured Damage ('000 US$)",
    "Total Deaths",
]

available_columns = [col for col in columns_to_show if col in filtered.columns]

st.dataframe(
    filtered[available_columns].sort_values("Start Year"),
    use_container_width=True,
)