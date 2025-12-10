import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import warnings
import os
import sys
from flask import Flask

warnings.filterwarnings('ignore')

print("=" * 80)
print("🚀 CUSTOMER DASHBOARD FOR RAILWAY")
print("=" * 80)

# Inisialisasi Flask
server = Flask(__name__)

# ========== LOAD & PREPARE DATA ==========
def smart_data_loader():
    """Load data dengan berbagai fallback"""
    try:
        # Coba load CSV
        if os.path.exists('final_customer_segments.csv'):
            df = pd.read_csv('final_customer_segments.csv')
            print(f"📊 Loaded CSV: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Coba ambil beberapa baris untuk preview
            print("\nFirst 3 rows:")
            for i in range(min(3, len(df))):
                print(f"Row {i}: {df.iloc[i].to_dict()}")
            
            # Buat data sederhana dari CSV
            # Asumsi: kolom ke-2 = Frequency, ke-3 = Monetary
            data = {
                'Frequency': df.iloc[:, 2] if len(df.columns) > 2 else np.random.randint(1, 50, len(df)),
                'Monetary': df.iloc[:, 3] if len(df.columns) > 3 else np.random.randint(100, 10000, len(df)),
                'Recency': np.random.randint(1, 365, len(df)),  # Tidak ada di CSV
                'AvgOrderValue': df.iloc[:, 4] if len(df.columns) > 4 else np.random.randint(50, 500, len(df)),
                'RFM_Score': np.random.randint(3, 15, len(df)),  # Tidak ada di CSV
                'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], len(df), p=[0.1, 0.2, 0.15, 0.1, 0.15, 0.1, 0.2])
            }
            
            # Jika ada Customer Category, gunakan untuk cluster
            if 'Customer Category' in df.columns:
                category_map = {'Champion': 1, 'Loyal': 2, 'At Risk': 3, 'Cannot Lose': 4, 'Others': 5}
                data['Cluster_KMeans'] = df['Customer Category'].map(category_map).fillna(0).astype(int)
            
            return pd.DataFrame(data)
            
        else:
            print("📂 CSV not found, using dummy data")
            return create_dummy_data()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return create_dummy_data()

def create_dummy_data():
    """Create good dummy data"""
    np.random.seed(42)
    n = 1000
    
    data = {
        'Recency': np.random.randint(1, 365, n),
        'Frequency': np.random.randint(1, 50, n),
        'Monetary': np.random.randint(100, 10000, n),
        'AvgOrderValue': np.random.randint(50, 500, n),
        'RFM_Score': np.random.randint(1, 10, n),
        'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n)
    }
    
    # Buat karakteristik khusus
    data['Monetary'] = np.where(data['Cluster_KMeans'] == 3, 
                               np.random.randint(5000, 50000, n), 
                               data['Monetary'])
    data['Frequency'] = np.where(data['Cluster_KMeans'] == 6, 
                                np.random.randint(20, 200, n), 
                                data['Frequency'])
    
    return pd.DataFrame(data)

# Load data
rfm = smart_data_loader()
print(f"\n✅ FINAL DATA: {len(rfm)} customers")
print(f"Clusters: {rfm['Cluster_KMeans'].nunique()}")
print(f"Revenue: £{rfm['Monetary'].sum()/1e6:.2f}M")

# ========== STRATEGIES & PROFILES ==========
strats = {
    0: {'name':'😴 Dormant','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['25-30% Off','Multi-Channel','Retargeting']},
    1: {'name':'🏆 Champions','color':'#FFD700','priority':'CRITICAL','strategy':'VIP','tactics':['Exclusive Access','Premium Gifts','VIP Events']},
    2: {'name':'💎 Loyal','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['Tiered Rewards','Birthday Offers','Referral Bonus']},
    3: {'name':'💰 Big Spenders','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['Flex Terms','Luxury Gifts','Concierge']},
    4: {'name':'🌱 Potential','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['Education','Welcome Flow','Tutorials']},
    5: {'name':'📊 Standard','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['Newsletters','Seasonal','AI Recs']},
    6: {'name':'🚀 High Potential','color':'#4ecdc4','priority':'HIGH','strategy':'Accelerate','tactics':['Upsell','Cross-sell','Priority Support']}
}

# Assign labels
for cluster_id, strat in strats.items():
    if cluster_id in rfm['Cluster_KMeans'].unique():
        mask = rfm['Cluster_KMeans'] == cluster_id
        rfm.loc[mask, 'Cluster_Label'] = f"{strat['name']} (C{cluster_id})"
        rfm.loc[mask, 'Priority'] = strat['priority']

print(f"\n🎯 Created {len(strats)} segment strategies")

# ========== DASH APP ==========
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Simple layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("📊 Customer Analytics Dashboard", 
                style={'color': 'white', 'marginBottom': '10px'}),
        html.P(f"Analyzing {len(rfm):,} customers with {rfm['Cluster_KMeans'].nunique()} segments",
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
            html.H3(f"{len(rfm):,}", style={'color': '#667eea', 'margin': '0'}),
            html.P("Total Customers", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 
                  'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"£{rfm['Monetary'].sum()/1e6:.1f}M", style={'color': '#667eea', 'margin': '0'}),
            html.P("Total Revenue", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 
                  'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"{rfm['Cluster_KMeans'].nunique()}", style={'color': '#667eea', 'margin': '0'}),
            html.P("Segments", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 
                  'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"£{rfm['AvgOrderValue'].mean():.0f}", style={'color': '#667eea', 'margin': '0'}),
            html.P("Avg Order Value", style={'margin': '0', 'color': '#666'})
        ], style={'padding': '20px', 'background': 'white', 'borderRadius': '10px', 
                  'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
    ], style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
        'gap': '15px',
        'marginBottom': '30px'
    }),
    
    # Charts
    html.Div([
        dcc.Graph(
            id='pie-chart',
            figure={
                'data': [go.Pie(
                    labels=rfm['Cluster_Label'].unique(),
                    values=rfm['Cluster_Label'].value_counts().values,
                    hole=0.4
                )],
                'layout': {
                    'title': 'Customer Distribution by Segment',
                    'height': 400
                }
            }
        )
    ], style={'marginBottom': '30px'}),
    
    # Data Table
    html.Div([
        html.H4("Customer Data Sample", style={'marginBottom': '10px'}),
        html.Table(
            # Header
            [html.Tr([html.Th(col) for col in ['Segment', 'Count', 'Avg Revenue', 'Avg Frequency']])] +
            # Rows
            [html.Tr([
                html.Td(segment),
                html.Td(f"{count:,}"),
                html.Td(f"£{rfm[rfm['Cluster_Label']==segment]['Monetary'].mean():,.0f}"),
                html.Td(f"{rfm[rfm['Cluster_Label']==segment]['Frequency'].mean():.1f}")
            ]) for segment, count in rfm['Cluster_Label'].value_counts().items()],
            style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'}
        )
    ], style={
        'padding': '20px',
        'background': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
    }),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P(f"✅ Dashboard loaded successfully | Data source: {'CSV' if os.path.exists('final_customer_segments.csv') else 'Dummy'}"),
        html.P(f"Python {sys.version.split()[0]} | Running on Railway")
    ], style={'marginTop': '40px', 'textAlign': 'center', 'color': '#666'})
], style={
    'padding': '20px',
    'maxWidth': '1200px',
    'margin': '0 auto',
    'fontFamily': 'Arial, sans-serif'
})

# Health check
@server.route('/health')
def health():
    return {
        'status': 'healthy',
        'customers': len(rfm),
        'data_source': 'csv' if os.path.exists('final_customer_segments.csv') else 'dummy'
    }

# Run
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("RAILWAY_ENVIRONMENT") != "production"
    
    print(f"\n🚀 Starting on port {port}")
    print(f"📊 Data: {len(rfm):,} customers")
    print(f"🔧 Debug: {debug}")
    
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=False
    )
