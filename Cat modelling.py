import pandas as pd
import matplotlib.pyplot as plt
from streamlit import title
import plotly.express as px
import numpy as np

df = pd.read_excel("/Users/apple/PycharmProjects/Catastrophe Risk Modelling/emdat_disasters.xlsx")
df= df[[
    "Country",
    "Disaster Type",
    "Start Year",
    "Insured Damage ('000 US$)",
"Total Damage ('000 US$)",
    "Total Deaths"
]]

df.head()
print (df.head())

events_per_year=df.groupby("Start Year").size()
events_per_year.plot()
plt.title("Number of Disasters Per Year")
plt.show()

fig=px.histogram(
    df, x="Total Damage ('000 US$)", title="Distribution of Disaster Losses",
    log_x=True
)
fig.show()

loss_by_type= df.groupby("Disaster Type")["Total Damage ('000 US$)"].sum()
loss_by_type.plot(kind="bar")
plt.title("Total Economic Loss by Disaster Type")
plt.show()

loss_by_country=df.groupby("Country")["Total Damage ('000 US$)"].sum().sort_values(ascending=False)
loss_by_country.head(10).plot(kind="bar")
plt.title("Top 10 Countries by Disaster Loss")
plt.show()

losses=df["Total Damage ('000 US$)"].dropna()
simulated_losses=np.random.choice(losses,1000)
expected_loss=simulated_losses.mean()
var_99= np.percentile(simulated_losses,99)
print("Expected Annual Loss:", expected_loss)
print("99% Value at Risk:", var_99)


