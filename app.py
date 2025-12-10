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
print("🚀 CUSTOMER INTELLIGENCE DASHBOARD - FIXED CASE SENSITIVITY")
print("=" * 80)
print(f"Python: {sys.version}")
print(f"Current dir: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# ========== FLASK SERVER ==========
server = Flask(__name__)

# ========== LOAD DATA (FIXED CASE SENSITIVITY) ==========
def load_data():
    """Load data with robust error handling - FIXED for case sensitivity"""
    try:
        # Cek file CSV yang mungkin ada
        csv_files = ['final_customer_segments (1).csv', 'final_customer_segments.csv']
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                print(f"📂 Found data file: {csv_file}")
                print(f"   Size: {os.path.getsize(csv_file):,} bytes")
                
                try:
                    # Coba baca CSV
                    df = pd.read_csv(csv_file)
                    print(f"✅ Data loaded successfully: {df.shape}")
                    print(f"   Original columns: {df.columns.tolist()}")
                    
                    # LOWER CASE SEMUA NAMA KOLOM untuk konsistensi
                    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
                    print(f"   Standardized columns: {df.columns.tolist()}")
                    
                    # HAPUS DUPLIKAT KOLOM (jika ada)
                    df = df.loc[:, ~df.columns.duplicated()]
                    
                    # CEK KOLOM YANG DIPERLUKAN - CASE INSENSITIVE
                    # Buat mapping untuk nama kolom yang berbeda
                    column_mapping = {}
                    
                    # Cari kolom recency
                    recency_candidates = ['recency', 'days_since_last_purchase', 'r_value']
                    for candidate in recency_candidates:
                        if candidate in df.columns:
                            column_mapping['recency'] = candidate
                            break
                    
                    # Cari kolom frequency
                    freq_candidates = ['frequency', 'transaction_count', 'f_value', 'total_transactions']
                    for candidate in freq_candidates:
                        if candidate in df.columns:
                            column_mapping['frequency'] = candidate
                            break
                    
                    # Cari kolom monetary
                    monetary_candidates = ['monetary', 'total_revenue', 'm_value', 'revenue', 'total_spent']
                    for candidate in monetary_candidates:
                        if candidate in df.columns:
                            column_mapping['monetary'] = candidate
                            break
                    
                    # Cari kolom cluster
                    cluster_candidates = ['cluster_kmeans', 'cluster', 'segment', 'customer_segment', 'kmeans_cluster']
                    for candidate in cluster_candidates:
                        if candidate in df.columns:
                            column_mapping['cluster_kmeans'] = candidate
                            break
                    
                    # Cari kolom RFM score
                    rfm_candidates = ['rfm_score', 'rfm_value', 'total_score']
                    for candidate in rfm_candidates:
                        if candidate in df.columns:
                            column_mapping['rfm_score'] = candidate
                            break
                    
                    # Cari kolom average order value
                    aov_candidates = ['avgordervalue', 'average_order_value', 'aov', 'avg_transaction_value']
                    for candidate in aov_candidates:
                        if candidate in df.columns:
                            column_mapping['avgordervalue'] = candidate
                            break
                    
                    print(f"✅ Column mapping found: {column_mapping}")
                    
                    # STANDARDISASI NAMA KOLOM
                    for standard_name, original_name in column_mapping.items():
                        if original_name != standard_name and original_name in df.columns:
                            df[standard_name] = df[original_name]
                    
                    # PASTIKAN SEMUA KOLOM STANDAR ADA
                    standard_columns = ['recency', 'frequency', 'monetary', 'cluster_kmeans', 'rfm_score', 'avgordervalue']
                    
                    for col in standard_columns:
                        if col not in df.columns:
                            print(f"⚠️ Column '{col}' not found, creating with dummy data")
                            if col == 'recency':
                                df[col] = np.random.randint(1, 365, len(df))
                            elif col == 'frequency':
                                df[col] = np.random.randint(1, 100, len(df))
                            elif col == 'monetary':
                                df[col] = np.random.randint(100, 20000, len(df))
                            elif col == 'cluster_kmeans':
                                df[col] = np.random.choice([0, 1, 2, 3, 4, 5, 6], len(df))
                            elif col == 'rfm_score':
                                df[col] = np.random.randint(1, 10, len(df))
                            elif col == 'avgordervalue':
                                df[col] = df['monetary'] / df['frequency'].clip(lower=1)
                    
                    # Konversi tipe data
                    df['recency'] = pd.to_numeric(df['recency'], errors='coerce').fillna(df['recency'].median())
                    df['frequency'] = pd.to_numeric(df['frequency'], errors='coerce').fillna(df['frequency'].median())
                    df['monetary'] = pd.to_numeric(df['monetary'], errors='coerce').fillna(df['monetary'].median())
                    df['cluster_kmeans'] = pd.to_numeric(df['cluster_kmeans'], errors='coerce').fillna(0).astype(int)
                    df['rfm_score'] = pd.to_numeric(df['rfm_score'], errors='coerce').fillna(df['rfm_score'].median())
                    
                    # Bersihkan nilai negatif
                    df['recency'] = df['recency'].abs()
                    df['frequency'] = df['frequency'].abs()
                    df['monetary'] = df['monetary'].abs()
                    
                    # Pastikan avgordervalue ada
                    if 'avgordervalue' not in df.columns:
                        df['avgordervalue'] = df['monetary'] / df['frequency'].clip(lower=1)
                    
                    print(f"✅ Processed {len(df)} rows")
                    print(f"   Final columns: {df.columns.tolist()}")
                    print(f"   Recency range: {df['recency'].min():.0f} - {df['recency'].max():.0f}")
                    print(f"   Frequency range: {df['frequency'].min():.0f} - {df['frequency'].max():.0f}")
                    print(f"   Monetary range: £{df['monetary'].min():.0f} - £{df['monetary'].max():.0f}")
                    print(f"   Cluster values: {df['cluster_kmeans'].unique()}")
                    
                    return df
                        
                except Exception as e:
                    print(f"❌ Error reading {csv_file}: {e}")
                    traceback.print_exc()
                    continue
                    
        print("📂 No valid data file found, using enhanced dummy data")
        
    except Exception as e:
        print(f"❌ Unexpected error in load_data: {e}")
        traceback.print_exc()
    
    # Fallback: Enhanced dummy data
    return create_enhanced_data()

def create_enhanced_data():
    """Create realistic data matching your CSV structure"""
    np.random.seed(42)
    n = 3680
    
    print(f"📊 Creating enhanced data with {n} customers")
    
    # Create base data with lowercase column names
    data = {
        'recency': np.random.randint(1, 365, n),
        'frequency': np.random.randint(1, 50, n),
        'monetary': np.random.randint(100, 10000, n),
        'avgordervalue': np.random.randint(50, 500, n),
        'rfm_score': np.random.randint(1, 10, n),
        'cluster_kmeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n, p=[0.15, 0.2, 0.15, 0.1, 0.15, 0.1, 0.15])
    }
    
    # Enhance for specific clusters
    # Cluster 1: Champions
    mask = data['cluster_kmeans'] == 1
    data['recency'] = np.where(mask, np.random.randint(1, 30, n), data['recency'])
    data['frequency'] = np.where(mask, np.random.randint(15, 50, n), data['frequency'])
    data['monetary'] = np.where(mask, np.random.randint(5000, 30000, n), data['monetary'])
    
    # Cluster 3: Big Spenders
    mask = data['cluster_kmeans'] == 3
    data['monetary'] = np.where(mask, np.random.randint(10000, 50000, n), data['monetary'])
    data['avgordervalue'] = np.where(mask, np.random.randint(1000, 5000, n), data['avgordervalue'])
    
    # Cluster 6: High Frequency
    mask = data['cluster_kmeans'] == 6
    data['frequency'] = np.where(mask, np.random.randint(30, 100, n), data['frequency'])
    
    # Cluster 0: Dormant
    mask = data['cluster_kmeans'] == 0
    data['recency'] = np.where(mask, np.random.randint(200, 365, n), data['recency'])
    data['frequency'] = np.where(mask, np.random.randint(1, 5, n), data['frequency'])
    
    rfm = pd.DataFrame(data)
    print(f"✅ Enhanced data created: {rfm.shape}")
    return rfm

# Load data
rfm = load_data()

# PASTIKAN KOLOM YANG DIPERLUKAN ADA (LOWERCASE!)
required_columns = ['recency', 'frequency', 'monetary', 'cluster_kmeans', 'rfm_score', 'avgordervalue']
for col in required_columns:
    if col not in rfm.columns:
        print(f"❌ CRITICAL: Column '{col}' missing from data!")
        print(f"   Available columns: {rfm.columns.tolist()}")
        # Exit jika kolom penting tidak ada
        sys.exit(1)

print(f"\n📊 DATA SUMMARY:")
print(f"   Total customers: {len(rfm):,}")
print(f"   Unique clusters: {rfm['cluster_kmeans'].nunique()}")
print(f"   Total revenue: £{rfm['monetary'].sum():,.0f}")
print(f"   Average order value: £{rfm['avgordervalue'].mean():.0f}")
print(f"   Recency stats: mean={rfm['recency'].mean():.1f}, std={rfm['recency'].std():.1f}")
print(f"   Frequency stats: mean={rfm['frequency'].mean():.1f}, std={rfm['frequency'].std():.1f}")
print(f"   Monetary stats: mean={rfm['monetary'].mean():.1f}, std={rfm['monetary'].std():.1f}")

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
    """Get strategy for cluster"""
    cd = data[data['cluster_kmeans'] == cid]
    if len(cd) == 0:
        return {**strats['standard'], 'cluster_id': cid}
    
    r = cd['recency'].mean()
    f = cd['frequency'].mean()
    m = cd['monetary'].mean()
    
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
for c in sorted(rfm['cluster_kmeans'].unique()):
    p = get_strat(c, rfm)
    profs[c] = p
    
    # Add cluster labels and priority
    rfm.loc[rfm['cluster_kmeans'] == c, 'cluster_label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    rfm.loc[rfm['cluster_kmeans'] == c, 'priority'] = p['priority']

# Create color mapping
colors = {}
for c, p in profs.items():
    label = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    colors[label] = p['color']

print(f"\n🎯 CLUSTER PROFILES CREATED:")
for c, p in profs.items():
    count = len(rfm[rfm['cluster_kmeans'] == c])
    revenue = rfm[rfm['cluster_kmeans'] == c]['monetary'].sum()
    print(f"   • {p['name']} (C{c}): {count:,} customers - £{revenue:,.0f} revenue - {p['priority']}")

# ========== DASH APP ==========
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    update_title=None
)

# ========== APP LAYOUT ==========
app.layout = html.Div([
    html.Div([
        # Header
        html.Div([
            html.H1("🎯 Customer Intelligence Hub", className="title"),
            html.P("Customer Segmentation for Personalized Retail Marketing", className="sub")
        ], className="hdr"),
        
        # Metrics - GANTI DENGAN LOWERCASE COLUMN NAMES
        html.Div([
            html.Div([
                html.Div("👥", className="met-icon"),
                html.Div(f"{len(rfm):,}", className="met-val"),
                html.Div("CUSTOMERS", className="met-lbl"),
                html.Div("Active Database", className="met-sub")
            ], className="met"),
            
            html.Div([
                html.Div("🎯", className="met-icon"),
                html.Div(f"{rfm['cluster_kmeans'].nunique()}", className="met-val"),
                html.Div("SEGMENTS", className="met-lbl"),
                html.Div("AI-Classified", className="met-sub")
            ], className="met"),
            
            html.Div([
                html.Div("💰", className="met-icon"),
                html.Div(f"£{rfm['monetary'].sum()/1e6:.2f}M", className="met-val"),
                html.Div("REVENUE", className="met-lbl"),
                html.Div(f"Avg £{rfm['monetary'].mean():.0f}", className="met-sub")
            ], className="met"),
            
            html.Div([
                html.Div("📈", className="met-icon"),
                html.Div(f"£{rfm['avgordervalue'].mean():.0f}", className="met-val"),
                html.Div("AVG ORDER", className="met-lbl"),
                html.Div(f"Peak £{rfm['avgordervalue'].max():.0f}", className="met-sub")
            ], className="met")
        ], className="metrics"),
        
        # Filters
        html.Div([
            html.Div("🎛️ Smart Filters", className="filt-t"),
            html.Div([
                html.Div([
                    html.Label("🎨 Segment Filter"),
                    dcc.Dropdown(
                        id='cf',
                        options=[{'label': '🌐 All Segments', 'value': 'all'}] + 
                                [{'label': f"{p['name']} - {champion_details[c]['tier']}" if p['name']=='🏆 Champions' and c in champion_details else p['name'],
                                  'value': c} for c, p in profs.items()],
                        value='all',
                        clearable=False,
                        style={'borderRadius': '12px'}
                    )
                ]),
                
                html.Div([
                    html.Label("📊 RFM Score Range"),
                    dcc.RangeSlider(
                        id='rf',
                        min=int(rfm['rfm_score'].min()),
                        max=int(rfm['rfm_score'].max()),
                        value=[int(rfm['rfm_score'].min()), int(rfm['rfm_score'].max())],
                        marks={i: {'label': str(i), 'style': {'fontWeight': '600'}}
                               for i in range(int(rfm['rfm_score'].min()), int(rfm['rfm_score'].max())+1, 2)},
                        tooltip={'placement': 'bottom', 'always_visible': False}
                    )
                ]),
                
                html.Div([
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
                        clearable=False,
                        style={'borderRadius': '12px'}
                    )
                ])
            ], className="filt-g")
        ], className="filt"),
        
        # Tabs
        dbc.Tabs([
            dbc.Tab(label="📊 Analytics Dashboard", children=[
                html.Div([
                    # Row 1 - Pie Chart and Revenue Chart
                    html.Div([
                        html.Div([
                            dcc.Graph(id='g1', config={'displayModeBar': False})
                        ], className="chart"),
                        
                        html.Div([
                            dcc.Graph(id='g2', config={'displayModeBar': False})
                        ], className="chart")
                    ], className="charts"),
                    
                    # Row 2 - 3D Scatter
                    html.Div([
                        dcc.Graph(id='g3', config={'displayModeBar': False})
                    ], className="chart chart-full"),
                    
                    # Row 3 - Histograms
                    html.Div([
                        html.Div([
                            dcc.Graph(id='g4', config={'displayModeBar': False})
                        ], className="chart"),
                        
                        html.Div([
                            dcc.Graph(id='g5', config={'displayModeBar': False})
                        ], className="chart"),
                        
                        html.Div([
                            dcc.Graph(id='g6', config={'displayModeBar': False})
                        ], className="chart")
                    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '26px', 'marginBottom': '26px'}),
                    
                    # Row 4 - Summary Table
                    html.Div([
                        dcc.Graph(id='g7', config={'displayModeBar': False})
                    ], className="chart chart-full")
                ], className="tab-content")
            ]),
            
            dbc.Tab(label="🎯 Growth Strategies", children=[
                html.Div([
                    html.Div(id='champ-detail'),
                    html.Div(id='st')
                ], className="tab-content")
            ]),
            
            dbc.Tab(label="💡 AI Insights", children=[
                html.Div(id='ins', className="tab-content")
            ])
        ])
    ], className="dash"),
    
    # Hidden div to store initial data
    dcc.Store(id='store-data', data=rfm.to_dict('records')),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P(f"✅ Dashboard loaded | {len(rfm):,} customers | {rfm['cluster_kmeans'].nunique()} segments"),
        html.P(f"Data: {'CSV' if any(os.path.exists(f) for f in ['final_customer_segments.csv', 'final_customer_segments (1).csv']) else 'Enhanced'} | Railway")
    ], style={
        'textAlign': 'center',
        'marginTop': '50px',
        'padding': '20px',
        'color': '#666'
    })
])

# ========== CREATE INITIAL FIGURES ==========
def create_initial_figures(data):
    """Create initial figures for dashboard"""
    
    try:
        # 1. Customer Distribution Pie
        if 'cluster_label' not in data.columns:
            # Create cluster_label if not exists
            data['cluster_label'] = data.apply(lambda row: f"Cluster {row['cluster_kmeans']}", axis=1)
        
        cluster_counts = data['cluster_label'].value_counts()
        pie_fig = go.Figure(go.Pie(
            labels=cluster_counts.index,
            values=cluster_counts.values,
            hole=0.68,
            marker=dict(colors=[colors.get(l, '#95A5A6') for l in cluster_counts.index]),
            textinfo='label+percent',
            textposition='outside',
            pull=[0.05] * len(cluster_counts)
        ))
        pie_fig.update_layout(
            title={'text': "<b>🎯 Customer Distribution</b>", 'x': 0.5},
            height=420,
            showlegend=False,
            annotations=[dict(
                text=f'<b>{len(data):,}</b><br>Customers',
                x=0.5, y=0.5,
                font={'size': 20, 'color': '#667eea'},
                showarrow=False
            )],
            margin=dict(t=60, b=40, l=40, r=40)
        )
        
        # 2. Revenue by Segment
        revenue_by_segment = data.groupby('cluster_label')['monetary'].sum().sort_values()
        bar_fig = go.Figure(go.Bar(
            x=revenue_by_segment.values,
            y=revenue_by_segment.index,
            orientation='h',
            marker_color=[colors.get(l, '#95A5A6') for l in revenue_by_segment.index],
            text=[f'£{v:,.0f}' for v in revenue_by_segment.values],
            textposition='outside'
        ))
        bar_fig.update_layout(
            title={'text': "<b>💰 Revenue by Segment</b>", 'x': 0.5},
            xaxis={'title': 'Revenue (£)'},
            yaxis={'title': 'Segment'},
            height=420,
            plot_bgcolor='rgba(245,247,250,.6)'
        )
        
        # 3. 3D Scatter
        sample_size = min(300, len(data))
        sample_data = data.sample(sample_size, random_state=42)
        
        scatter_fig = go.Figure(go.Scatter3d(
            x=sample_data['recency'],
            y=sample_data['frequency'],
            z=sample_data['monetary'],
            mode='markers',
            marker=dict(
                size=5,
                color=sample_data['cluster_kmeans'],
                colorscale='Rainbow',
                showscale=True,
                opacity=0.8
            ),
            text=sample_data['cluster_label']
        ))
        scatter_fig.update_layout(
            title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': 0.5},
            height=500,
            scene=dict(
                xaxis_title='Recency (days)',
                yaxis_title='Frequency',
                zaxis_title='Monetary (£)'
            )
        )
        
        # 4. Recency Distribution
        hist_recency = go.Figure()
        hist_recency.add_trace(go.Histogram(
            x=data['recency'],
            nbinsx=30,
            marker_color='#ff6b6b',
            opacity=0.7
        ))
        hist_recency.update_layout(
            title={'text': "<b>⏰ Recency Distribution</b>", 'x': 0.5},
            xaxis_title='Days Since Last Purchase',
            yaxis_title='Number of Customers',
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)'
        )
        
        # 5. Frequency Distribution
        hist_frequency = go.Figure()
        hist_frequency.add_trace(go.Histogram(
            x=data['frequency'],
            nbinsx=30,
            marker_color='#4ecdc4',
            opacity=0.7
        ))
        hist_frequency.update_layout(
            title={'text': "<b>🔄 Frequency Distribution</b>", 'x': 0.5},
            xaxis_title='Number of Purchases',
            yaxis_title='Number of Customers',
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)'
        )
        
        # 6. Monetary Distribution
        hist_monetary = go.Figure()
        hist_monetary.add_trace(go.Histogram(
            x=data['monetary'],
            nbinsx=30,
            marker_color='#45b7d1',
            opacity=0.7
        ))
        hist_monetary.update_layout(
            title={'text': "<b>💵 Monetary Distribution</b>", 'x': 0.5},
            xaxis_title='Total Spend (£)',
            yaxis_title='Number of Customers',
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)'
        )
        
        # 7. Summary Table
        if 'cluster_label' in data.columns and 'avgordervalue' in data.columns:
            summary = data.groupby('cluster_label').agg({
                'recency': 'mean',
                'frequency': 'mean',
                'monetary': 'mean',
                'avgordervalue': 'mean',
                'rfm_score': 'mean'
            }).round(1).reset_index()
            summary['count'] = data.groupby('cluster_label').size().values
            
            table_fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                           '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                    fill_color='#667eea',
                    font=dict(color='white', size=13),
                    align='center',
                    height=40
                ),
                cells=dict(
                    values=[
                        summary['cluster_label'],
                        summary['count'],
                        [f"{v:.0f}d" for v in summary['recency']],
                        summary['frequency'].round(1),
                        [f"£{v:,.0f}" for v in summary['monetary']],
                        [f"£{v:.0f}" for v in summary['avgordervalue']],
                        summary['rfm_score'].round(1)
                    ],
                    fill_color=['white', '#f8f9fc'] * len(summary),
                    align='center',
                    font={'size': 12},
                    height=35
                )
            )])
            table_fig.update_layout(height=380)
        else:
            # Create empty table if columns missing
            table_fig = go.Figure()
            table_fig.update_layout(
                title={'text': 'Data not available', 'x': 0.5},
                height=380
            )
        
        return [pie_fig, bar_fig, scatter_fig, hist_recency, hist_frequency, hist_monetary, table_fig]
    
    except Exception as e:
        print(f"Error creating initial figures: {e}")
        traceback.print_exc()
        # Return simple empty figures as fallback
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Loading...")
        return [empty_fig] * 7

# Create initial figures
initial_figures = create_initial_figures(rfm)
print("✅ Initial figures created")

# ========== CALLBACK FUNCTIONS ==========
@app.callback(
    [Output('g1', 'figure'),
     Output('g2', 'figure'),
     Output('g3', 'figure'),
     Output('g4', 'figure'),
     Output('g5', 'figure'),
     Output('g6', 'figure'),
     Output('g7', 'figure'),
     Output('champ-detail', 'children'),
     Output('st', 'children'),
     Output('ins', 'children')],
    [Input('cf', 'value'),
     Input('rf', 'value'),
     Input('pf', 'value')]
)
def update_all_charts(segment, rfm_range, priority):
    """Main callback for updating all dashboard elements"""
    try:
        print(f"\n🔄 Updating dashboard with filters:")
        print(f"   Segment: {segment}, RFM Range: {rfm_range}, Priority: {priority}")
        
        # Filter data - GUNAKAN LOWERCASE COLUMN NAMES
        df = rfm[(rfm['rfm_score'] >= rfm_range[0]) & (rfm['rfm_score'] <= rfm_range[1])]
        
        if segment != 'all':
            df = df[df['cluster_kmeans'] == segment]
        
        if priority != 'all':
            if 'priority' in df.columns:
                df = df[df['priority'] == priority]
        
        print(f"✅ Filtered to {len(df)} customers")
        
        # If no data after filtering
        if len(df) == 0:
            print("⚠️ No data for selected filters")
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title={'text': 'No data for selected filters', 'x': 0.5},
                height=300,
                plot_bgcolor='white'
            )
            
            empty_message = html.Div([
                html.H3("No data found for selected filters", 
                       style={'textAlign': 'center', 'color': '#667eea', 'marginBottom': '20px'}),
                html.P("Try adjusting your filter settings to see more data",
                      style={'textAlign': 'center', 'color': '#7f8c8d'})
            ], style={'textAlign': 'center', 'padding': '50px', 'background': '#f8f9fa', 'borderRadius': '15px'})
            
            return [empty_fig] * 7 + [empty_message, empty_message, empty_message]
        
        # Create cluster_label if not exists
        if 'cluster_label' not in df.columns:
            for c in df['cluster_kmeans'].unique():
                if c in profs:
                    df.loc[df['cluster_kmeans'] == c, 'cluster_label'] = f"{profs[c]['name'][:2]} {profs[c]['name'][2:]} (C{c})"
                else:
                    df.loc[df['cluster_kmeans'] == c, 'cluster_label'] = f"Cluster {c}"
        
        # 1. Customer Distribution Pie
        cluster_counts = df['cluster_label'].value_counts()
        pie_fig = go.Figure(go.Pie(
            labels=cluster_counts.index,
            values=cluster_counts.values,
            hole=0.68,
            marker=dict(colors=[colors.get(l, '#95A5A6') for l in cluster_counts.index]),
            textinfo='label+percent',
            textposition='outside',
            pull=[0.05] * len(cluster_counts)
        ))
        pie_fig.update_layout(
            title={'text': "<b>🎯 Customer Distribution</b>", 'x': 0.5},
            height=420,
            showlegend=False,
            annotations=[dict(
                text=f'<b>{len(df):,}</b><br>Customers',
                x=0.5, y=0.5,
                font={'size': 20, 'color': '#667eea'},
                showarrow=False
            )],
            margin=dict(t=60, b=40, l=40, r=40)
        )
        
        # 2. Revenue by Segment
        revenue_by_segment = df.groupby('cluster_label')['monetary'].sum().sort_values()
        bar_fig = go.Figure(go.Bar(
            x=revenue_by_segment.values,
            y=revenue_by_segment.index,
            orientation='h',
            marker_color=[colors.get(l, '#95A5A6') for l in revenue_by_segment.index],
            text=[f'£{v:,.0f}' for v in revenue_by_segment.values],
            textposition='outside'
        ))
        bar_fig.update_layout(
            title={'text': "<b>💰 Revenue by Segment</b>", 'x': 0.5},
            xaxis={'title': 'Revenue (£)'},
            yaxis={'title': 'Segment'},
            height=420,
            plot_bgcolor='rgba(245,247,250,.6)'
        )
        
        # 3. 3D Scatter
        sample_size = min(300, len(df))
        sample_data = df.sample(sample_size, random_state=42)
        
        scatter_fig = go.Figure(go.Scatter3d(
            x=sample_data['recency'],
            y=sample_data['frequency'],
            z=sample_data['monetary'],
            mode='markers',
            marker=dict(
                size=5,
                color=sample_data['cluster_kmeans'],
                colorscale='Rainbow',
                showscale=True,
                opacity=0.8
            ),
            text=sample_data['cluster_label']
        ))
        scatter_fig.update_layout(
            title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': 0.5},
            height=500,
            scene=dict(
                xaxis_title='Recency (days)',
                yaxis_title='Frequency',
                zaxis_title='Monetary (£)'
            )
        )
        
        # 4. Recency Distribution
        hist_recency = go.Figure()
        hist_recency.add_trace(go.Histogram(
            x=df['recency'],
            nbinsx=30,
            marker_color='#ff6b6b',
            opacity=0.7
        ))
        hist_recency.update_layout(
            title={'text': "<b>⏰ Recency Distribution</b>", 'x': 0.5},
            xaxis_title='Days Since Last Purchase',
            yaxis_title='Number of Customers',
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)'
        )
        
        # 5. Frequency Distribution
        hist_frequency = go.Figure()
        hist_frequency.add_trace(go.Histogram(
            x=df['frequency'],
            nbinsx=30,
            marker_color='#4ecdc4',
            opacity=0.7
        ))
        hist_frequency.update_layout(
            title={'text': "<b>🔄 Frequency Distribution</b>", 'x': 0.5},
            xaxis_title='Number of Purchases',
            yaxis_title='Number of Customers',
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)'
        )
        
        # 6. Monetary Distribution
        hist_monetary = go.Figure()
        hist_monetary.add_trace(go.Histogram(
            x=df['monetary'],
            nbinsx=30,
            marker_color='#45b7d1',
            opacity=0.7
        ))
        hist_monetary.update_layout(
            title={'text': "<b>💵 Monetary Distribution</b>", 'x': 0.5},
            xaxis_title='Total Spend (£)',
            yaxis_title='Number of Customers',
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)'
        )
        
        # 7. Summary Table
        summary = df.groupby('cluster_label').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean',
            'avgordervalue': 'mean',
            'rfm_score': 'mean'
        }).round(1).reset_index()
        summary['count'] = df.groupby('cluster_label').size().values
        
        table_fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                       '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                fill_color='#667eea',
                font=dict(color='white', size=13),
                align='center',
                height=40
            ),
            cells=dict(
                values=[
                    summary['cluster_label'],
                    summary['count'],
                    [f"{v:.0f}d" for v in summary['recency']],
                    summary['frequency'].round(1),
                    [f"£{v:,.0f}" for v in summary['monetary']],
                    [f"£{v:.0f}" for v in summary['avgordervalue']],
                    summary['rfm_score'].round(1)
                ],
                fill_color=['white', '#f8f9fc'] * len(summary),
                align='center',
                font={'size': 12},
                height=35
            )
        )])
        table_fig.update_layout(height=380)
        
        # 8. Champion Breakdown
        champion_clusters = [c for c in df['cluster_kmeans'].unique() 
                           if c in profs and profs[c]['name'] == '🏆 Champions']
        
        champion_breakdown = None
        if champion_clusters:
            champ_cards = []
            for cid in sorted(champion_clusters):
                if cid in champion_details:
                    detail = champion_details[cid]
                    count = len(df[df['cluster_kmeans'] == cid])
                    champ_cards.append(html.Div([
                        html.Div(f"Champion C{cid}", className="champ-num"),
                        html.Div(f"🏅 {detail['tier']}", className="champ-tier"),
                        html.Div(detail['desc'], className="champ-desc"),
                        html.Div(f"📊 Characteristics: {detail['char']}", className="champ-char")
                    ], className="champ-card"))
            
            if champ_cards:
                champion_breakdown = html.Div([
                    html.Div("🏆 Champion Segments Breakdown", className="champ-break-t"),
                    html.Div("Understanding the 4 Different Champion Tiers",
                            style={'textAlign': 'center', 'fontSize': '1.1rem', 'marginBottom': '24px', 'opacity': '0.95'}),
                    html.Div(champ_cards, className="champ-grid")
                ], className="champ-break")
        
        # 9. Strategy Cards
        strategy_cards = []
        for cid, strat in profs.items():
            if segment == 'all' or segment == cid:
                customer_count = len(df[df['cluster_kmeans'] == cid])
                if customer_count > 0:
                    strategy_cards.append(html.Div([
                        html.Div([
                            html.Div(strat['name'], className="strat-name"),
                            html.Div(strat['priority'], className="pri-badge")
                        ], className="strat-hdr"),
                        
                        html.Div(f"📋 {strat['strategy']} Strategy", className="strat-sub"),
                        
                        html.Div([
                            html.Div("🎯 Key Tactics", className="tact-t"),
                            *[html.Div(t, className="tact") for t in strat['tactics']]
                        ], className="tactics"),
                        
                        html.Div([
                            html.Div("📊 Target KPIs", className="tact-t"),
                            html.Div([html.Div(k, className="kpi") for k in strat['kpis']], className="kpi-g")
                        ], className="tactics"),
                        
                        html.Div([
                            html.Div([
                                html.Div("Budget Allocation", className="budget-l"),
                                html.Div(strat['budget'], className="budget-v")
                            ]),
                            html.Div([
                                html.Div("ROI Target", className="budget-l"),
                                html.Div(strat['roi'], className="budget-v")
                            ]),
                            html.Div([
                                html.Div("Customers", className="budget-l"),
                                html.Div(f"{customer_count:,}", className="budget-v")
                            ])
                        ], className="budget")
                    ], className="strat", style={'background': strat['grad']}))
        
        # 10. AI Insights
        insights = html.Div([
            html.Div("🧠 AI-Powered Insights & Recommendations", className="ins-t"),
            html.Div([
                html.Div([
                    html.Div("📊 Top Performers", className="ins-h"),
                    html.Ul([
                        html.Li(f"🏆 Highest Revenue: {df.groupby('cluster_label')['monetary'].sum().idxmax()}"),
                        html.Li(f"👥 Largest Group: {df['cluster_label'].value_counts().idxmax()} ({df['cluster_label'].value_counts().max():,} customers)"),
                        html.Li(f"💰 Best AOV: {df.groupby('cluster_label')['avgordervalue'].mean().idxmax()} (£{df.groupby('cluster_label')['avgordervalue'].mean().max():.0f})"),
                        html.Li(f"🔄 Most Frequent: {df.groupby('cluster_label')['frequency'].mean().idxmax()} ({df.groupby('cluster_label')['frequency'].mean().max():.1f} orders)")
                    ], className="ins-list")
                ], className="ins-card"),
                
                html.Div([
                    html.Div("💡 Smart Recommendations", className="ins-h"),
                    html.Ul([
                        html.Li("🎯 Prioritize high-value segment retention programs"),
                        html.Li("📧 Launch win-back campaigns for dormant customers"),
                        html.Li("🚀 Accelerate potential customer nurturing flows"),
                        html.Li("💎 Create exclusive VIP experiences for champions"),
                        html.Li("📈 Implement cross-sell strategies for loyal segments")
                    ], className="ins-list")
                ], className="ins-card")
            ], className="ins-g")
        ], className="ins")
        
        print("✅ All charts updated successfully")
        return [pie_fig, bar_fig, scatter_fig, hist_recency, hist_frequency, 
                hist_monetary, table_fig, champion_breakdown, 
                html.Div(strategy_cards, className="strat-g"), insights]
    
    except Exception as e:
        print(f"❌ Error in main callback: {e}")
        traceback.print_exc()
        
        # Return initial figures as fallback
        error_message = html.Div([
            html.H3("⚠️ Error updating dashboard", 
                   style={'textAlign': 'center', 'color': '#ff6b6b', 'marginBottom': '20px'}),
            html.P("Please try again or refresh the page",
                  style={'textAlign': 'center', 'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '50px', 'background': '#f8f9fa', 'borderRadius': '15px'})
        
        return initial_figures + [error_message, error_message, error_message]

# ========== HEALTH CHECK ==========
@server.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'customers': len(rfm),
        'segments': rfm['cluster_kmeans'].nunique() if 'cluster_kmeans' in rfm.columns else 0,
        'revenue': f"£{rfm['monetary'].sum()/1e6:.2f}M" if 'monetary' in rfm.columns else "N/A",
        'data_source': 'CSV' if any(os.path.exists(f) for f in ['final_customer_segments.csv', 'final_customer_segments (1).csv']) else 'Enhanced'
    }

# ========== RUN APP ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("RAILWAY_ENVIRONMENT") != "production"
    
    print(f"\n{'='*80}")
    print(f"🚀 STARTING FIXED DASHBOARD ON PORT: {port}")
    print(f"📊 Data: {len(rfm):,} customers")
    print(f"🔧 Debug mode: {debug}")
    print(f"{'='*80}\n")
    
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=False
    )
