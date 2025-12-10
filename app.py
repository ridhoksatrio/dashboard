import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import warnings
import os
import sys
from flask import Flask
import traceback

warnings.filterwarnings('ignore')

# ========== DEBUG INFO ==========
print("=" * 80)
print("🚀 CUSTOMER INTELLIGENCE DASHBOARD - OPTIMIZED FOR DEPLOYMENT")
print("=" * 80)
print(f"Python: {sys.version}")
print(f"Current dir: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# ========== FLASK SERVER ==========
server = Flask(__name__)

# ========== LOAD DATA (ROBUST VERSION) ==========
def load_data():
    """Load data with robust error handling"""
    try:
        # Cek file CSV yang mungkin ada
        csv_files = ['final_customer_segments (1).csv', 'final_customer_segments.csv']
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                print(f"📂 Found CSV file: {csv_file}")
                print(f"   Size: {os.path.getsize(csv_file):,} bytes")
                
                try:
                    # Coba baca dengan index_col=0 seperti kode kedua
                    df = pd.read_csv(csv_file, index_col=0)
                    print(f"✅ CSV loaded successfully: {df.shape}")
                    print(f"   Columns: {df.columns.tolist()}")
                    
                    # Cek kolom yang diperlukan
                    required_cols = ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score', 'Cluster_KMeans']
                    
                    # Jika ada kolom 'Customer Category', kita bisa gunakan untuk mapping
                    if 'Customer Category' in df.columns:
                        print("   Found 'Customer Category' column, mapping to Cluster_KMeans")
                        category_map = {
                            'Champion': 1, 'Champions': 1,
                            'Loyal': 2,
                            'At Risk': 3,
                            'Cannot Lose': 4,
                            'Others': 5, 'Other': 5
                        }
                        df['Cluster_KMeans'] = df['Customer Category'].map(category_map).fillna(0).astype(int)
                    
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    
                    if missing_cols:
                        print(f"⚠️ Missing columns: {missing_cols}")
                        print("🔄 Creating missing columns...")
                        
                        # Tambahkan kolom yang hilang berdasarkan data yang ada
                        if 'Recency' not in df.columns:
                            df['Recency'] = np.random.randint(1, 365, len(df))
                        if 'Frequency' not in df.columns:
                            df['Frequency'] = np.random.randint(1, 50, len(df))
                        if 'Monetary' not in df.columns:
                            df['Monetary'] = np.random.randint(100, 10000, len(df))
                        if 'AvgOrderValue' not in df.columns:
                            df['AvgOrderValue'] = (df['Monetary'] / df['Frequency']).clip(lower=50, upper=5000)
                        if 'RFM_Score' not in df.columns:
                            df['RFM_Score'] = np.random.randint(1, 10, len(df))
                        if 'Cluster_KMeans' not in df.columns:
                            df['Cluster_KMeans'] = np.random.choice([0, 1, 2, 3, 4, 5, 6], len(df))
                    
                    print("✅ Data preparation complete")
                    return df
                        
                except Exception as e:
                    print(f"❌ Error reading {csv_file}: {e}")
                    continue
                    
        print("📂 No valid CSV found, using enhanced dummy data")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
    
    # Fallback: Enhanced dummy data
    return create_enhanced_data()

def create_enhanced_data():
    """Create realistic data matching your CSV structure"""
    np.random.seed(42)
    n = 3680  # Match your data size
    
    print(f"📊 Creating enhanced data with {n} customers")
    
    # Create more realistic distributions
    # Recency: Most customers purchased recently (skewed right)
    recency = np.random.exponential(30, n).astype(int) + 1
    recency = np.clip(recency, 1, 365)
    
    # Frequency: Most customers have few purchases (skewed right)
    frequency = np.random.poisson(5, n) + 1
    frequency = np.clip(frequency, 1, 100)
    
    # Monetary: Most customers spend small amounts (skewed right)
    monetary = np.random.exponential(500, n).astype(int) + 50
    monetary = np.clip(monetary, 50, 20000)
    
    # Create base data
    data = {
        'Recency': recency,
        'Frequency': frequency,
        'Monetary': monetary,
        'AvgOrderValue': (monetary / frequency).clip(lower=20, upper=1000),
        'RFM_Score': np.random.randint(1, 10, n),
        'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n, p=[0.15, 0.2, 0.15, 0.1, 0.15, 0.1, 0.15])
    }
    
    # Enhance for specific clusters
    # Cluster 1: Champions - recent, frequent, high spend
    mask = data['Cluster_KMeans'] == 1
    data['Recency'] = np.where(mask, np.random.randint(1, 30, n), data['Recency'])
    data['Frequency'] = np.where(mask, np.random.randint(10, 50, n), data['Frequency'])
    data['Monetary'] = np.where(mask, np.random.randint(2000, 20000, n), data['Monetary'])
    
    # Cluster 0: Dormant - not recent, infrequent, low spend
    mask = data['Cluster_KMeans'] == 0
    data['Recency'] = np.where(mask, np.random.randint(200, 365, n), data['Recency'])
    data['Frequency'] = np.where(mask, np.random.randint(1, 5, n), data['Frequency'])
    data['Monetary'] = np.where(mask, np.random.randint(50, 500, n), data['Monetary'])
    
    rfm = pd.DataFrame(data)
    print(f"✅ Enhanced data created: {rfm.shape}")
    return rfm

# Load data
rfm = load_data()
print(f"\n📊 DATA SUMMARY:")
print(f"   Customers: {len(rfm):,}")
print(f"   Clusters: {rfm['Cluster_KMeans'].nunique()}")
print(f"   Revenue: £{rfm['Monetary'].sum()/1e6:.2f}M")
print(f"   Avg Order: £{rfm['AvgOrderValue'].mean():.0f}")

# ========== DASH APP ==========
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    update_title=None
)

# ========== CREATE HISTOGRAMS LIKE IN THE SECOND IMAGE ==========
def create_distribution_histograms(data):
    """Create histograms like in the second image"""
    figures = []
    
    # 1. Recency Distribution
    fig1 = go.Figure()
    fig1.add_trace(go.Histogram(
        x=data['Recency'],
        nbinsx=30,
        marker_color='#667eea',
        opacity=0.8,
        name='Recency',
        hovertemplate='Days: %{x}<br>Customers: %{y}<extra></extra>'
    ))
    fig1.update_layout(
        title={'text': '<b>Recovery Distribution</b>', 'x': 0.5, 'y': 0.95,
               'font': {'size': 18, 'color': '#2c3e50'}},
        xaxis={'title': '<b>Days Since Last Purchase</b>', 
               'titlefont': {'size': 14},
               'gridcolor': 'rgba(0,0,0,0.05)'},
        yaxis={'title': '<b>Number of Customers</b>', 
               'titlefont': {'size': 14},
               'gridcolor': 'rgba(0,0,0,0.05)',
               'rangemode': 'tozero'},
        height=350,
        plot_bgcolor='white',
        margin=dict(t=60, b=60, l=60, r=30),
        bargap=0.1,
        showlegend=False
    )
    figures.append(fig1)
    
    # 2. Frequency Distribution
    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(
        x=data['Frequency'],
        nbinsx=20,
        marker_color='#38ef7d',
        opacity=0.8,
        name='Frequency',
        hovertemplate='Purchases: %{x}<br>Customers: %{y}<extra></extra>'
    ))
    fig2.update_layout(
        title={'text': '<b>Frequency Distribution</b>', 'x': 0.5, 'y': 0.95,
               'font': {'size': 18, 'color': '#2c3e50'}},
        xaxis={'title': '<b>Number of Purchases</b>', 
               'titlefont': {'size': 14},
               'gridcolor': 'rgba(0,0,0,0.05)'},
        yaxis={'title': '<b>Number of Customers</b>', 
               'titlefont': {'size': 14},
               'gridcolor': 'rgba(0,0,0,0.05)',
               'rangemode': 'tozero'},
        height=350,
        plot_bgcolor='white',
        margin=dict(t=60, b=60, l=60, r=30),
        bargap=0.1,
        showlegend=False
    )
    figures.append(fig2)
    
    # 3. Monetary Distribution
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=data['Monetary'],
        nbinsx=30,
        marker_color='#f093fb',
        opacity=0.8,
        name='Monetary',
        hovertemplate='Spend: £%{x}<br>Customers: %{y}<extra></extra>'
    ))
    fig3.update_layout(
        title={'text': '<b>Monetary Distribution</b>', 'x': 0.5, 'y': 0.95,
               'font': {'size': 18, 'color': '#2c3e50'}},
        xaxis={'title': '<b>Total Spend (£)</b>', 
               'titlefont': {'size': 14},
               'gridcolor': 'rgba(0,0,0,0.05)'},
        yaxis={'title': '<b>Number of Customers</b>', 
               'titlefont': {'size': 14},
               'gridcolor': 'rgba(0,0,0,0.05)',
               'rangemode': 'tozero'},
        height=350,
        plot_bgcolor='white',
        margin=dict(t=60, b=60, l=60, r=30),
        bargap=0.1,
        showlegend=False
    )
    figures.append(fig3)
    
    return figures

# ========== CREATE OTHER FIGURES ==========
def create_other_figures(data):
    """Create other dashboard figures"""
    figures = []
    
    # 1. Customer Distribution Pie
    try:
        cluster_counts = data['Cluster_KMeans'].value_counts()
        pie_fig = go.Figure(go.Pie(
            labels=[f'Segment {i}' for i in cluster_counts.index],
            values=cluster_counts.values,
            hole=0.5,
            marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#ff6b6b', '#38ef7d', '#45b7d1']),
            textinfo='percent+label',
            textposition='outside'
        ))
        pie_fig.update_layout(
            title={'text': '<b>Customer Segments</b>', 'x': 0.5},
            height=400,
            showlegend=True,
            margin=dict(t=50, b=30, l=30, r=30)
        )
        figures.append(pie_fig)
    except:
        figures.append(go.Figure())
    
    # 2. Revenue by Segment Bar
    try:
        revenue_by_cluster = data.groupby('Cluster_KMeans')['Monetary'].sum()
        bar_fig = go.Figure(go.Bar(
            x=[f'Segment {i}' for i in revenue_by_cluster.index],
            y=revenue_by_cluster.values,
            marker_color=['#667eea', '#764ba2', '#f093fb', '#ff6b6b', '#38ef7d', '#45b7d1']
        ))
        bar_fig.update_layout(
            title={'text': '<b>Revenue by Segment</b>', 'x': 0.5},
            xaxis={'title': 'Segment'},
            yaxis={'title': 'Revenue (£)'},
            height=400,
            plot_bgcolor='rgba(0,0,0,0.02)'
        )
        figures.append(bar_fig)
    except:
        figures.append(go.Figure())
    
    return figures

# Create initial figures
dist_figures = create_distribution_histograms(rfm)
other_figures = create_other_figures(rfm)

# ========== APP LAYOUT ==========
app.layout = html.Div([
    html.Div([
        # Header
        html.Div([
            html.H1("📊 Customer Analytics Dashboard", 
                   style={'color': 'white', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.P("RFM Analysis & Customer Segmentation", 
                  style={'color': 'white', 'textAlign': 'center', 'fontSize': '18px'})
        ], style={'backgroundColor': '#667eea', 'padding': '30px', 'borderRadius': '10px', 
                 'marginBottom': '30px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'}),
        
        # Metrics Summary
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Customers", className="card-title"),
                        html.H2(f"{len(rfm):,}", className="card-text", 
                               style={'color': '#667eea', 'fontWeight': 'bold'}),
                        html.Small("Active database", className="text-muted")
                    ])
                ], className="shadow-sm")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Revenue", className="card-title"),
                        html.H2(f"£{rfm['Monetary'].sum()/1e6:.2f}M", className="card-text",
                               style={'color': '#28a745', 'fontWeight': 'bold'}),
                        html.Small(f"Avg £{rfm['Monetary'].mean():.0f}", className="text-muted")
                    ])
                ], className="shadow-sm")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Avg Frequency", className="card-title"),
                        html.H2(f"{rfm['Frequency'].mean():.1f}", className="card-text",
                               style={'color': '#ffc107', 'fontWeight': 'bold'}),
                        html.Small("Purchases per customer", className="text-muted")
                    ])
                ], className="shadow-sm")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Avg Recency", className="card-title"),
                        html.H2(f"{rfm['Recency'].mean():.0f} days", className="card-text",
                               style={'color': '#dc3545', 'fontWeight': 'bold'}),
                        html.Small("Days since last purchase", className="text-muted")
                    ])
                ], className="shadow-sm")
            ], width=3),
        ], className="mb-4"),
        
        # Distribution Charts Section
        html.H3("📈 Distribution Analysis", style={'marginTop': '30px', 'marginBottom': '20px'}),
        html.P("Customer behavior distributions based on RFM metrics", 
              style={'color': '#666', 'marginBottom': '30px'}),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recovery Distribution", 
                                  style={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(
                            id='recency-histogram',
                            figure=dist_figures[0],
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm h-100")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Frequency Distribution", 
                                  style={'backgroundColor': '#38ef7d', 'color': 'black', 'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(
                            id='frequency-histogram',
                            figure=dist_figures[1],
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm h-100")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Monetary Distribution", 
                                  style={'backgroundColor': '#f093fb', 'color': 'black', 'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(
                            id='monetary-histogram',
                            figure=dist_figures[2],
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm h-100")
            ], width=4),
        ], className="mb-5"),
        
        # Other Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Customer Segments", style={'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(
                            id='segment-pie',
                            figure=other_figures[0],
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Revenue by Segment", style={'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(
                            id='revenue-bar',
                            figure=other_figures[1],
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
        ], className="mb-4"),
        
        # Data Summary Table
        dbc.Card([
            dbc.CardHeader("Data Summary", style={'fontWeight': 'bold'}),
            dbc.CardBody([
                dbc.Table([
                    html.Thead(
                        html.Tr([
                            html.Th("Metric"),
                            html.Th("Value"),
                            html.Th("Min"),
                            html.Th("Max"),
                            html.Th("Avg")
                        ])
                    ),
                    html.Tbody([
                        html.Tr([
                            html.Td("Recency (days)"),
                            html.Td(f"{len(rfm)}"),
                            html.Td(f"{rfm['Recency'].min()}"),
                            html.Td(f"{rfm['Recency'].max()}"),
                            html.Td(f"{rfm['Recency'].mean():.1f}")
                        ]),
                        html.Tr([
                            html.Td("Frequency"),
                            html.Td(f"{len(rfm)}"),
                            html.Td(f"{rfm['Frequency'].min()}"),
                            html.Td(f"{rfm['Frequency'].max()}"),
                            html.Td(f"{rfm['Frequency'].mean():.1f}")
                        ]),
                        html.Tr([
                            html.Td("Monetary (£)"),
                            html.Td(f"{len(rfm)}"),
                            html.Td(f"£{rfm['Monetary'].min():,.0f}"),
                            html.Td(f"£{rfm['Monetary'].max():,.0f}"),
                            html.Td(f"£{rfm['Monetary'].mean():,.0f}")
                        ])
                    ])
                ], bordered=True, hover=True, responsive=True)
            ])
        ], className="mb-4"),
        
        # Footer
        html.Div([
            html.Hr(),
            html.P([
                "Dashboard created with ",
                html.Span("❤️", style={'color': 'red'}),
                " using Plotly Dash | ",
                f"Data: {len(rfm):,} customers | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"
            ], style={'textAlign': 'center', 'color': '#666', 'marginTop': '20px', 'paddingBottom': '20px'})
        ])
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '20px'})
])

# ========== CALLBACK FOR FILTERING ==========
@app.callback(
    [Output('recency-histogram', 'figure'),
     Output('frequency-histogram', 'figure'),
     Output('monetary-histogram', 'figure'),
     Output('segment-pie', 'figure'),
     Output('revenue-bar', 'figure')],
    [Input('recency-histogram', 'relayoutData')]  # Placeholder for filters
)
def update_charts(relayout_data):
    """Update charts based on filters"""
    # For now, just return the initial figures
    # In a real app, you would filter data based on user input
    return dist_figures + other_figures

# ========== RUN APP ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"\n{'='*80}")
    print(f"🚀 STARTING DASHBOARD ON PORT: {port}")
    print(f"📊 Data Statistics:")
    print(f"   - Recency: Min={rfm['Recency'].min()}, Max={rfm['Recency'].max()}, Mean={rfm['Recency'].mean():.1f}")
    print(f"   - Frequency: Min={rfm['Frequency'].min()}, Max={rfm['Frequency'].max()}, Mean={rfm['Frequency'].mean():.1f}")
    print(f"   - Monetary: Min=£{rfm['Monetary'].min():,.0f}, Max=£{rfm['Monetary'].max():,.0f}, Mean=£{rfm['Monetary'].mean():,.0f}")
    print(f"{'='*80}\n")
    
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=debug
    )
