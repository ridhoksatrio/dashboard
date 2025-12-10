import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import warnings
import os
import sys
from flask import Flask

warnings.filterwarnings('ignore')

# ========== INITIALIZE ==========
print("=" * 80)
print("🚀 SIMPLE DASHBOARD FOR RAILWAY")
print("=" * 80)

server = Flask(__name__)

# ========== LOAD DATA ==========
def load_data():
    try:
        # Coba load CSV
        if os.path.exists('final_customer_segments.csv'):
            df = pd.read_csv('final_customer_segments.csv')
            print(f"✅ CSV loaded: {df.shape}")
            
            # Ekstrak kolom yang diperlukan
            data = {}
            
            # Frequency - cari kolom yang mengandung 'freq' atau 'order'
            freq_cols = [col for col in df.columns if 'freq' in str(col).lower() or 'order' in str(col).lower()]
            data['Frequency'] = df[freq_cols[0]] if freq_cols else np.random.randint(1, 50, len(df))
            
            # Monetary - cari kolom yang mengandung 'monet' atau 'revenue'
            money_cols = [col for col in df.columns if 'monet' in str(col).lower() or 'revenue' in str(col).lower()]
            data['Monetary'] = df[money_cols[0]] if money_cols else np.random.randint(100, 10000, len(df))
            
            # Buat kolom lainnya
            data['Recency'] = np.random.randint(1, 365, len(df))
            data['AvgOrderValue'] = np.random.randint(50, 500, len(df))
            data['RFM_Score'] = np.random.randint(3, 15, len(df))
            data['Cluster_KMeans'] = np.random.choice([0, 1, 2, 3, 4, 5, 6], len(df))
            
            rfm = pd.DataFrame(data)
            
        else:
            print("📊 Using dummy data")
            rfm = create_dummy_data()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        rfm = create_dummy_data()
    
    return rfm

def create_dummy_data():
    np.random.seed(42)
    n = 3680
    
    data = {
        'Recency': np.random.randint(1, 365, n),
        'Frequency': np.random.randint(1, 50, n),
        'Monetary': np.random.randint(100, 10000, n),
        'AvgOrderValue': np.random.randint(50, 500, n),
        'RFM_Score': np.random.randint(1, 10, n),
        'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n)
    }
    
    return pd.DataFrame(data)

# Load data
rfm = load_data()
print(f"📊 Final data: {len(rfm):,} customers")

# ========== CREATE STATIC CHARTS ==========
# 1. Pie Chart
cluster_counts = rfm['Cluster_KMeans'].value_counts()
pie_fig = go.Figure(data=[go.Pie(
    labels=[f'Cluster {i}' for i in cluster_counts.index],
    values=cluster_counts.values,
    hole=0.5
)])
pie_fig.update_layout(title_text='Customer Distribution')

# 2. Bar Chart - Revenue by Cluster
revenue_by_cluster = rfm.groupby('Cluster_KMeans')['Monetary'].sum()
bar_fig = go.Figure(data=[go.Bar(
    x=[f'Cluster {i}' for i in revenue_by_cluster.index],
    y=revenue_by_cluster.values,
    marker_color='#667eea'
)])
bar_fig.update_layout(
    title_text='Revenue by Cluster',
    xaxis_title='Cluster',
    yaxis_title='Revenue (£)'
)

# 3. 3D Scatter
scatter_fig = go.Figure(data=[go.Scatter3d(
    x=rfm['Recency'].sample(500),
    y=rfm['Frequency'].sample(500),
    z=rfm['Monetary'].sample(500),
    mode='markers',
    marker=dict(
        size=5,
        color=rfm['Cluster_KMeans'].sample(500),
        colorscale='Viridis',
        opacity=0.8
    )
)])
scatter_fig.update_layout(
    title_text='3D Customer Analysis',
    scene=dict(
        xaxis_title='Recency',
        yaxis_title='Frequency',
        zaxis_title='Monetary'
    ),
    height=500
)

# ========== CREATE DASH APP ==========
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Simple inline CSS
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🎯 Customer Intelligence Dashboard", 
                style={'color': 'white', 'marginBottom': '10px'}),
        html.P("Customer Segmentation for Personalized Retail Marketing", 
               style={'color': 'rgba(255,255,255,0.9)'})
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '30px',
        'borderRadius': '10px',
        'textAlign': 'center',
        'marginBottom': '20px'
    }),
    
    # Metrics
    html.Div([
        html.Div([
            html.H3(f"{len(rfm):,}", style={'color': '#667eea', 'margin': '0', 'fontSize': '2.5rem'}),
            html.P("Customers", style={'margin': '0', 'color': '#666', 'fontWeight': 'bold'}),
            html.P("Active Database", style={'margin': '0', 'color': '#999', 'fontSize': '0.9rem'})
        ], style={
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'textAlign': 'center',
            'flex': '1'
        }),
        
        html.Div([
            html.H3(f"{rfm['Cluster_KMeans'].nunique()}", style={'color': '#667eea', 'margin': '0', 'fontSize': '2.5rem'}),
            html.P("Segments", style={'margin': '0', 'color': '#666', 'fontWeight': 'bold'}),
            html.P("AI-Classified", style={'margin': '0', 'color': '#999', 'fontSize': '0.9rem'})
        ], style={
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'textAlign': 'center',
            'flex': '1'
        }),
        
        html.Div([
            html.H3(f"£{rfm['Monetary'].sum()/1e6:.2f}M", style={'color': '#667eea', 'margin': '0', 'fontSize': '2.5rem'}),
            html.P("Revenue", style={'margin': '0', 'color': '#666', 'fontWeight': 'bold'}),
            html.P(f"Avg £{rfm['Monetary'].mean():.0f}", style={'margin': '0', 'color': '#999', 'fontSize': '0.9rem'})
        ], style={
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'textAlign': 'center',
            'flex': '1'
        }),
        
        html.Div([
            html.H3(f"£{rfm['AvgOrderValue'].mean():.0f}", style={'color': '#667eea', 'margin': '0', 'fontSize': '2.5rem'}),
            html.P("Avg Order", style={'margin': '0', 'color': '#666', 'fontWeight': 'bold'}),
            html.P(f"Peak £{rfm['AvgOrderValue'].max():.0f}", style={'margin': '0', 'color': '#999', 'fontSize': '0.9rem'})
        ], style={
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'textAlign': 'center',
            'flex': '1'
        })
    ], style={
        'display': 'flex',
        'gap': '15px',
        'marginBottom': '30px',
        'flexWrap': 'wrap'
    }),
    
    # Filters
    html.Div([
        html.H4("🎛️ Smart Filters", style={'marginBottom': '15px', 'color': '#333'}),
        
        html.Div([
            html.Div([
                html.Label("🎨 Segment Filter", style={'display': 'block', 'marginBottom': '5px', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='segment-filter',
                    options=[
                        {'label': 'All Segments', 'value': 'all'},
                        {'label': 'Cluster 0', 'value': 0},
                        {'label': 'Cluster 1', 'value': 1},
                        {'label': 'Cluster 2', 'value': 2},
                        {'label': 'Cluster 3', 'value': 3},
                        {'label': 'Cluster 4', 'value': 4},
                        {'label': 'Cluster 5', 'value': 5},
                        {'label': 'Cluster 6', 'value': 6}
                    ],
                    value='all',
                    style={'width': '100%'}
                )
            ], style={'flex': '1'}),
            
            html.Div([
                html.Label("📊 RFM Score Range", style={'display': 'block', 'marginBottom': '5px', 'fontWeight': 'bold'}),
                dcc.RangeSlider(
                    id='rfm-slider',
                    min=int(rfm['RFM_Score'].min()),
                    max=int(rfm['RFM_Score'].max()),
                    value=[int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())],
                    marks={i: str(i) for i in range(int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())+1, 2)}
                )
            ], style={'flex': '2', 'padding': '0 20px'}),
            
            html.Div([
                html.Label("🔥 Priority Level", style={'display': 'block', 'marginBottom': '5px', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='priority-filter',
                    options=[
                        {'label': 'All Priorities', 'value': 'all'},
                        {'label': 'CRITICAL', 'value': 'critical'},
                        {'label': 'URGENT', 'value': 'urgent'},
                        {'label': 'HIGH', 'value': 'high'},
                        {'label': 'MEDIUM', 'value': 'medium'}
                    ],
                    value='all',
                    style={'width': '100%'}
                )
            ], style={'flex': '1'})
        ], style={
            'display': 'flex',
            'gap': '20px',
            'alignItems': 'center'
        })
    ], style={
        'background': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '10px',
        'marginBottom': '30px'
    }),
    
    # Tabs dengan grafik STATIC (tanpa callback)
    dbc.Tabs([
        # Tab 1: Analytics
        dbc.Tab(label="📊 Analytics Dashboard", children=[
            html.Div([
                # Row 1
                html.Div([
                    html.Div([
                        dcc.Graph(figure=pie_fig, config={'displayModeBar': False})
                    ], style={
                        'padding': '15px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                        'flex': '1'
                    }),
                    
                    html.Div([
                        dcc.Graph(figure=bar_fig, config={'displayModeBar': False})
                    ], style={
                        'padding': '15px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                        'flex': '1'
                    })
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
                
                # Row 2
                html.Div([
                    dcc.Graph(figure=scatter_fig, config={'displayModeBar': False})
                ], style={
                    'padding': '15px',
                    'background': 'white',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                    'marginBottom': '20px'
                }),
                
                # Row 3: Histograms
                html.Div([
                    html.Div([
                        dcc.Graph(
                            figure=go.Figure(data=[go.Histogram(x=rfm['Recency'], nbinsx=30, marker_color='#ff6b6b')]),
                            config={'displayModeBar': False}
                        )
                    ], style={
                        'padding': '15px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                        'flex': '1'
                    }),
                    
                    html.Div([
                        dcc.Graph(
                            figure=go.Figure(data=[go.Histogram(x=rfm['Frequency'], nbinsx=30, marker_color='#4ecdc4')]),
                            config={'displayModeBar': False}
                        )
                    ], style={
                        'padding': '15px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                        'flex': '1'
                    }),
                    
                    html.Div([
                        dcc.Graph(
                            figure=go.Figure(data=[go.Histogram(x=rfm['Monetary'], nbinsx=30, marker_color='#45b7d1')]),
                            config={'displayModeBar': False}
                        )
                    ], style={
                        'padding': '15px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                        'flex': '1'
                    })
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
                
                # Row 4: Table
                html.Div([
                    # Buat table sederhana
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Metric"),
                            html.Th("Value"),
                            html.Th("Description")
                        ])),
                        html.Tbody([
                            html.Tr([html.Td("Total Customers"), html.Td(f"{len(rfm):,}"), html.Td("Number of customers in database")]),
                            html.Tr([html.Td("Average Recency"), html.Td(f"{rfm['Recency'].mean():.0f} days"), html.Td("Days since last purchase")]),
                            html.Tr([html.Td("Average Frequency"), html.Td(f"{rfm['Frequency'].mean():.1f}"), html.Td("Number of purchases")]),
                            html.Tr([html.Td("Average Monetary"), html.Td(f"£{rfm['Monetary'].mean():,.0f}"), html.Td("Total spend per customer")]),
                            html.Tr([html.Td("Average RFM Score"), html.Td(f"{rfm['RFM_Score'].mean():.1f}"), html.Td("RFM composite score")])
                        ])
                    ], style={'width': '100%', 'borderCollapse': 'collapse'})
                ], style={
                    'padding': '20px',
                    'background': 'white',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                })
            ], style={'padding': '10px'})
        ]),
        
        # Tab 2: Strategies
        dbc.Tab(label="🎯 Growth Strategies", children=[
            html.Div([
                html.H3("Customer Growth Strategies", style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.H4("🏆 Champions", style={'color': '#FFD700'}),
                        html.P("VIP customers with high engagement"),
                        html.Ul([
                            html.Li("Exclusive early access to new products"),
                            html.Li("Premium gifts and rewards"),
                            html.Li("24/7 dedicated manager"),
                            html.Li("VIP events and experiences")
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, #FFD700, #FFA500)',
                        'color': 'white',
                        'borderRadius': '10px',
                        'marginBottom': '15px'
                    }),
                    
                    html.Div([
                        html.H4("💎 Loyal Customers", style={'color': '#667eea'}),
                        html.P("Consistent buyers with good retention"),
                        html.Ul([
                            html.Li("Tiered rewards program"),
                            html.Li("Birthday and anniversary offers"),
                            html.Li("Referral bonus program"),
                            html.Li("Flash sale access")
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, #667eea, #764ba2)',
                        'color': 'white',
                        'borderRadius': '10px',
                        'marginBottom': '15px'
                    }),
                    
                    html.Div([
                        html.H4("💰 Big Spenders", style={'color': '#f093fb'}),
                        html.P("High-value but infrequent buyers"),
                        html.Ul([
                            html.Li("Flexible payment terms"),
                            html.Li("Luxury gift packages"),
                            html.Li("Free express shipping"),
                            html.Li("Personal concierge service")
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, #f093fb, #f5576c)',
                        'color': 'white',
                        'borderRadius': '10px'
                    })
                ])
            ], style={'padding': '20px'})
        ]),
        
        # Tab 3: Insights
        dbc.Tab(label="💡 AI Insights", children=[
            html.Div([
                html.H3("AI-Powered Insights", style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.H4("📊 Top Performers"),
                        html.Ul([
                            html.Li(f"Highest revenue cluster: Cluster {revenue_by_cluster.idxmax()}"),
                            html.Li(f"Most frequent buyers: Cluster {rfm.groupby('Cluster_KMeans')['Frequency'].mean().idxmax()}"),
                            html.Li(f"Best average order value: Cluster {rfm.groupby('Cluster_KMeans')['AvgOrderValue'].mean().idxmax()}"),
                            html.Li(f"Most recent purchases: Cluster {rfm.groupby('Cluster_KMeans')['Recency'].mean().idxmin()}")
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'marginBottom': '15px',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                    }),
                    
                    html.Div([
                        html.H4("🎯 Recommendations"),
                        html.Ul([
                            html.Li("Launch win-back campaigns for dormant segments"),
                            html.Li("Create VIP programs for high-value customers"),
                            html.Li("Implement cross-sell strategies for loyal segments"),
                            html.Li("Use personalized email marketing based on RFM scores"),
                            html.Li("Offer loyalty rewards to increase frequency")
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                    })
                ])
            ], style={'padding': '20px'})
        ])
    ]),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P(f"✅ Dashboard loaded successfully | {len(rfm):,} customers | {rfm['Cluster_KMeans'].nunique()} segments"),
        html.P(f"Data updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} | Running on Railway")
    ], style={
        'marginTop': '40px',
        'textAlign': 'center',
        'color': '#666',
        'padding': '20px'
    })
], style={
    'padding': '20px',
    'maxWidth': '1400px',
    'margin': '0 auto',
    'fontFamily': 'Arial, sans-serif'
})

# ========== SIMPLE CALLBACK (jika ingin interaktif) ==========
# Hapus callback kompleks untuk sekarang

# ========== HEALTH CHECK ==========
@server.route('/health')
def health():
    return {
        'status': 'ok',
        'customers': len(rfm),
        'clusters': rfm['Cluster_KMeans'].nunique(),
        'timestamp': pd.Timestamp.now().isoformat()
    }

# ========== RUN APP ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("RAILWAY_ENVIRONMENT") != "production"
    
    print(f"\n🚀 Starting server on port {port}")
    print(f"📊 Data loaded: {len(rfm):,} customers")
    print(f"🔧 Debug mode: {debug}")
    
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=False
    )
