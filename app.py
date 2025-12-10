import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import warnings
import os
import sys
from flask import Flask

warnings.filterwarnings('ignore')

# ========== CRITICAL FIX: BUAT DATA DUMMY YANG BAIK ==========
print("=" * 80)
print("🚀 INITIALIZING DASHBOARD FOR RAILWAY")
print("=" * 80)

# Buat Flask server
server = Flask(__name__)

# ========== BUAT DATA DUMMY REALISTIS ==========
np.random.seed(42)
n_customers = 1500

print(f"📊 Creating realistic dummy data with {n_customers} customers...")

# Buat data yang lebih realistis
data = {
    'CustomerID': range(1, n_customers + 1),
    'Recency': np.random.randint(1, 365, n_customers),
    'Frequency': np.random.randint(1, 50, n_customers),
    'Monetary': np.random.randint(100, 10000, n_customers),
    'AvgOrderValue': np.random.randint(50, 500, n_customers),
    'RFM_Score': np.random.randint(1, 10, n_customers),
    'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n_customers, p=[0.1, 0.15, 0.2, 0.05, 0.15, 0.1, 0.25])
}

# Buat karakteristik khusus untuk setiap cluster
data['Monetary'] = np.where(data['Cluster_KMeans'] == 3, 
                           np.random.randint(5000, 50000, n_customers), 
                           data['Monetary'])
data['Frequency'] = np.where(data['Cluster_KMeans'] == 6, 
                            np.random.randint(20, 200, n_customers), 
                            data['Frequency'])
data['Recency'] = np.where(data['Cluster_KMeans'] == 0, 
                          np.random.randint(300, 365, n_customers), 
                          data['Recency'])
data['Recency'] = np.where(data['Cluster_KMeans'] == 1, 
                          np.random.randint(1, 30, n_customers), 
                          data['Recency'])

rfm = pd.DataFrame(data)
rfm.set_index('CustomerID', inplace=True)

print(f"✅ Created dummy data: {len(rfm)} rows, {len(rfm.columns)} columns")
print(f"📈 Sample data:")
print(rfm.head(3))

# ========== STRATEGI CLUSTER ==========
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

# Assign strategi ke cluster
def get_strat(cid):
    if cid == 1 or cid == 3 or cid == 4 or cid == 6:
        return {**strats['champions'], 'cluster_id': cid}
    elif cid == 2:
        return {**strats['loyal'], 'cluster_id': cid}
    elif cid == 5:
        return {**strats['big'], 'cluster_id': cid}
    elif cid == 0:
        return {**strats['dormant'], 'cluster_id': cid}
    else:
        return {**strats['standard'], 'cluster_id': cid}

profs = {}
for c in rfm['Cluster_KMeans'].unique():
    profs[c] = get_strat(c)
    
# Tambahkan kolom label
for c, p in profs.items():
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']

colors = {}
for c, p in profs.items():
    label = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    colors[label] = p['color']

print(f"✅ Created {len(profs)} customer segments")

# ========== INITIALIZE DASH APP ==========
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# ========== SIMPLE LAYOUT (MINIMAL CSS) ==========
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🎯 Customer Intelligence Dashboard", 
                style={'textAlign': 'center', 'color': 'white', 'marginBottom': '10px'}),
        html.P("Real-time Customer Segmentation & Analytics", 
               style={'textAlign': 'center', 'color': 'rgba(255,255,255,0.9)'})
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '30px',
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),
    
    # Metrics Cards
    html.Div([
        html.Div([
            html.H3(f"{len(rfm):,}", style={'color': '#667eea', 'margin': '0'}),
            html.P("Total Customers", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"£{rfm['Monetary'].sum()/1e6:.1f}M", style={'color': '#667eea', 'margin': '0'}),
            html.P("Total Revenue", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"{rfm['Cluster_KMeans'].nunique()}", style={'color': '#667eea', 'margin': '0'}),
            html.P("Customer Segments", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"£{rfm['AvgOrderValue'].mean():.0f}", style={'color': '#667eea', 'margin': '0'}),
            html.P("Avg Order Value", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
    ], style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
        'gap': '20px',
        'marginBottom': '30px'
    }),
    
    # Simple Filters
    html.Div([
        html.Label("Select Segment:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='segment-filter',
            options=[{'label': 'All Segments', 'value': 'all'}] + 
                    [{'label': f"{p['name']} (C{c})", 'value': c} for c, p in profs.items()],
            value='all',
            style={'width': '300px', 'display': 'inline-block'}
        )
    ], style={'padding': '20px', 'background': '#f8f9fa', 'borderRadius': '10px', 'marginBottom': '30px'}),
    
    # Tabs
    dbc.Tabs([
        # Tab 1: Charts
        dbc.Tab(label="📈 Analytics", children=[
            html.Div([
                dcc.Graph(id='pie-chart', style={'height': '400px'}),
                dcc.Graph(id='bar-chart', style={'height': '400px'}),
                dcc.Graph(id='scatter-3d', style={'height': '500px'})
            ], style={'padding': '20px'})
        ]),
        
        # Tab 2: Strategies
        dbc.Tab(label="🎯 Strategies", children=[
            html.Div(id='strategy-cards', style={'padding': '20px'})
        ])
    ]),
    
    # Status indicator
    html.Div([
        html.P(f"✅ Dashboard loaded successfully | Data: {len(rfm):,} customers",
               style={'textAlign': 'center', 'color': '#666', 'marginTop': '30px'})
    ])
], style={
    'padding': '20px',
    'maxWidth': '1400px',
    'margin': '0 auto',
    'fontFamily': 'Arial, sans-serif'
})

# ========== SIMPLE CALLBACKS ==========
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('scatter-3d', 'figure'),
     Output('strategy-cards', 'children')],
    [Input('segment-filter', 'value')]
)
def update_charts(selected_segment):
    # Filter data
    if selected_segment == 'all':
        df = rfm
    else:
        df = rfm[rfm['Cluster_KMeans'] == selected_segment]
    
    print(f"📊 Updating charts with {len(df)} customers")
    
    # 1. Pie Chart
    cluster_counts = df['Cluster_Label'].value_counts()
    pie_fig = go.Figure(data=[go.Pie(
        labels=cluster_counts.index,
        values=cluster_counts.values,
        hole=0.4,
        marker=dict(colors=[colors.get(l, '#ccc') for l in cluster_counts.index])
    )])
    pie_fig.update_layout(title_text="Customer Distribution")
    
    # 2. Bar Chart
    revenue_by_segment = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
    bar_fig = go.Figure(data=[go.Bar(
        x=revenue_by_segment.values,
        y=revenue_by_segment.index,
        orientation='h',
        marker=dict(color='#667eea')
    )])
    bar_fig.update_layout(
        title_text="Revenue by Segment",
        xaxis_title="Revenue (£)",
        yaxis_title="Segment"
    )
    
    # 3. 3D Scatter
    scatter_fig = go.Figure(data=[go.Scatter3d(
        x=df['Recency'],
        y=df['Frequency'],
        z=df['Monetary'],
        mode='markers',
        marker=dict(
            size=5,
            color=df['Cluster_KMeans'],
            colorscale='Viridis',
            opacity=0.8
        ),
        text=df['Cluster_Label'],
        hoverinfo='text'
    )])
    scatter_fig.update_layout(
        title_text="3D Customer Analysis",
        scene=dict(
            xaxis_title="Recency (days)",
            yaxis_title="Frequency",
            zaxis_title="Monetary (£)"
        ),
        height=500
    )
    
    # 4. Strategy Cards
    if selected_segment == 'all':
        segments_to_show = list(profs.keys())[:3]  # Show first 3
    else:
        segments_to_show = [selected_segment]
    
    strategy_cards = []
    for cid in segments_to_show:
        p = profs[cid]
        strategy_cards.append(
            html.Div([
                html.H4(p['name'], style={'color': p['color']}),
                html.P(f"Strategy: {p['strategy']}"),
                html.P(f"Priority: {p['priority']}"),
                html.Hr(),
                html.P("Key Tactics:"),
                html.Ul([html.Li(tactic) for tactic in p['tactics'][:3]])
            ], style={
                'padding': '20px',
                'background': 'white',
                'borderRadius': '10px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'marginBottom': '20px'
            })
        )
    
    return pie_fig, bar_fig, scatter_fig, strategy_cards

# ========== HEALTH CHECK ==========
@server.route('/health')
def health():
    return {
        'status': 'ok',
        'customers': len(rfm),
        'segments': rfm['Cluster_KMeans'].nunique(),
        'revenue': f"£{rfm['Monetary'].sum():,.0f}"
    }

# ========== DEBUG ROUTE ==========
@server.route('/debug')
def debug():
    return {
        'data_loaded': len(rfm),
        'columns': list(rfm.columns),
        'sample': rfm.head(5).to_dict()
    }

# ========== RUN APP ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    
    print("=" * 80)
    print(f"🚀 STARTING SERVER ON PORT: {port}")
    print(f"📊 Total customers: {len(rfm):,}")
    print(f"🎯 Segments: {rfm['Cluster_KMeans'].nunique()}")
    print(f"💰 Total revenue: £{rfm['Monetary'].sum():,.0f}")
    print(f"🔧 Debug mode: {debug_mode}")
    print("=" * 80)
    
    # Start the server
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        dev_tools_hot_reload=False
    )
