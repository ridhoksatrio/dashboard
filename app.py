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

# ========== CUSTOM HTML TEMPLATE (FROM KODE KEDUA) ==========
app.index_string = '''<!DOCTYPE html><html><head>
{%metas%}
<title>Customer Intelligence Dashboard</title>
{%css%}
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Poppins:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Poppins',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);padding:16px;min-height:100vh}
.dash{background:rgba(255,255,255,0.98);border-radius:32px;padding:40px;box-shadow:0 40px 100px rgba(0,0,0,0.4);animation:fadeIn .8s ease-out}
@keyframes fadeIn{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}

/* HEADER */
.hdr{text-align:center;padding:28px 24px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:24px;margin-bottom:36px;position:relative;overflow:hidden;box-shadow:0 15px 40px rgba(102,126,234,0.35)}
.hdr::before{content:'';position:absolute;top:-50%;right:-50%;width:200%;height:200%;background:radial-gradient(circle,rgba(255,255,255,.15),transparent 60%);animation:pulse 4s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scale(1) rotate(0deg)}50%{transform:scale(1.15) rotate(5deg)}}
.title{font-size:3.8rem;font-weight:900;color:#fff;text-shadow:4px 4px 8px rgba(0,0,0,.35);margin:0;letter-spacing:-1.5px;line-height:1.1}
.sub{color:rgba(255,255,255,.95);font-size:1.35rem;margin-top:10px;font-weight:500;letter-spacing:0.5px}

/* METRICS */
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-bottom:36px}
.met{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:22px;padding:32px 28px;text-align:center;color:#fff;box-shadow:0 15px 40px rgba(102,126,234,.45);transition:all .4s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden}
.met::before{content:'';position:absolute;top:-100%;left:-100%;width:300%;height:300%;background:radial-gradient(circle,rgba(255,255,255,.2),transparent 65%);transition:.7s ease}
.met:hover{transform:translateY(-14px) scale(1.05);box-shadow:0 25px 60px rgba(102,126,234,.65)}
.met:hover::before{top:0;left:0}
.met-icon{font-size:3.5rem;margin-bottom:14px;animation:float 3.5s ease-in-out infinite;filter:drop-shadow(2px 2px 4px rgba(0,0,0,0.2))}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.met-val{font-size:3.2rem;font-weight:900;margin:12px 0;text-shadow:3px 3px 6px rgba(0,0,0,.25);letter-spacing:-1px}
.met-lbl{font-size:1rem;text-transform:uppercase;letter-spacing:2.5px;font-weight:700;margin-bottom:6px}
.met-sub{font-size:.88rem;margin-top:8px;opacity:.9;font-weight:500}

/* FILTERS */
.filt{background:linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%);border-radius:22px;padding:32px;margin-bottom:32px;box-shadow:0 10px 30px rgba(0,0,0,.12)}
.filt-t{font-size:1.6rem;font-weight:800;color:#2c3e50;margin-bottom:22px;display:flex;align-items:center;gap:12px}
.filt-g{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.filt-g label{display:block;font-weight:700;color:#34495e;margin-bottom:8px;font-size:1rem;letter-spacing:0.3px}
.Select-control,.rc-slider{border-radius:12px !important}

/* TABS */
.tab-content{padding:28px 0}
.nav-tabs{border:none;gap:12px;margin-bottom:28px}
.nav-tabs .nav-link{border:none;border-radius:16px;padding:14px 32px;font-weight:700;font-size:1.1rem;color:#667eea;background:#f8f9fa;transition:all .3s;letter-spacing:0.5px}
.nav-tabs .nav-link:hover{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;transform:translateY(-3px);box-shadow:0 8px 20px rgba(102,126,234,.35)}
.nav-tabs .nav-link.active{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;box-shadow:0 8px 20px rgba(102,126,234,.4)}

/* CHARTS */
.charts{display:grid;grid-template-columns:repeat(2,1fr);gap:26px;margin-bottom:26px}
.chart{background:#fff;border-radius:24px;padding:32px;box-shadow:0 10px 35px rgba(0,0,0,.08);transition:all .35s ease;border:3px solid transparent}
.chart:hover{transform:translateY(-6px);box-shadow:0 20px 50px rgba(0,0,0,.15);border-color:#667eea}
.chart-full{grid-column:1/-1}

/* DISTRIBUTION GRID */
.dist-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin-bottom:26px}
.dist-chart{background:#fff;border-radius:20px;padding:24px;box-shadow:0 8px 25px rgba(0,0,0,.08);transition:all 0.3s ease;border:2px solid transparent}
.dist-chart:hover{transform:translateY(-5px);box-shadow:0 15px 35px rgba(0,0,0,.12);border-color:#667eea}
.dist-title{font-size:1.3rem;font-weight:700;color:#2c3e50;margin-bottom:15px;text-align:center}
.dist-axis{font-size:0.9rem;font-weight:600;color:#7f8c8d;text-align:center;margin-top:10px}

/* STRATEGY CARDS */
.strat-g{display:grid;grid-template-columns:repeat(2,1fr);gap:26px}
.strat{border-radius:24px;padding:36px 32px;color:#fff;box-shadow:0 15px 40px rgba(0,0,0,.22);transition:all .45s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden}
.strat::after{content:'';position:absolute;bottom:-50px;right:-50px;width:200px;height:200px;background:rgba(255,255,255,.12);border-radius:50%;transition:.6s ease}
.strat:hover{transform:translateY(-8px) scale(1.03);box-shadow:0 25px 60px rgba(0,0,0,.32)}
.strat:hover::after{bottom:-20px;right:-20px;width:240px;height:240px}
.strat-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;flex-wrap:wrap;gap:12px}
.strat-name{font-size:2.2rem;font-weight:900;text-shadow:3px 3px 6px rgba(0,0,0,.25);letter-spacing:-0.5px}
.pri-badge{padding:10px 22px;border-radius:24px;font-weight:800;font-size:.95rem;letter-spacing:1.5px;background:rgba(255,255,255,.25);backdrop-filter:blur(10px);animation:glow 2.5s ease-in-out infinite;box-shadow:0 4px 15px rgba(0,0,0,.15)}
@keyframes glow{0%,100%{box-shadow:0 0 15px rgba(255,255,255,.3)}50%{box-shadow:0 0 28px rgba(255,255,255,.6)}}
.strat-sub{font-size:1.3rem;font-weight:700;margin-bottom:20px;opacity:.95;letter-spacing:0.3px}
.tactics{background:rgba(255,255,255,.12);border-radius:16px;padding:22px;margin:20px 0;backdrop-filter:blur(12px);box-shadow:inset 0 2px 8px rgba(0,0,0,.1)}
.tact-t{font-size:1.2rem;font-weight:800;margin-bottom:14px;letter-spacing:0.5px}
.tact{padding:14px 18px;margin:10px 0;background:rgba(255,255,255,.18);border-radius:12px;transition:all .3s ease;border-left:4px solid rgba(255,255,255,.45);font-weight:600;font-size:1.02rem}
.tact:hover{background:rgba(255,255,255,.28);transform:translateX(8px);border-left-width:6px;box-shadow:0 4px 12px rgba(0,0,0,.1)}
.kpi-g{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:20px 0}
.kpi{background:rgba(255,255,255,.16);padding:12px;border-radius:10px;font-weight:700;text-align:center;backdrop-filter:blur(8px);font-size:1.02rem;letter-spacing:0.3px}
.budget{display:flex;justify-content:space-between;margin-top:20px;padding:18px;background:rgba(255,255,255,.16);border-radius:12px;backdrop-filter:blur(10px);gap:12px}
.budget div{text-align:center;flex:1}
.budget-l{font-size:.92rem;opacity:.92;margin-bottom:6px;font-weight:600;letter-spacing:0.5px}
.budget-v{font-size:1.8rem;font-weight:900;letter-spacing:-0.5px}

/* CHAMPION BREAKDOWN */
.champ-break{background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:24px;padding:36px;color:#fff;margin:26px 0;box-shadow:0 15px 40px rgba(255,215,0,.4)}
.champ-break-t{font-size:2rem;font-weight:900;margin-bottom:26px;letter-spacing:-0.5px;text-align:center}
.champ-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}
.champ-card{background:rgba(255,255,255,.16);border-radius:16px;padding:24px;backdrop-filter:blur(10px);transition:all .35s ease;box-shadow:0 4px 15px rgba(0,0,0,.1);border-left:5px solid rgba(255,255,255,.5)}
.champ-card:hover{background:rgba(255,255,255,.26);transform:translateY(-4px) translateX(4px);box-shadow:0 8px 25px rgba(0,0,0,.15);border-left-width:8px}
.champ-num{font-size:2.5rem;font-weight:900;margin-bottom:8px;text-shadow:2px 2px 4px rgba(0,0,0,.2)}
.champ-tier{font-size:1.3rem;font-weight:800;margin-bottom:12px;letter-spacing:0.3px}
.champ-desc{font-size:1.05rem;margin-bottom:12px;opacity:.95;line-height:1.5}
.champ-char{font-size:.95rem;background:rgba(255,255,255,.2);padding:10px;border-radius:8px;font-weight:600;margin-top:8px}

/* INSIGHTS */
.ins{background:linear-gradient(135deg,#4facfe 0%,#00f2fe 100%);border-radius:24px;padding:36px;color:#fff;margin:26px 0;box-shadow:0 15px 40px rgba(79,172,254,.4)}
.ins-t{font-size:2rem;font-weight:900;margin-bottom:26px;letter-spacing:-0.5px}
.ins-g{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}
.ins-card{background:rgba(255,255,255,.16);border-radius:16px;padding:24px;backdrop-filter:blur(10px);transition:all .35s ease;box-shadow:0 4px 15px rgba(0,0,0,.1)}
.ins-card:hover{background:rgba(255,255,255,.26);transform:translateY(-4px);box-shadow:0 8px 25px rgba(0,0,0,.15)}
.ins-h{font-size:1.35rem;font-weight:800;margin-bottom:16px;letter-spacing:0.3px}
.ins-list{list-style:none;padding:0}
.ins-list li{padding:10px 0;border-bottom:1px solid rgba(255,255,255,.25);font-size:1.02rem;font-weight:500;letter-spacing:0.2px}
.ins-list li:last-child{border-bottom:none}

/* FOOTER */
.foot{text-align:center;margin-top:50px;padding:26px;border-top:4px solid #667eea;color:#7f8c8d;font-size:1.05rem;font-weight:600;letter-spacing:0.5px}

/* RESPONSIVE */
@media(max-width:1200px){
    .metrics,.charts,.strat-g,.ins-g{grid-template-columns:repeat(2,1fr)}
    .filt-g{grid-template-columns:1fr}
    .chart-full,.dist-grid{grid-column:1/-1}
    .dist-grid{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:768px){
    .metrics,.charts,.strat-g,.ins-g,.dist-grid{grid-template-columns:1fr}
    .title{font-size:2.8rem}
    .dash{padding:24px}
}
</style>
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>'''

# ========== CREATE INITIAL FIGURES (OPTIMIZED FROM KODE KEDUA) ==========
def create_initial_figures(data):
    """Create initial figures for dashboard - optimized version"""
    try:
        # Pastikan data memiliki kolom Cluster_Label
        if 'Cluster_Label' not in data.columns:
            print("⚠️ Warning: Cluster_Label not found, creating default labels")
            data['Cluster_Label'] = data['Cluster_KMeans'].apply(lambda x: f"Segment {x}")
        
        # 1. Customer Distribution Pie
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
        
        # 2. Revenue by Segment
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
        
        # 3. 3D RFM Analysis
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
        
        # 4-6. Distribusi seperti pada gambar (Recovery, Frequency, Monetary)
        def create_distribution_histogram(col, title, xaxis_title, color):
            """Create clean histogram like in the image"""
            fig = go.Figure()
            
            # Add histogram trace
            fig.add_trace(go.Histogram(
                x=data[col],
                nbinsx=30,
                marker=dict(
                    color=color,
                    line=dict(color='white', width=1),
                    opacity=0.85
                ),
                name=title,
                hovertemplate=f'<b>{title}</b><br>{xaxis_title}: %{{x}}<br>Number of Customers: %{{y}}<extra></extra>'
            ))
            
            # Calculate statistics
            mean_val = data[col].mean()
            median_val = data[col].median()
            
            # Add vertical lines for mean and median
            fig.add_vline(
                x=mean_val, 
                line_dash="dash", 
                line_color="#ff6b6b",
                annotation_text=f"Mean: {mean_val:.1f}",
                annotation_position="top right"
            )
            
            fig.add_vline(
                x=median_val, 
                line_dash="dot", 
                line_color="#45b7d1",
                annotation_text=f"Median: {median_val:.1f}",
                annotation_position="top left"
            )
            
            fig.update_layout(
                title={'text': f"<b>{title}</b>", 'x': 0.5,
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
        
        # Create the three distribution histograms as in the image
        hist_recency = create_distribution_histogram(
            'Recency', 
            '⏰ Recovery Distribution', 
            'Days Since Last Purchase', 
            '#667eea'  # Blue color
        )
        
        hist_frequency = create_distribution_histogram(
            'Frequency', 
            '🔄 Frequency Distribution', 
            'Number of Purchases', 
            '#38ef7d'  # Green color
        )
        
        hist_monetary = create_distribution_histogram(
            'Monetary', 
            '💵 Monetary Distribution', 
            'Total Spend (£)', 
            '#f093fb'  # Purple color
        )
        
        # 7. Segment Summary Table
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
        
        print("✅ Initial figures created successfully")
        return [pie_fig, bar_fig, scatter_fig, hist_recency, hist_frequency, hist_monetary, table_fig]
    
    except Exception as e:
        print(f"❌ Error creating initial figures: {e}")
        traceback.print_exc()
        # Create simple empty figures as fallback
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title={'text': "Error loading figure", 'x': 0.5},
            height=300,
            plot_bgcolor='white'
        )
        return [empty_fig] * 7

# Create initial figures
initial_figures = create_initial_figures(rfm)
print("✅ Initial figures created with enhanced visuals")

# ========== APP LAYOUT (OPTIMIZED FROM KODE KEDUA) ==========
app.layout = html.Div([
    html.Div([
        # Header
        html.Div([
            html.H1("🎯 Customer Intelligence Hub", className="title"),
            html.P("Customer Segmentation for Personalized Retail Marketing", className="sub")
        ], className="hdr"),
        
        # Metrics
        html.Div([
            html.Div([
                html.Div("👥", className="met-icon"),
                html.Div(f"{len(rfm):,}", className="met-val"),
                html.Div("Customers", className="met-lbl"),
                html.Div("Active Database", className="met-sub")
            ], className="met"),
            
            html.Div([
                html.Div("🎯", className="met-icon"),
                html.Div(f"{rfm['Cluster_KMeans'].nunique()}", className="met-val"),
                html.Div("Segments", className="met-lbl"),
                html.Div("AI-Classified", className="met-sub")
            ], className="met"),
            
            html.Div([
                html.Div("💰", className="met-icon"),
                html.Div(f"£{rfm['Monetary'].sum()/1e6:.2f}M", className="met-val"),
                html.Div("Revenue", className="met-lbl"),
                html.Div(f"Avg £{rfm['Monetary'].mean():.0f}", className="met-sub")
            ], className="met"),
            
            html.Div([
                html.Div("📈", className="met-icon"),
                html.Div(f"£{rfm['AvgOrderValue'].mean():.0f}", className="met-val"),
                html.Div("Avg Order", className="met-lbl"),
                html.Div(f"Peak £{rfm['AvgOrderValue'].max():.0f}", className="met-sub")
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
                        min=int(rfm['RFM_Score'].min()),
                        max=int(rfm['RFM_Score'].max()),
                        value=[int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())],
                        marks={i: {'label': str(i), 'style': {'fontWeight': '600'}}
                               for i in range(int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())+1, 2)},
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
                    # Row 1
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='g1', 
                                figure=initial_figures[0],
                                config={'displayModeBar': True, 'displaylogo': False}
                            )
                        ], className="chart"),
                        
                        html.Div([
                            dcc.Graph(
                                id='g2',
                                figure=initial_figures[1],
                                config={'displayModeBar': True, 'displaylogo': False}
                            )
                        ], className="chart")
                    ], className="charts"),
                    
                    # Row 2
                    html.Div([
                        dcc.Graph(
                            id='g3',
                            figure=initial_figures[2],
                            config={'displayModeBar': True, 'displaylogo': False}
                        )
                    ], className="chart chart-full"),
                    
                    # Row 3 - Distribution Charts (Recovery, Frequency, Monetary)
                    html.Div([
                        html.Div([
                            html.Div("⏰ Recovery Distribution", className="dist-title"),
                            html.Div("Days Since Last Purchase", className="dist-axis"),
                            dcc.Graph(
                                id='g4',
                                figure=initial_figures[3],
                                config={'displayModeBar': True, 'displaylogo': False}
                            )
                        ], className="dist-chart"),
                        
                        html.Div([
                            html.Div("🔄 Frequency Distribution", className="dist-title"),
                            html.Div("Number of Purchases", className="dist-axis"),
                            dcc.Graph(
                                id='g5',
                                figure=initial_figures[4],
                                config={'displayModeBar': True, 'displaylogo': False}
                            )
                        ], className="dist-chart"),
                        
                        html.Div([
                            html.Div("💵 Monetary Distribution", className="dist-title"),
                            html.Div("Total Spend (£)", className="dist-axis"),
                            dcc.Graph(
                                id='g6',
                                figure=initial_figures[5],
                                config={'displayModeBar': True, 'displaylogo': False}
                            )
                        ], className="dist-chart")
                    ], className="dist-grid"),
                    
                    # Row 4
                    html.Div([
                        dcc.Graph(
                            id='g7',
                            figure=initial_figures[6],
                            config={'displayModeBar': True, 'displaylogo': False}
                        )
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
        ]),
        
        # Footer
        html.Div([
            html.Hr(style={'margin': '40px 0', 'border': 'none', 'height': '2px', 
                          'background': 'linear-gradient(90deg, #667eea, #764ba2, #f093fb)'}),
            html.Div([
                html.P(f"✅ Dashboard loaded successfully | {len(rfm):,} customers | {rfm['Cluster_KMeans'].nunique()} segments",
                      style={'marginBottom': '10px'}),
                html.P(f"Data: {'CSV' if any(os.path.exists(f) for f in ['final_customer_segments.csv', 'final_customer_segments (1).csv']) else 'Enhanced'} | Deployed on Railway",
                      style={'marginBottom': '0'})
            ], className="foot")
        ])
    ], className="dash"),
    
    # Hidden div to store initial data
    dcc.Store(id='store-data', data=rfm.to_dict('records'))
])

# ========== CALLBACK FUNCTIONS (OPTIMIZED FROM KODE KEDUA) ==========
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
    """Main callback for updating all dashboard elements - optimized version"""
    try:
        print(f"\n🔄 Updating dashboard with filters:")
        print(f"   Segment: {segment}, RFM Range: {rfm_range}, Priority: {priority}")
        
        # Filter data
        df = rfm[(rfm['RFM_Score'] >= rfm_range[0]) & (rfm['RFM_Score'] <= rfm_range[1])]
        
        if segment != 'all':
            df = df[df['Cluster_KMeans'] == segment]
        
        if priority != 'all':
            df = df[df['Priority'] == priority]
        
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
        
        # 1. Customer Distribution Pie
        try:
            cluster_counts = df['Cluster_Label'].value_counts()
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
                    text=f'<b>{len(df):,}</b><br><span style="font-size:14px">Customers</span>',
                    x=0.5, y=0.5,
                    font={'size': 24, 'color': '#667eea', 'family': 'Inter, Poppins'},
                    showarrow=False
                )],
                margin=dict(t=80, b=40, l=40, r=40)
            )
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            pie_fig = initial_figures[0]
        
        # 2. Revenue by Segment
        try:
            revenue_by_segment = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
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
            print(f"Error creating bar chart: {e}")
            bar_fig = initial_figures[1]
        
        # 3. 3D RFM Analysis
        try:
            sample_size = min(500, len(df))
            scatter_fig = go.Figure(go.Scatter3d(
                x=df['Recency'].sample(sample_size, random_state=42),
                y=df['Frequency'].sample(sample_size, random_state=42),
                z=df['Monetary'].sample(sample_size, random_state=42),
                mode='markers',
                marker=dict(
                    size=7,
                    color=df['Cluster_KMeans'].sample(sample_size, random_state=42),
                    colorscale='Rainbow',
                    showscale=True,
                    line=dict(width=0.8, color='white'),
                    opacity=0.88,
                    colorbar=dict(title='Cluster', thickness=20, len=0.7)
                ),
                text=df['Cluster_Label'].sample(sample_size, random_state=42),
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
            print(f"Error creating 3D scatter: {e}")
            scatter_fig = initial_figures[2]
        
        # 4-6. Distribusi seperti pada gambar (Recovery, Frequency, Monetary)
        def create_distribution_histogram(col, title, xaxis_title, color, default_fig_index):
            try:
                fig = go.Figure()
                
                # Add histogram trace
                fig.add_trace(go.Histogram(
                    x=df[col],
                    nbinsx=30,
                    marker=dict(
                        color=color,
                        line=dict(color='white', width=1),
                        opacity=0.85
                    ),
                    name=title,
                    hovertemplate=f'<b>{title}</b><br>{xaxis_title}: %{{x}}<br>Number of Customers: %{{y}}<extra></extra>'
                ))
                
                # Calculate statistics
                mean_val = df[col].mean()
                median_val = df[col].median()
                
                # Add vertical lines for mean and median
                fig.add_vline(
                    x=mean_val, 
                    line_dash="dash", 
                    line_color="#ff6b6b",
                    annotation_text=f"Mean: {mean_val:.1f}",
                    annotation_position="top right"
                )
                
                fig.add_vline(
                    x=median_val, 
                    line_dash="dot", 
                    line_color="#45b7d1",
                    annotation_text=f"Median: {median_val:.1f}",
                    annotation_position="top left"
                )
                
                fig.update_layout(
                    title={'text': f"<b>{title}</b>", 'x': 0.5,
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
                print(f"Error creating histogram for {col}: {e}")
                return initial_figures[default_fig_index]
        
        # Create the three distribution histograms
        hist_recency = create_distribution_histogram(
            'Recency', 
            '⏰ Recovery Distribution', 
            'Days Since Last Purchase', 
            '#667eea',  # Blue color
            3
        )
        
        hist_frequency = create_distribution_histogram(
            'Frequency', 
            '🔄 Frequency Distribution', 
            'Number of Purchases', 
            '#38ef7d',  # Green color
            4
        )
        
        hist_monetary = create_distribution_histogram(
            'Monetary', 
            '💵 Monetary Distribution', 
            'Total Spend (£)', 
            '#f093fb',  # Purple color
            5
        )
        
        # 7. Segment Summary Table
        try:
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
            print(f"Error creating table: {e}")
            table_fig = initial_figures[6]
        
        # 8. Champion Breakdown
        champion_breakdown = None
        try:
            champion_clusters = [c for c in df['Cluster_KMeans'].unique() 
                               if c in profs and profs[c]['name'] == '🏆 Champions']
            
            if champion_clusters:
                champ_cards = []
                for cid in sorted(champion_clusters):
                    if cid in champion_details:
                        detail = champion_details[cid]
                        count = len(df[df['Cluster_KMeans'] == cid])
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
        except Exception as e:
            print(f"Error creating champion breakdown: {e}")
            champion_breakdown = html.Div([
                html.H4("Champion breakdown not available", style={'textAlign': 'center', 'color': '#ff6b6b'})
            ])
        
        # 9. Strategy Cards
        strategy_cards = []
        try:
            for cid, strat in profs.items():
                if segment == 'all' or segment == cid:
                    customer_count = len(df[df['Cluster_KMeans'] == cid])
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
                                ])
                            ], className="budget")
                        ], className="strat", style={'background': strat['grad']}))
        except Exception as e:
            print(f"Error creating strategy cards: {e}")
            strategy_cards = [html.Div("Strategy cards not available", 
                                      style={'textAlign': 'center', 'padding': '50px', 'color': '#667eea'})]
        
        # 10. AI Insights
        try:
            insights = html.Div([
                html.Div("🧠 AI-Powered Insights & Recommendations", className="ins-t"),
                html.Div([
                    html.Div([
                        html.Div("📊 Top Performers", className="ins-h"),
                        html.Ul([
                            html.Li(f"🏆 Highest Revenue: {df.groupby('Cluster_Label')['Monetary'].sum().idxmax()}"),
                            html.Li(f"👥 Largest Group: {df['Cluster_Label'].value_counts().idxmax()} ({df['Cluster_Label'].value_counts().max():,} customers)"),
                            html.Li(f"💰 Best AOV: {df.groupby('Cluster_Label')['AvgOrderValue'].mean().idxmax()} (£{df.groupby('Cluster_Label')['AvgOrderValue'].mean().max():.0f})"),
                            html.Li(f"🔄 Most Frequent: {df.groupby('Cluster_Label')['Frequency'].mean().idxmax()} ({df.groupby('Cluster_Label')['Frequency'].mean().max():.1f} orders)")
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
        except Exception as e:
            print(f"Error creating insights: {e}")
            insights = html.Div([
                html.H4("Insights not available", style={'textAlign': 'center', 'color': '#667eea'})
            ])
        
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
        'segments': rfm['Cluster_KMeans'].nunique(),
        'revenue': f"£{rfm['Monetary'].sum()/1e6:.2f}M",
        'data_source': 'CSV' if any(os.path.exists(f) for f in ['final_customer_segments.csv', 'final_customer_segments (1).csv']) else 'Enhanced',
        'debug': {
            'csv_exists': any(os.path.exists(f) for f in ['final_customer_segments.csv', 'final_customer_segments (1).csv']),
            'files': os.listdir('.'),
            'python': sys.version
        }
    }

# ========== RUN APP ==========
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("RAILWAY_ENVIRONMENT") != "production"
    
    print(f"\n{'='*80}")
    print(f"🚀 STARTING OPTIMIZED DASHBOARD ON PORT: {port}")
    print(f"📊 Data: {len(rfm):,} customers, {rfm['Cluster_KMeans'].nunique()} segments")
    print(f"💰 Revenue: £{rfm['Monetary'].sum()/1e6:.2f}M")
    print(f"🎨 Visual Features: Enhanced from kode kedua")
    print(f"🔧 Debug mode: {debug}")
    print(f"{'='*80}\n")
    
    # Important for Railway: Disable hot reload
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=False,
        dev_tools_ui=False,
        dev_tools_props_check=False
    )
