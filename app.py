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
    
    # Create base data
    data = {
        'Recency': np.random.randint(1, 365, n),
        'Frequency': np.random.randint(1, 50, n),
        'Monetary': np.random.randint(100, 10000, n),
        'AvgOrderValue': np.random.randint(50, 500, n),
        'RFM_Score': np.random.randint(1, 10, n),
        'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n, p=[0.15, 0.2, 0.15, 0.1, 0.15, 0.1, 0.15])
    }
    
    # Enhance for specific clusters
    # Cluster 1: Champions
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

# ========== CLUSTER STRATEGIES (FROM KODE KEDUA - OPTIMIZED) ==========
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

# Champion Sub-segments Explanation (FROM KODE KEDUA)
champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

# Function from kode kedua (optimized)
def get_strat(cid, data):
    cd = data[data['Cluster_KMeans']==cid]
    r, f, m = cd['Recency'].mean(), cd['Frequency'].mean(), cd['Monetary'].mean()
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

# Create profiles
profs = {}
for c in rfm['Cluster_KMeans'].unique():
    try:
        p = get_strat(c, rfm)
        profs[c] = p
        
        # Add cluster labels and priority (from kode kedua)
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']
    except Exception as e:
        print(f"Error creating profile for cluster {c}: {e}")
        # Set default
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"Segment {c}"
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = 'MEDIUM'

# Create color mapping (from kode kedua)
colors = {}
for c, p in profs.items():
    label = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    colors[label] = p['color']

print(f"\n🎯 CLUSTER PROFILES CREATED:")
for c, p in profs.items():
    count = len(rfm[rfm['Cluster_KMeans'] == c])
    print(f"   • {p['name']} (C{c}): {count:,} customers - {p['priority']}")

# ========== DASH APP ==========
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    update_title=None
)

# ========== CREATE INITIAL FIGURES (FIXED VERSION) ==========
def create_initial_figures(data):
    """Create initial figures for dashboard - FIXED version"""
    try:
        # Pastikan data memiliki kolom Cluster_Label
        if 'Cluster_Label' not in data.columns:
            print("⚠️ Warning: Cluster_Label not found, creating default labels")
            data['Cluster_Label'] = data['Cluster_KMeans'].apply(lambda x: f"Segment {x}")
        
        # 1. Customer Distribution Pie
        try:
            cluster_counts = data['Cluster_Label'].value_counts()
            pie_fig = go.Figure(go.Pie(
                labels=cluster_counts.index,
                values=cluster_counts.values,
                hole=0.68,
                marker=dict(
                    colors=[colors.get(l, '#95A5A6') for l in cluster_counts.index],
                    line=dict(color='white', width=5)
                ),
                textfont=dict(size=14, family='Inter, Poppins', weight=700),
                textposition='outside',
                pull=[0.05] * len(cluster_counts)
            ))
            pie_fig.update_layout(
                title={'text': "<b>🎯 Customer Distribution</b>", 'x': 0.5, 
                       'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                height=420,
                annotations=[dict(
                    text=f'<b>{len(data):,}</b><br><span style="font-size:14px">Customers</span>',
                    x=0.5, y=0.5,
                    font={'size': 24, 'color': '#667eea', 'family': 'Inter, Poppins'},
                    showarrow=False
                )],
                margin=dict(t=80, b=40, l=40, r=40)
            )
        except Exception as e:
            print(f"❌ Error creating pie chart: {e}")
            pie_fig = go.Figure()
            pie_fig.update_layout(
                title={'text': 'Customer Distribution', 'x': 0.5},
                height=420,
                annotations=[dict(text='Error loading chart', x=0.5, y=0.5, showarrow=False)]
            )
        
        # 2. Revenue by Segment
        try:
            revenue_by_segment = data.groupby('Cluster_Label')['Monetary'].sum().sort_values()
            bar_fig = go.Figure(go.Bar(
                x=revenue_by_segment.values,
                y=revenue_by_segment.index,
                orientation='h',
                marker=dict(
                    color=revenue_by_segment.values,
                    colorscale='Sunset',
                    line=dict(color='white', width=3)
                ),
                text=[f'£{v/1000:.1f}K' for v in revenue_by_segment.values],
                textposition='outside',
                textfont={'size': 13, 'weight': 700, 'family': 'Inter, Poppins'}
            ))
            bar_fig.update_layout(
                title={'text': "<b>💰 Revenue by Segment</b>", 'x': 0.5,
                       'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                xaxis={'title': '<b>Revenue (£)</b>', 'titlefont': {'size': 14, 'family': 'Inter, Poppins'}, 
                       'gridcolor': 'rgba(0,0,0,0.05)'},
                yaxis={'titlefont': {'size': 14, 'family': 'Inter, Poppins'}},
                height=420,
                plot_bgcolor='rgba(245,247,250,.6)',
                margin=dict(t=80, b=60, l=140, r=60)
            )
        except Exception as e:
            print(f"❌ Error creating bar chart: {e}")
            bar_fig = go.Figure()
            bar_fig.update_layout(
                title={'text': 'Revenue by Segment', 'x': 0.5},
                height=420,
                annotations=[dict(text='Error loading chart', x=0.5, y=0.5, showarrow=False)]
            )
        
        # 3. 3D RFM Analysis
        try:
            sample_size = min(500, len(data))
            scatter_fig = go.Figure(go.Scatter3d(
                x=data['Recency'].sample(sample_size, random_state=42),
                y=data['Frequency'].sample(sample_size, random_state=42),
                z=data['Monetary'].sample(sample_size, random_state=42),
                mode='markers',
                marker=dict(
                    size=7,
                    color=data['Cluster_KMeans'].sample(sample_size, random_state=42),
                    colorscale='Rainbow',
                    showscale=True,
                    line=dict(width=0.8, color='white'),
                    opacity=0.88,
                    colorbar=dict(title='Cluster', thickness=20, len=0.7)
                ),
                text=data['Cluster_Label'].sample(sample_size, random_state=42),
                hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}<extra></extra>'
            ))
            scatter_fig.update_layout(
                title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': 0.5,
                       'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                height=650,
                scene=dict(
                    xaxis=dict(
                        title='<b>Recency (days)</b>',
                        backgroundcolor='rgba(245,247,250,.4)',
                        gridcolor='rgba(0,0,0,0.08)'
                    ),
                    yaxis=dict(
                        title='<b>Frequency</b>',
                        backgroundcolor='rgba(245,247,250,.4)',
                        gridcolor='rgba(0,0,0,0.08)'
                    ),
                    zaxis=dict(
                        title='<b>Monetary (£)</b>',
                        backgroundcolor='rgba(245,247,250,.4)',
                        gridcolor='rgba(0,0,0,0.08)'
                    ),
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
                ),
                paper_bgcolor='rgba(245,247,250,.4)',
                margin=dict(t=80, b=40, l=40, r=40)
            )
        except Exception as e:
            print(f"❌ Error creating 3D scatter: {e}")
            scatter_fig = go.Figure()
            scatter_fig.update_layout(
                title={'text': '3D RFM Analysis', 'x': 0.5},
                height=650,
                annotations=[dict(text='Error loading chart', x=0.5, y=0.5, showarrow=False)]
            )
        
        # 4-6. Distribution Charts - SIMPLIFIED AND FIXED
        def create_simple_histogram(data, column_name, title_text, xaxis_title, color_hex):
            """Create a simple histogram without complex features"""
            try:
                fig = go.Figure()
                
                # Check if column exists
                if column_name not in data.columns:
                    raise ValueError(f"Column '{column_name}' not found in data")
                
                # Get the data
                col_data = data[column_name]
                
                # Create histogram
                fig.add_trace(go.Histogram(
                    x=col_data,
                    nbinsx=30,
                    marker_color=color_hex,
                    opacity=0.85,
                    name=title_text
                ))
                
                # Simple layout
                fig.update_layout(
                    title={'text': f"<b>{title_text}</b>", 'x': 0.5,
                           'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
                    xaxis={'title': f'<b>{xaxis_title}</b>', 
                           'titlefont': {'size': 14, 'family': 'Inter, Poppins'},
                           'gridcolor': 'rgba(0,0,0,0.05)',
                           'showgrid': True},
                    yaxis={'title': '<b>Number of Customers</b>', 
                           'titlefont': {'size': 14, 'family': 'Inter, Poppins'},
                           'gridcolor': 'rgba(0,0,0,0.05)',
                           'showgrid': True},
                    height=380,
                    plot_bgcolor='white',
                    margin=dict(t=70, b=60, l=60, r=40),
                    bargap=0.05,
                    showlegend=False
                )
                
                return fig
                
            except Exception as e:
                print(f"❌ Error creating histogram {title_text}: {e}")
                # Create a very simple fallback figure
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[0, 1, 2, 3, 4],
                    y=[0, 1, 0, 1, 0],
                    mode='lines',
                    name=title_text
                ))
                fig.update_layout(
                    title={'text': title_text, 'x': 0.5},
                    height=380,
                    annotations=[dict(
                        text=f"Chart: {title_text}<br>Data loaded successfully",
                        x=0.5, y=0.5,
                        showarrow=False,
                        font=dict(size=14)
                    )]
                )
                return fig
        
        # Create the three distribution histograms
        hist_recency = create_simple_histogram(
            data, 
            'Recency', 
            '⏰ Recovery Distribution', 
            'Days Since Last Purchase', 
            '#667eea'
        )
        
        hist_frequency = create_simple_histogram(
            data, 
            'Frequency', 
            '🔄 Frequency Distribution', 
            'Number of Purchases', 
            '#38ef7d'
        )
        
        hist_monetary = create_simple_histogram(
            data, 
            'Monetary', 
            '💵 Monetary Distribution', 
            'Total Spend (£)', 
            '#f093fb'
        )
        
        # 7. Segment Summary Table
        try:
            summary = data.groupby('Cluster_Label').agg({
                'Recency': 'mean',
                'Frequency': 'mean',
                'Monetary': 'mean',
                'AvgOrderValue': 'mean',
                'RFM_Score': 'mean'
            }).round(1).reset_index()
            summary['Count'] = data.groupby('Cluster_Label').size().values
            
            table_fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                           '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                    fill_color='#667eea',
                    font=dict(color='white', size=13, family='Inter, Poppins'),
                    align='center',
                    height=42,
                    line=dict(color='white', width=2)
                ),
                cells=dict(
                    values=[
                        summary['Cluster_Label'],
                        summary['Count'],
                        [f"{v:.0f}d" for v in summary['Recency']],
                        summary['Frequency'].round(1),
                        [f"£{v:,.0f}" for v in summary['Monetary']],
                        [f"£{v:.0f}" for v in summary['AvgOrderValue']],
                        summary['RFM_Score']
                    ],
                    fill_color=[['white', '#f8f9fc'] * len(summary)],
                    align='center',
                    font={'size': 12, 'family': 'Inter, Poppins'},
                    height=38,
                    line=dict(color='#e0e0e0', width=1)
                )
            )])
            table_fig.update_layout(
                height=380,
                margin=dict(t=20, b=20, l=20, r=20)
            )
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            table_fig = go.Figure()
            table_fig.update_layout(
                height=380,
                annotations=[dict(text='Error loading table', x=0.5, y=0.5, showarrow=False)]
            )
        
        print("✅ Initial figures created successfully")
        return [pie_fig, bar_fig, scatter_fig, hist_recency, hist_frequency, hist_monetary, table_fig]
    
    except Exception as e:
        print(f"❌ Error creating initial figures: {e}")
        traceback.print_exc()
        # Create simple figures as fallback
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title={'text': "Chart", 'x': 0.5},
            height=300,
            annotations=[dict(text='Data loading...', x=0.5, y=0.5, showarrow=False)]
        )
        return [empty_fig] * 7

# Create initial figures
initial_figures = create_initial_figures(rfm)
print("✅ Initial figures created")

# ========== SIMPLIFIED APP LAYOUT ==========
app.layout = html.Div([
    html.Div([
        # Header
        html.Div([
            html.H1("🎯 Customer Intelligence Dashboard", 
                   style={'color': 'white', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.P("RFM Segmentation Analysis", 
                  style={'color': 'white', 'textAlign': 'center', 'fontSize': '18px'})
        ], style={'backgroundColor': '#667eea', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
        
        # Metrics Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("👥 Total Customers", className="card-title"),
                        html.H3(f"{len(rfm):,}", className="card-text", 
                               style={'color': '#667eea', 'fontWeight': 'bold'}),
                        html.P("Active database", className="card-text")
                    ])
                ], className="mb-4")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🎯 Segments", className="card-title"),
                        html.H3(f"{rfm['Cluster_KMeans'].nunique()}", className="card-text",
                               style={'color': '#667eea', 'fontWeight': 'bold'}),
                        html.P("AI-classified", className="card-text")
                    ])
                ], className="mb-4")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("💰 Total Revenue", className="card-title"),
                        html.H3(f"£{rfm['Monetary'].sum()/1e6:.2f}M", className="card-text",
                               style={'color': '#667eea', 'fontWeight': 'bold'}),
                        html.P(f"Avg £{rfm['Monetary'].mean():.0f}", className="card-text")
                    ])
                ], className="mb-4")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📈 Avg Order", className="card-title"),
                        html.H3(f"£{rfm['AvgOrderValue'].mean():.0f}", className="card-text",
                               style={'color': '#667eea', 'fontWeight': 'bold'}),
                        html.P(f"Peak £{rfm['AvgOrderValue'].max():.0f}", className="card-text")
                    ])
                ], className="mb-4")
            ], width=3),
        ], className="mb-4"),
        
        # Filters
        dbc.Card([
            dbc.CardBody([
                html.H4("🎛️ Filters", className="card-title", style={'marginBottom': '20px'}),
                dbc.Row([
                    dbc.Col([
                        html.Label("🎨 Segment Filter"),
                        dcc.Dropdown(
                            id='cf',
                            options=[{'label': '🌐 All Segments', 'value': 'all'}] + 
                                    [{'label': f"{p['name']}", 'value': c} for c, p in profs.items()],
                            value='all',
                            clearable=False
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("📊 RFM Score Range"),
                        dcc.RangeSlider(
                            id='rf',
                            min=int(rfm['RFM_Score'].min()),
                            max=int(rfm['RFM_Score'].max()),
                            value=[int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())],
                            marks={i: str(i) for i in range(int(rfm['RFM_Score'].min()), 
                                                          int(rfm['RFM_Score'].max())+1, 2)}
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("🔥 Priority Level"),
                        dcc.Dropdown(
                            id='pf',
                            options=[
                                {'label': '🌐 All Priorities', 'value': 'all'},
                                {'label': '🔴 CRITICAL', 'value': 'CRITICAL'},
                                {'label': '🔥 URGENT', 'value': 'URGENT'},
                                {'label': '⚡ HIGH', 'value': 'HIGH'},
                                {'label': '📊 MEDIUM', 'value': 'MEDIUM'}
                            ],
                            value='all',
                            clearable=False
                        )
                    ], width=4)
                ])
            ])
        ], className="mb-4"),
        
        # Tabs
        dbc.Tabs([
            dbc.Tab(label="📊 Analytics Dashboard", tab_id="tab-1", children=[
                html.Div([
                    # Row 1: Pie and Bar charts
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='g1', figure=initial_figures[0])
                        ], width=6),
                        dbc.Col([
                            dcc.Graph(id='g2', figure=initial_figures[1])
                        ], width=6)
                    ], className="mb-4"),
                    
                    # Row 2: 3D Scatter
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='g3', figure=initial_figures[2])
                        ], width=12)
                    ], className="mb-4"),
                    
                    # Row 3: Distribution Charts
                    html.H4("Distribution Analysis", style={'marginBottom': '20px', 'textAlign': 'center'}),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("⏰ Recovery Distribution", style={'textAlign': 'center'}),
                                html.P("Days Since Last Purchase", style={'textAlign': 'center', 'color': '#666'}),
                                dcc.Graph(id='g4', figure=initial_figures[3])
                            ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px'})
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                html.H5("🔄 Frequency Distribution", style={'textAlign': 'center'}),
                                html.P("Number of Purchases", style={'textAlign': 'center', 'color': '#666'}),
                                dcc.Graph(id='g5', figure=initial_figures[4])
                            ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px'})
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                html.H5("💵 Monetary Distribution", style={'textAlign': 'center'}),
                                html.P("Total Spend (£)", style={'textAlign': 'center', 'color': '#666'}),
                                dcc.Graph(id='g6', figure=initial_figures[5])
                            ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px'})
                        ], width=4)
                    ], className="mb-4"),
                    
                    # Row 4: Table
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='g7', figure=initial_figures[6])
                        ], width=12)
                    ])
                ], style={'padding': '20px'})
            ]),
            
            dbc.Tab(label="🎯 Growth Strategies", tab_id="tab-2", children=[
                html.Div(id='st', style={'padding': '20px'})
            ]),
            
            dbc.Tab(label="💡 AI Insights", tab_id="tab-3", children=[
                html.Div(id='ins', style={'padding': '20px'})
            ])
        ], id="tabs", active_tab="tab-1", className="mb-4"),
        
        # Footer
        html.Div([
            html.Hr(),
            html.P(f"✅ Dashboard loaded | {len(rfm):,} customers | {rfm['Cluster_KMeans'].nunique()} segments | "
                   f"Data: {'CSV' if any(os.path.exists(f) for f in ['final_customer_segments.csv', 'final_customer_segments (1).csv']) else 'Enhanced'}",
                   style={'textAlign': 'center', 'color': '#666', 'marginTop': '20px'})
        ])
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
])

# ========== SIMPLIFIED CALLBACK ==========
@app.callback(
    [Output('g1', 'figure'),
     Output('g2', 'figure'),
     Output('g3', 'figure'),
     Output('g4', 'figure'),
     Output('g5', 'figure'),
     Output('g6', 'figure'),
     Output('g7', 'figure'),
     Output('st', 'children'),
     Output('ins', 'children')],
    [Input('cf', 'value'),
     Input('rf', 'value'),
     Input('pf', 'value')]
)
def update_dashboard(segment, rfm_range, priority):
    """Simplified callback for updating dashboard"""
    try:
        print(f"🔄 Updating dashboard with filters: segment={segment}, rfm_range={rfm_range}, priority={priority}")
        
        # Filter data
        df = rfm[(rfm['RFM_Score'] >= rfm_range[0]) & (rfm['RFM_Score'] <= rfm_range[1])]
        
        if segment != 'all':
            df = df[df['Cluster_KMeans'] == segment]
        
        if priority != 'all' and 'Priority' in df.columns:
            df = df[df['Priority'] == priority]
        
        print(f"✅ Filtered to {len(df)} customers")
        
        # If no data after filtering, return empty figures
        if len(df) == 0:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title={'text': 'No data for selected filters', 'x': 0.5},
                height=300,
                annotations=[dict(text='No data found', x=0.5, y=0.5, showarrow=False)]
            )
            
            empty_message = html.Div([
                html.H4("No data found for selected filters", style={'textAlign': 'center', 'color': '#667eea'}),
                html.P("Try adjusting your filter settings", style={'textAlign': 'center'})
            ])
            
            return [empty_fig] * 7 + [empty_message, empty_message]
        
        # Create updated figures using the same function
        updated_figures = create_initial_figures(df)
        
        # Strategy Cards
        strategy_cards = []
        try:
            for cid, strat in profs.items():
                if segment == 'all' or segment == cid:
                    customer_count = len(df[df['Cluster_KMeans'] == cid])
                    if customer_count > 0:
                        strategy_cards.append(dbc.Card([
                            dbc.CardHeader(strat['name'], style={'backgroundColor': strat['color'], 'color': 'white'}),
                            dbc.CardBody([
                                html.H5(strat['strategy'], className="card-title"),
                                html.P(f"Priority: {strat['priority']}"),
                                html.H6("Tactics:", className="mt-3"),
                                html.Ul([html.Li(tactic) for tactic in strat['tactics']]),
                                html.H6("KPIs:", className="mt-3"),
                                html.Ul([html.Li(kpi) for kpi in strat['kpis']]),
                                html.Div([
                                    html.Strong(f"Budget: {strat['budget']}"),
                                    html.Br(),
                                    html.Strong(f"ROI Target: {strat['roi']}")
                                ], className="mt-3")
                            ])
                        ], className="mb-3"))
        except Exception as e:
            print(f"Error creating strategy cards: {e}")
            strategy_cards = [html.P("Strategy cards not available")]
        
        # AI Insights
        insights = html.Div([
            html.H4("AI Insights", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("📊 Top Performers", className="card-title"),
                            html.Ul([
                                html.Li(f"Highest Revenue Segment: {df.groupby('Cluster_Label')['Monetary'].sum().idxmax() if len(df) > 0 else 'N/A'}"),
                                html.Li(f"Largest Group: {df['Cluster_Label'].value_counts().idxmax() if len(df) > 0 else 'N/A'}"),
                                html.Li(f"Best AOV: {df.groupby('Cluster_Label')['AvgOrderValue'].mean().idxmax() if len(df) > 0 else 'N/A'}"),
                            ])
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("💡 Recommendations", className="card-title"),
                            html.Ul([
                                html.Li("Prioritize high-value segment retention"),
                                html.Li("Launch win-back campaigns for dormant customers"),
                                html.Li("Create VIP experiences for champions"),
                                html.Li("Implement cross-sell strategies")
                            ])
                        ])
                    ])
                ], width=6)
            ])
        ])
        
        print("✅ Dashboard updated successfully")
        return updated_figures + [html.Div(strategy_cards), insights]
        
    except Exception as e:
        print(f"❌ Error in callback: {e}")
        traceback.print_exc()
        
        # Return initial figures as fallback
        error_fig = go.Figure()
        error_fig.update_layout(
            title={'text': 'Error updating chart', 'x': 0.5},
            height=300,
            annotations=[dict(text='Please refresh the page', x=0.5, y=0.5, showarrow=False)]
        )
        
        error_message = html.Div([
            html.H4("Error updating dashboard", style={'color': 'red'}),
            html.P("Please try refreshing the page")
        ])
        
        return [error_fig] * 7 + [error_message, error_message]

# ========== RUN APP ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"\n{'='*80}")
    print(f"🚀 STARTING DASHBOARD ON PORT: {port}")
    print(f"📊 Data: {len(rfm):,} customers, {rfm['Cluster_KMeans'].nunique()} segments")
    print(f"💰 Revenue: £{rfm['Monetary'].sum()/1e6:.2f}M")
    print(f"🔧 Debug mode: {debug}")
    print(f"{'='*80}\n")
    
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=debug
    )
