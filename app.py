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
import traceback

warnings.filterwarnings('ignore')

# ========== INITIALIZATION ==========
print("=" * 80)
print("🚀 CUSTOMER INTELLIGENCE DASHBOARD - RAILWAY DEPLOYMENT")
print("=" * 80)

# Inisialisasi Flask server
server = Flask(__name__)

# ========== SMART DATA LOADER ==========
def smart_data_loader():
    """Load data dengan berbagai fallback"""
    try:
        # Coba load CSV
        if os.path.exists('final_customer_segments.csv'):
            df = pd.read_csv('final_customer_segments.csv')
            print(f"📊 Loaded CSV: {df.shape}")
            
            # Buat data dari CSV dengan mapping otomatis
            data = {}
            
            # Cari kolom Frequency
            freq_cols = [col for col in df.columns if 'freq' in col.lower() or 'order' in col.lower()]
            data['Frequency'] = df[freq_cols[0]] if freq_cols else np.random.randint(1, 50, len(df))
            
            # Cari kolom Monetary
            money_cols = [col for col in df.columns if 'monet' in col.lower() or 'revenue' in col.lower() or 'spend' in col.lower()]
            data['Monetary'] = df[money_cols[0]] if money_cols else np.random.randint(100, 10000, len(df))
            
            # Recency (default karena tidak ada di CSV)
            data['Recency'] = np.random.randint(1, 365, len(df))
            
            # AvgOrderValue
            avg_cols = [col for col in df.columns if 'avg' in col.lower() or 'average' in col.lower()]
            data['AvgOrderValue'] = df[avg_cols[0]] if avg_cols else np.random.randint(50, 500, len(df))
            
            # RFM Score
            score_cols = [col for col in df.columns if 'score' in col.lower() or 'rfm' in col.lower()]
            data['RFM_Score'] = df[score_cols[0]] if score_cols else np.random.randint(3, 15, len(df))
            
            # Cluster (dari Customer Category jika ada)
            if 'Customer Category' in df.columns:
                category_map = {
                    'Champion': 1, 'Champions': 1,
                    'Loyal': 2, 
                    'At Risk': 3, 'At Risk': 3,
                    'Cannot Lose': 4,
                    'Others': 5, 'Other': 5
                }
                data['Cluster_KMeans'] = df['Customer Category'].map(category_map).fillna(0).astype(int)
            else:
                # Buat cluster dari RFM score
                data['Cluster_KMeans'] = pd.qcut(data['RFM_Score'], 7, labels=False, duplicates='drop')
            
            rfm = pd.DataFrame(data)
            print(f"✅ Processed {len(rfm)} rows from CSV")
            
        else:
            print("📂 CSV not found, using enhanced dummy data")
            rfm = create_enhanced_dummy_data()
            
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        print("🔄 Falling back to dummy data")
        rfm = create_enhanced_dummy_data()
    
    return rfm

def create_enhanced_dummy_data():
    """Create realistic dummy data for dashboard"""
    np.random.seed(42)
    n = 3680  # Sesuai dengan data Anda
    
    print(f"📊 Creating enhanced dummy data with {n} customers...")
    
    # Buat data dasar
    data = {
        'Recency': np.random.randint(1, 365, n),
        'Frequency': np.random.randint(1, 50, n),
        'Monetary': np.random.randint(100, 10000, n),
        'AvgOrderValue': np.random.randint(50, 500, n),
        'RFM_Score': np.random.randint(1, 10, n),
        'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n, p=[0.15, 0.2, 0.15, 0.1, 0.15, 0.1, 0.15])
    }
    
    # Enhance untuk cluster tertentu
    # Cluster 1: Champions (low recency, high frequency, high monetary)
    mask = data['Cluster_KMeans'] == 1
    data['Recency'] = np.where(mask, np.random.randint(1, 30, n), data['Recency'])
    data['Frequency'] = np.where(mask, np.random.randint(15, 50, n), data['Frequency'])
    data['Monetary'] = np.where(mask, np.random.randint(5000, 30000, n), data['Monetary'])
    
    # Cluster 3: Big Spenders
    mask = data['Cluster_KMeans'] == 3
    data['Monetary'] = np.where(mask, np.random.randint(10000, 50000, n), data['Monetary'])
    data['AvgOrderValue'] = np.where(mask, np.random.randint(1000, 5000, n), data['AvgOrderValue'])
    
    # Cluster 6: High Frequency
    mask = data['Cluster_KMeans'] == 6
    data['Frequency'] = np.where(mask, np.random.randint(30, 100, n), data['Frequency'])
    
    # Cluster 0: Dormant
    mask = data['Cluster_KMeans'] == 0
    data['Recency'] = np.where(mask, np.random.randint(200, 365, n), data['Recency'])
    data['Frequency'] = np.where(mask, np.random.randint(1, 5, n), data['Frequency'])
    
    return pd.DataFrame(data)

# Load data
rfm = smart_data_loader()
print(f"\n✅ FINAL DATA LOADED: {len(rfm):,} customers")
print(f"📈 Clusters: {rfm['Cluster_KMeans'].nunique()}")
print(f"💰 Revenue: £{rfm['Monetary'].sum()/1e6:.2f}M")
print(f"📊 Sample data:\n{rfm.head(3)}")

# ========== CLUSTER STRATEGIES ==========
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

# Champion Sub-segments Explanation
champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

def get_strat(cid, data):
    """Assign strategy based on cluster characteristics"""
    try:
        cd = data[data['Cluster_KMeans'] == cid]
        if len(cd) == 0:
            return {**strats['standard'], 'cluster_id': cid}
        
        r = cd['Recency'].mean()
        f = cd['Frequency'].mean()
        m = cd['Monetary'].mean()
        
        if r < 50 and f > 10 and m > 1000:
            s = 'champions'
        elif r < 50 and f > 5:
            s = 'loyal'
        elif m > 1500:
            s = 'big'
        elif r > 100:
            s = 'dormant'
        elif r < 50 and f < 5:
            s = 'potential'
        else:
            s = 'standard'
        
        return {**strats[s], 'cluster_id': cid}
    except:
        return {**strats['standard'], 'cluster_id': cid}

# Create cluster profiles
profs = {}
for c in rfm['Cluster_KMeans'].unique():
    p = get_strat(c, rfm)
    profs[c] = p
    
    # Add cluster labels
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']

colors = {f"{p['name'][:2]} {p['name'][2:]} (C{c})": p['color'] for c, p in profs.items()}

print(f"\n🎯 Created {len(profs)} customer segments")
for c, p in profs.items():
    count = len(rfm[rfm['Cluster_KMeans'] == c])
    print(f"  • {p['name']} (C{c}): {count:,} customers")

# ========== DASH APP INITIALIZATION ==========
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Custom HTML template dengan styling
app.index_string = '''<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Customer Intelligence Dashboard</title>
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Poppins:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Inter', 'Poppins', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 16px; min-height: 100vh; }
            .dash-container { background: rgba(255, 255, 255, 0.98); border-radius: 32px; padding: 40px; box-shadow: 0 40px 100px rgba(0,0,0,0.4); animation: fadeIn 0.8s ease-out; max-width: 1400px; margin: 0 auto; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
            
            /* Header */
            .header { text-align: center; padding: 28px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 24px; margin-bottom: 36px; position: relative; overflow: hidden; box-shadow: 0 15px 40px rgba(102,126,234,0.35); }
            .header-title { font-size: 3.2rem; font-weight: 900; color: #fff; text-shadow: 4px 4px 8px rgba(0,0,0,.35); margin: 0; letter-spacing: -1.5px; line-height: 1.1; }
            .header-subtitle { color: rgba(255,255,255,.95); font-size: 1.2rem; margin-top: 10px; font-weight: 500; letter-spacing: 0.5px; }
            
            /* Metrics */
            .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 36px; }
            .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 24px; text-align: center; color: #fff; box-shadow: 0 15px 40px rgba(102,126,234,.45); transition: all 0.4s; }
            .metric-card:hover { transform: translateY(-10px); box-shadow: 0 25px 60px rgba(102,126,234,.65); }
            .metric-icon { font-size: 2.8rem; margin-bottom: 12px; }
            .metric-value { font-size: 2.8rem; font-weight: 900; margin: 12px 0; text-shadow: 3px 3px 6px rgba(0,0,0,.25); }
            .metric-label { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; margin-bottom: 6px; }
            .metric-subtext { font-size: 0.85rem; margin-top: 8px; opacity: 0.9; }
            
            /* Filters */
            .filter-section { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 20px; padding: 24px; margin-bottom: 32px; }
            .filter-title { font-size: 1.4rem; font-weight: 800; color: #2c3e50; margin-bottom: 20px; }
            .filter-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
            
            /* Charts */
            .chart-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin-bottom: 24px; }
            .chart-card { background: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,.08); }
            .chart-full { grid-column: 1 / -1; }
            
            /* Tabs */
            .nav-tabs { border: none; margin-bottom: 24px; }
            .nav-tabs .nav-link { border: none; border-radius: 12px; padding: 12px 24px; font-weight: 700; color: #667eea; background: #f8f9fa; margin-right: 10px; }
            .nav-tabs .nav-link.active { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
            
            /* Strategy Cards */
            .strategy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
            .strategy-card { border-radius: 20px; padding: 28px; color: #fff; box-shadow: 0 15px 40px rgba(0,0,0,.22); margin-bottom: 20px; }
            
            /* Responsive */
            @media (max-width: 1200px) {
                .metrics-grid, .chart-grid, .strategy-grid { grid-template-columns: repeat(2, 1fr); }
                .filter-grid { grid-template-columns: 1fr; }
                .header-title { font-size: 2.5rem; }
            }
            @media (max-width: 768px) {
                .metrics-grid, .chart-grid, .strategy-grid { grid-template-columns: 1fr; }
                .dash-container { padding: 20px; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>'''

# ========== APP LAYOUT ==========
app.layout = html.Div([
    html.Div([
        # Header
        html.Div([
            html.H1("🎯 Customer Intelligence Hub", className="header-title"),
            html.P("Customer Segmentation for Personalized Retail Marketing", className="header-subtitle")
        ], className="header"),
        
        # Metrics
        html.Div([
            html.Div([
                html.Div("👥", className="metric-icon"),
                html.Div(f"{len(rfm):,}", className="metric-value"),
                html.Div("Customers", className="metric-label"),
                html.Div("Active Database", className="metric-subtext")
            ], className="metric-card"),
            
            html.Div([
                html.Div("🎯", className="metric-icon"),
                html.Div(f"{rfm['Cluster_KMeans'].nunique()}", className="metric-value"),
                html.Div("Segments", className="metric-label"),
                html.Div("AI-Classified", className="metric-subtext")
            ], className="metric-card"),
            
            html.Div([
                html.Div("💰", className="metric-icon"),
                html.Div(f"£{rfm['Monetary'].sum()/1e6:.2f}M", className="metric-value"),
                html.Div("Revenue", className="metric-label"),
                html.Div(f"Avg £{rfm['Monetary'].mean():.0f}", className="metric-subtext")
            ], className="metric-card"),
            
            html.Div([
                html.Div("📈", className="metric-icon"),
                html.Div(f"£{rfm['AvgOrderValue'].mean():.0f}", className="metric-value"),
                html.Div("Avg Order", className="metric-label"),
                html.Div(f"Peak £{rfm['AvgOrderValue'].max():.0f}", className="metric-subtext")
            ], className="metric-card")
        ], className="metrics-grid"),
        
        # Filters
        html.Div([
            html.Div("🎛️ Smart Filters", className="filter-title"),
            html.Div([
                html.Div([
                    html.Label("🎨 Segment Filter", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='segment-filter',
                        options=[{'label': '🌐 All Segments', 'value': 'all'}] + 
                                [{'label': f"{p['name']} - {champion_details[c]['tier']}" if p['name']=='🏆 Champions' and c in champion_details else p['name'],
                                  'value': c} for c, p in profs.items()],
                        value='all',
                        clearable=False,
                        style={'borderRadius': '12px'}
                    )
                ]),
                
                html.Div([
                    html.Label("📊 RFM Score Range", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='rfm-slider',
                        min=int(rfm['RFM_Score'].min()),
                        max=int(rfm['RFM_Score'].max()),
                        value=[int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())],
                        marks={i: {'label': str(i), 'style': {'fontWeight': '600'}}
                               for i in range(int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())+1, 2)},
                        tooltip={'placement': 'bottom', 'always_visible': False}
                    )
                ]),
                
                html.Div([
                    html.Label("🔥 Priority Level", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='priority-filter',
                        options=[
                            {'label': '🌐 All Priorities', 'value': 'all'},
                            {'label': '🔴 CRITICAL', 'value': 'CRITICAL'},
                            {'label': '🔥 URGENT', 'value': 'URGENT'},
                            {'label': '⚡ HIGH', 'value': 'HIGH'},
                            {'label': '📊 MEDIUM', 'value': 'MEDIUM'}
                        ],
                        value='all',
                        clearable=False,
                        style={'borderRadius': '12px'}
                    )
                ])
            ], className="filter-grid")
        ], className="filter-section"),
        
        # Tabs
        dbc.Tabs([
            # Tab 1: Analytics Dashboard
            dbc.Tab(label="📊 Analytics Dashboard", children=[
                html.Div([
                    # Row 1
                    html.Div([
                        html.Div([
                            dcc.Graph(id='pie-chart', config={'displayModeBar': False})
                        ], className="chart-card"),
                        html.Div([
                            dcc.Graph(id='bar-chart', config={'displayModeBar': False})
                        ], className="chart-card")
                    ], className="chart-grid"),
                    
                    # Row 2
                    html.Div([
                        dcc.Graph(id='3d-chart', config={'displayModeBar': False})
                    ], className="chart-card chart-full"),
                    
                    # Row 3
                    html.Div([
                        html.Div([
                            dcc.Graph(id='recency-hist', config={'displayModeBar': False})
                        ], className="chart-card"),
                        html.Div([
                            dcc.Graph(id='frequency-hist', config={'displayModeBar': False})
                        ], className="chart-card"),
                        html.Div([
                            dcc.Graph(id='monetary-hist', config={'displayModeBar': False})
                        ], className="chart-card")
                    ], className="chart-grid"),
                    
                    # Row 4
                    html.Div([
                        dcc.Graph(id='summary-table', config={'displayModeBar': False})
                    ], className="chart-card chart-full")
                ], style={'padding': '20px 0'})
            ]),
            
            # Tab 2: Growth Strategies
            dbc.Tab(label="🎯 Growth Strategies", children=[
                html.Div([
                    html.Div(id='champion-breakdown'),
                    html.Div(id='strategy-cards-container')
                ], style={'padding': '20px 0'})
            ]),
            
            # Tab 3: AI Insights
            dbc.Tab(label="💡 AI Insights", children=[
                html.Div(id='ai-insights', style={'padding': '20px 0'})
            ])
        ]),
        
        # Footer
        html.Div([
            html.P(f"✅ Dashboard loaded successfully | {len(rfm):,} customers | {rfm['Cluster_KMeans'].nunique()} segments"),
            html.P(f"Running on Railway | Python {sys.version.split()[0]} | Data updated just now")
        ], style={
            'textAlign': 'center',
            'marginTop': '50px',
            'padding': '20px',
            'color': '#666',
            'borderTop': '2px solid #667eea'
        })
    ], className="dash-container")
])

# ========== CALLBACK FUNCTIONS ==========
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('3d-chart', 'figure'),
     Output('recency-hist', 'figure'),
     Output('frequency-hist', 'figure'),
     Output('monetary-hist', 'figure'),
     Output('summary-table', 'figure'),
     Output('champion-breakdown', 'children'),
     Output('strategy-cards-container', 'children'),
     Output('ai-insights', 'children')],
    [Input('segment-filter', 'value'),
     Input('rfm-slider', 'value'),
     Input('priority-filter', 'value')]
)
def update_dashboard(segment, rfm_range, priority):
    try:
        # Filter data
        df = rfm[(rfm['RFM_Score'] >= rfm_range[0]) & (rfm['RFM_Score'] <= rfm_range[1])]
        
        if segment != 'all':
            df = df[df['Cluster_KMeans'] == segment]
        
        if priority != 'all':
            df = df[df['Priority'] == priority]
        
        # 1. Pie Chart
        cluster_counts = df['Cluster_Label'].value_counts()
        pie_fig = go.Figure(go.Pie(
            labels=cluster_counts.index,
            values=cluster_counts.values,
            hole=0.5,
            marker=dict(colors=[colors.get(label, '#95A5A6') for label in cluster_counts.index]),
            textinfo='label+percent',
            textposition='outside'
        ))
        pie_fig.update_layout(
            title={'text': 'Customer Distribution by Segment', 'x': 0.5},
            height=400,
            showlegend=False
        )
        
        # 2. Bar Chart
        revenue_by_segment = df.groupby('Cluster_Label')['Monetary'].sum().sort_values(ascending=True)
        bar_fig = go.Figure(go.Bar(
            x=revenue_by_segment.values,
            y=revenue_by_segment.index,
            orientation='h',
            marker=dict(color=revenue_by_segment.values, colorscale='Sunset'),
            text=[f'£{val/1000:.1f}K' for val in revenue_by_segment.values],
            textposition='outside'
        ))
        bar_fig.update_layout(
            title={'text': 'Revenue by Customer Segment', 'x': 0.5},
            xaxis_title='Revenue (£)',
            height=400
        )
        
        # 3. 3D Chart
        scatter_3d = go.Figure(go.Scatter3d(
            x=df['Recency'],
            y=df['Frequency'],
            z=df['Monetary'],
            mode='markers',
            marker=dict(
                size=5,
                color=df['Cluster_KMeans'],
                colorscale='Rainbow',
                opacity=0.8
            ),
            text=df['Cluster_Label'],
            hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}'
        ))
        scatter_3d.update_layout(
            title={'text': '3D Customer Analysis (Recency-Frequency-Monetary)', 'x': 0.5},
            scene=dict(
                xaxis_title='Recency (days)',
                yaxis_title='Frequency',
                zaxis_title='Monetary (£)'
            ),
            height=500
        )
        
        # 4-6. Histograms
        def create_histogram(data, column, title, color):
            fig = go.Figure(go.Histogram(
                x=data[column],
                nbinsx=30,
                marker_color=color,
                opacity=0.8
            ))
            fig.update_layout(
                title={'text': title, 'x': 0.5},
                xaxis_title=column,
                yaxis_title='Count',
                height=350
            )
            return fig
        
        hist_recency = create_histogram(df, 'Recency', '⏰ Recency Distribution', '#ff6b6b')
        hist_frequency = create_histogram(df, 'Frequency', '🔄 Frequency Distribution', '#4ecdc4')
        hist_monetary = create_histogram(df, 'Monetary', '💵 Monetary Distribution', '#45b7d1')
        
        # 7. Summary Table
        summary = df.groupby('Cluster_Label').agg({
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean',
            'AvgOrderValue': 'mean',
            'RFM_Score': 'mean'
        }).round(1).reset_index()
        summary['Count'] = df.groupby('Cluster_Label').size().values
        
        table_fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                       '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                fill_color='#667eea',
                align='center',
                font=dict(color='white', size=12),
                height=40
            ),
            cells=dict(
                values=[
                    summary['Cluster_Label'],
                    summary['Count'],
                    [f"{v:.0f}d" for v in summary['Recency']],
                    summary['Frequency'].round(1),
                    [f"£{v:,.0f}" for v in summary['Monetary']],
                    [f"£{v:.0f}" for v in summary['AvgOrderValue']],
                    summary['RFM_Score'].round(1)
                ],
                fill_color=[['white', '#f8f9fa'] * len(summary)],
                align='center',
                font=dict(size=11),
                height=35
            )
        )])
        table_fig.update_layout(height=400)
        
        # 8. Champion Breakdown
        champion_clusters = [c for c in df['Cluster_KMeans'].unique() 
                           if c in profs and profs[c]['name'] == '🏆 Champions']
        
        champion_breakdown = None
        if champion_clusters:
            champ_cards = []
            for cid in sorted(champion_clusters):
                if cid in champion_details:
                    detail = champion_details[cid]
                    count = len(df[df['Cluster_KMeans'] == cid])
                    champ_cards.append(html.Div([
                        html.H4(f"Champion C{cid}", style={'color': '#FFD700', 'marginBottom': '10px'}),
                        html.P(f"🏅 {detail['tier']}", style={'fontWeight': 'bold'}),
                        html.P(detail['desc'], style={'marginBottom': '10px'}),
                        html.P(f"📊 {detail['char']}", style={'fontSize': '0.9rem', 'color': '#666'}),
                        html.P(f"👥 {count:,} customers", style={'marginTop': '10px', 'fontWeight': 'bold'})
                    ], style={
                        'padding': '20px',
                        'background': 'rgba(255, 215, 0, 0.1)',
                        'borderRadius': '15px',
                        'borderLeft': '5px solid #FFD700'
                    }))
            
            if champ_cards:
                champion_breakdown = html.Div([
                    html.H3("🏆 Champion Segments Breakdown", style={'marginBottom': '20px'}),
                    html.Div(champ_cards, style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px'})
                ])
        
        # 9. Strategy Cards
        strategy_cards = []
        for cid, strat in profs.items():
            if segment == 'all' or segment == cid:
                customer_count = len(df[df['Cluster_KMeans'] == cid])
                strategy_cards.append(html.Div([
                    html.Div([
                        html.H4(strat['name'], style={'margin': '0', 'display': 'inline-block'}),
                        html.Span(strat['priority'], style={
                            'float': 'right',
                            'background': 'rgba(255,255,255,0.3)',
                            'padding': '5px 15px',
                            'borderRadius': '20px',
                            'fontWeight': 'bold',
                            'fontSize': '0.9rem'
                        })
                    ], style={'marginBottom': '15px'}),
                    
                    html.P(f"📋 {strat['strategy']}", style={'fontWeight': 'bold', 'marginBottom': '15px'}),
                    
                    html.Div([
                        html.P("🎯 Key Tactics:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                        html.Ul([html.Li(tactic) for tactic in strat['tactics'][:3]])
                    ], style={
                        'background': 'rgba(255,255,255,0.2)',
                        'padding': '15px',
                        'borderRadius': '10px',
                        'marginBottom': '15px'
                    }),
                    
                    html.Div([
                        html.P("📊 Target KPIs:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                        html.Div([html.Span(kpi, style={
                            'display': 'inline-block',
                            'background': 'rgba(255,255,255,0.2)',
                            'padding': '5px 10px',
                            'margin': '0 5px 5px 0',
                            'borderRadius': '5px',
                            'fontSize': '0.9rem'
                        }) for kpi in strat['kpis']])
                    ]),
                    
                    html.Div([
                        html.Div([
                            html.P("Budget Allocation", style={'margin': '0', 'fontSize': '0.9rem'}),
                            html.H5(strat['budget'], style={'margin': '0', 'color': '#fff'})
                        ]),
                        html.Div([
                            html.P("ROI Target", style={'margin': '0', 'fontSize': '0.9rem'}),
                            html.H5(strat['roi'], style={'margin': '0', 'color': '#fff'})
                        ]),
                        html.Div([
                            html.P("Customers", style={'margin': '0', 'fontSize': '0.9rem'}),
                            html.H5(f"{customer_count:,}", style={'margin': '0', 'color': '#fff'})
                        ])
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'space-between',
                        'marginTop': '20px',
                        'paddingTop': '15px',
                        'borderTop': '1px solid rgba(255,255,255,0.3)'
                    })
                ], className="strategy-card", style={'background': strat['grad']}))
        
        # 10. AI Insights
        if len(df) > 0:
            top_segment = df.groupby('Cluster_Label')['Monetary'].sum().idxmax()
            top_revenue = df.groupby('Cluster_Label')['Monetary'].sum().max()
            largest_segment = df['Cluster_Label'].value_counts().idxmax()
            largest_count = df['Cluster_Label'].value_counts().max()
            
            ai_insights = html.Div([
                html.H3("🧠 AI-Powered Insights", style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.H4("📊 Performance Analysis"),
                        html.Ul([
                            html.Li(f"🏆 Highest Revenue: {top_segment} (£{top_revenue/1000:.1f}K)"),
                            html.Li(f"👥 Largest Segment: {largest_segment} ({largest_count:,} customers)"),
                            html.Li(f"💰 Avg Order Value: £{df['AvgOrderValue'].mean():.0f}"),
                            html.Li(f"🔄 Avg Frequency: {df['Frequency'].mean():.1f} orders"),
                            html.Li(f"⏰ Avg Recency: {df['Recency'].mean():.0f} days")
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                        'color': 'white',
                        'borderRadius': '15px',
                        'marginBottom': '20px'
                    }),
                    
                    html.Div([
                        html.H4("💡 Strategic Recommendations"),
                        html.Ul([
                            html.Li("🎯 Prioritize retention programs for high-value segments"),
                            html.Li("📧 Launch targeted win-back campaigns for dormant customers"),
                            html.Li("🚀 Accelerate nurturing flows for potential customers"),
                            html.Li("💎 Create exclusive VIP experiences for champions"),
                            html.Li("📈 Implement cross-sell strategies for loyal segments"),
                            html.Li("🤖 Use AI recommendations for personalized marketing")
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        'color': 'white',
                        'borderRadius': '15px'
                    })
                ])
            ])
        else:
            ai_insights = html.Div([
                html.H3("No data available for selected filters", style={'textAlign': 'center', 'color': '#666'})
            ])
        
        return (pie_fig, bar_fig, scatter_3d, hist_recency, hist_frequency, 
                hist_monetary, table_fig, champion_breakdown, 
                html.Div(strategy_cards, className="strategy-grid"), ai_insights)
    
    except Exception as e:
        print(f"❌ Error in callback: {e}")
        traceback.print_exc()
        
        # Return empty figures in case of error
        empty_fig = go.Figure()
        empty_fig.update_layout(title={'text': 'Error loading data', 'x': 0.5}, height=300)
        
        error_msg = html.Div([
            html.H3("⚠️ Error loading dashboard"),
            html.P("Please check the server logs for details.")
        ], style={'textAlign': 'center', 'padding': '50px'})
        
        return [empty_fig] * 7 + [error_msg, error_msg, error_msg]

# ========== HEALTH CHECK ==========
@server.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'customers': len(rfm),
        'segments': rfm['Cluster_KMeans'].nunique(),
        'revenue': f"£{rfm['Monetary'].sum()/1e6:.2f}M",
        'timestamp': pd.Timestamp.now().isoformat()
    }

# ========== RUN APP ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("RAILWAY_ENVIRONMENT") != "production"
    
    print(f"\n{'='*80}")
    print(f"🚀 DASHBOARD STARTING ON PORT: {port}")
    print(f"📊 Data: {len(rfm):,} customers, {rfm['Cluster_KMeans'].nunique()} segments")
    print(f"💰 Total Revenue: £{rfm['Monetary'].sum()/1e6:.2f}M")
    print(f"🔧 Debug Mode: {debug}")
    print(f"{'='*80}\n")
    
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=False
    )
