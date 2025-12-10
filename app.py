import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings("ignore")

# Load Data
try:
    rfm = pd.read_csv("final_customer_segments (1).csv", index_col=0)
except:
    rfm = pd.read_csv("final_customer_segments.csv", index_col=0)

# Cluster Strategies
strats = {
    "champions": {"name": "🏆 Champions", "color": "#FFD700", "priority": "CRITICAL"},
    "loyal": {"name": "💎 Loyal", "color": "#667eea", "priority": "HIGH"},
    "big": {"name": "💰 Big Spenders", "color": "#f093fb", "priority": "CRITICAL"},
    "dormant": {"name": "😴 Dormant", "color": "#ff6b6b", "priority": "URGENT"},
    "potential": {"name": "🌱 Potential", "color": "#11998e", "priority": "MEDIUM"},
    "standard": {"name": "📊 Standard", "color": "#89f7fe", "priority": "MEDIUM"}
}

# Simple Strategy Logic
def get_strat(cid, data):
    cd = data[data["Cluster_KMeans"] == cid]
    r = cd["Recency"].mean()
    f = cd["Frequency"].mean()
    m = cd["Monetary"].mean()

    if r < 50 and f > 10 and m > 1000:
        key = "champions"
    elif r < 50 and f > 5:
        key = "loyal"
    elif m > 1500:
        key = "big"
    elif r > 100:
        key = "dormant"
    elif r < 50 and f < 5:
        key = "potential"
    else:
        key = "standard"

    return {**strats[key], "cluster_id": cid}

# Attach Labels
profs = {}
for c in rfm["Cluster_KMeans"].unique():
    p = get_strat(c, rfm)
    profs[c] = p
    rfm.loc[rfm["Cluster_KMeans"] == c, "Cluster_Label"] = f"{p['name']} (C{c})"
    rfm.loc[rfm["Cluster_KMeans"] == c, "Priority"] = p["priority"]

colors = {p["name"] + f" (C{c})": p["color"] for c, p in profs.items()}

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Customer Intelligence Dashboard"),
    dcc.Dropdown(
        id="cf",
        options=[{"label": "All Segments", "value": "all"}] + 
                [{"label": p["name"], "value": c} for c, p in profs.items()],
        value="all"
    ),
    dcc.Graph(id="pie"),
    dcc.Graph(id="rev")
])

@app.callback(
    [Output("pie", "figure"), Output("rev", "figure")],
    [Input("cf", "value")]
)
def upd(sc):
    df = rfm.copy()
    if sc != "all":
        df = df[df["Cluster_KMeans"] == sc]

    # Pie
    cc = df["Cluster_Label"].value_counts()
    pie = go.Figure(go.Pie(
        labels=cc.index,
        values=cc.values,
        hole=0.55,
        marker=dict(colors=[colors.get(l, "#95A5A6") for l in cc.index])
    ))

    # Revenue Bar
    rv = df.groupby("Cluster_Label")["Monetary"].sum().sort_values()
    bar = go.Figure(go.Bar(
        x=rv.values,
        y=rv.index,
        orientation="h"
    ))

    return pie, bar

server = app.server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run_server(host="0.0.0.0", port=port)
