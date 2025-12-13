
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Customer Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load & Prepare Data
@st.cache_data
def load_data():
    try:
        rfm = pd.read_csv('final_customer_segments (1).csv', index_col=0)
    except:
        try:
            rfm = pd.read_csv('final_customer_segments.csv', index_col=0)
        except:
            # Create sample data if file not found
            st.error("Data file not found. Using sample data for demonstration.")
            np.random.seed(42)
            n_samples = 1000
            rfm = pd.DataFrame({
                'Recency': np.random.randint(1, 365, n_samples),
                'Frequency': np.random.randint(1, 50, n_samples),
                'Monetary': np.random.uniform(100, 50000, n_samples),
                'AvgOrderValue': np.random.uniform(50, 500, n_samples),
                'RFM_Score': np.random.randint(100, 600, n_samples),
                'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5], n_samples, p=[0.2, 0.1, 0.15, 0.1, 0.25, 0.2])
            })
            rfm.index = [f'CUST_{i:04d}' for i in range(n_samples)]
    
    # Ensure required columns exist
    required_cols = ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score', 'Cluster_KMeans']
    for col in required_cols:
        if col not in rfm.columns:
            if col == 'Cluster_KMeans':
                rfm[col] = 0  # Default cluster
            else:
                rfm[col] = 0  # Default value
    
    return rfm

rfm = load_data()

# Cluster Strategies
strats = {
    'champions': {'name':'🏆 Champions','grad':'linear-gradient(135deg,#FFD700,#FFA500, #FF8C00)','color':'#FFD700','priority':'CRITICAL','strategy':'VIP Platinum','tactics':['💎 Exclusive Early Access','🎁 Premium Gifts','📞 24/7 Manager','🌟 VIP Events','✨ Celebrations'],'kpis':['Retention>95%','Upsell>40%','Referral>30%'],'budget':'30%','roi':'500%'},
    'loyal': {'name':'💎 Loyal','grad':'linear-gradient(135deg,#667eea,#764ba2,#5a52a3)','color':'#667eea','priority':'HIGH','strategy':'Loyalty Boost','tactics':['🎯 Tiered Rewards','📱 App Benefits','🎉 Birthday Offers','💝 Referral Bonus','🔔 Flash Access'],'kpis':['Retention>85%','Frequency+20%','NPS>8'],'budget':'25%','roi':'380%'},
    'big': {'name':'💰 Big Spenders','grad':'linear-gradient(135deg,#f093fb,#f5576c,#d2368d)','color':'#f093fb','priority':'CRITICAL','strategy':'Value Max','tactics':['💳 Flex Terms','🎁 Luxury Gifts','🚚 Free Express','📦 Custom Bundles','🌟 Concierge'],'kpis':['AOV+15%','Retention>90%','Sat>4.8/5'],'budget':'20%','roi':'420%'},
    'dormant': {'name':'😴 Dormant','grad':'linear-gradient(135deg,#ff6b6b,#ee5a6f,#c44569)','color':'#ff6b6b','priority':'URGENT','strategy':'Win-Back','tactics':['🎁 25-30% Off','📧 Multi-Channel','🎯 Retargeting','💬 Personal Call','⏰ Urgency'],'kpis':['Winback>25%','Response>15%','ROI>200%'],'budget':'15%','roi':'250%'},
    'potential': {'name':'🌱 Potential','grad':'linear-gradient(135deg,#11998e,#38ef7d,#00b09b)','color':'#11998e','priority':'MEDIUM','strategy':'Fast Convert','tactics':['🎓 Education','🎁 15% 2nd Buy','💌 Welcome Flow','📚 Tutorials','🎯 Cross-Sell'],'kpis':['Convert>35%','2nd<30d','LTV+25%'],'budget':'5%','roi':'180%'},
    'standard': {'name':'📊 Standard','grad':'linear-gradient(135deg,#89f7fe,#66a6ff,#4a6fff)','color':'#89f7fe','priority':'MEDIUM','strategy':'Steady Engage','tactics':['📧 Newsletters','🎯 Seasonal','💌 AI Recs','🎁 Surprises','📱 Community'],'kpis':['Engage>40%','Stable','Sat>3.5/5'],'budget':'5%','roi':'150%'}
}

# Champion Sub-segments Explanation
champion_details = {
    1: {'tier':'Platinum Elite','desc':'Super frequent buyers with highest engagement','char':'11d recency, 15.6 orders, £5,425 spend'},
    3: {'tier':'Ultra VIP','desc':'Extreme high-value with massive order frequency','char':'8d recency, 38.9 orders, £40,942 spend'},
    4: {'tier':'Gold Tier','desc':'Consistent champions with solid performance','char':'1d recency, 10.9 orders, £3,981 spend'},
    6: {'tier':'Diamond Elite','desc':'Ultra frequent buyers with exceptional loyalty','char':'1d recency, 126.8 orders, £33,796 spend'}
}

def get_strat(cid, data):
    cd = data[data['Cluster_KMeans'] == cid]
    if len(cd) == 0:
        return {**strats['standard'], 'cluster_id': cid}
    
    r = cd['Recency'].mean() if 'Recency' in cd.columns else 100
    f = cd['Frequency'].mean() if 'Frequency' in cd.columns else 5
    m = cd['Monetary'].mean() if 'Monetary' in cd.columns else 500
    
    if pd.isna(r) or pd.isna(f) or pd.isna(m):
        s = 'standard'
    elif r < 50 and f > 10 and m > 1000: 
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

# Inisialisasi profs dan colors
@st.cache_data
def init_data(rfm):
    profs = {}
    for c in rfm['Cluster_KMeans'].unique():
        p = get_strat(c, rfm)
        profs[c] = p
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name']} (C{c})"
        rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']
    
    colors = {}
    for c, p in profs.items():
        label = f"{p['name']} (C{c})"
        colors[label] = p['color']
    
    return profs, colors, rfm

profs, colors, rfm = init_data(rfm)

# CSS Custom untuk Streamlit yang lebih modern
st.markdown("""
<style>
    * {margin: 0; padding: 0; box-sizing: border-box}
    body {font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; min-height: 100vh}
    .stApp {background: transparent !important; padding: 0 !important; max-width: 100% !important}
    
    /* SIDEBAR */
    .st-emotion-cache-1cypcdb {background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; border-right: 1px solid #334155}
    .st-emotion-cache-16txtl3 {padding: 2rem 1.5rem !important}
    
    /* HEADER dengan glassmorphism */
    .header-container {background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); 
                      border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding: 1.5rem 2rem; position: sticky; top: 0; z-index: 1000}
    .main-header {display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem}
    .header-title {font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0}
    .header-subtitle {color: #94a3b8; font-size: 1rem; margin-top: 0.25rem; font-weight: 400}
    .header-stats {display: flex; gap: 1.5rem; flex-wrap: wrap}
    .stat-item {display: flex; flex-direction: column; align-items: center; padding: 0.75rem 1.25rem; 
                background: rgba(30, 41, 59, 0.7); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05)}
    .stat-value {font-size: 1.25rem; font-weight: 700; color: #fff; margin-bottom: 0.25rem}
    .stat-label {font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em}
    
    /* METRICS GRID dengan neumorphism */
    .metrics-grid {display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0}
    @media (max-width: 1200px) {.metrics-grid {grid-template-columns: repeat(2, 1fr)}}
    @media (max-width: 768px) {.metrics-grid {grid-template-columns: 1fr}}
    .metric-card {background: rgba(30, 41, 59, 0.8); border-radius: 16px; padding: 1.5rem; 
                  border: 1px solid rgba(255, 255, 255, 0.05); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                  position: relative; overflow: hidden}
    .metric-card:hover {transform: translateY(-4px); border-color: rgba(102, 126, 234, 0.3); 
                       box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3)}
    .metric-card::before {content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; 
                         background: linear-gradient(90deg, #667eea, #764ba2)}
    .metric-icon {font-size: 2rem; margin-bottom: 1rem; display: inline-block}
    .metric-value {font-size: 2rem; font-weight: 800; color: #fff; margin: 0.5rem 0; line-height: 1}
    .metric-label {font-size: 0.875rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600}
    .metric-change {font-size: 0.75rem; display: flex; align-items: center; gap: 0.25rem; margin-top: 0.5rem}
    .change-positive {color: #10b981}
    .change-negative {color: #ef4444}
    
    /* FILTER SECTION */
    .filter-section {background: rgba(30, 41, 59, 0.8); border-radius: 16px; padding: 1.5rem; 
                    margin: 1.5rem 0; border: 1px solid rgba(255, 255, 255, 0.05)}
    .filter-title {font-size: 1.25rem; font-weight: 700; color: #fff; margin-bottom: 1rem; 
                  display: flex; align-items: center; gap: 0.5rem}
    .filter-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem}
    @media (max-width: 768px) {.filter-grid {grid-template-columns: 1fr}}
    
    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {gap: 0.5rem; margin-bottom: 1.5rem}
    .stTabs [data-baseweb="tab"] {background: rgba(30, 41, 59, 0.5) !important; border: 1px solid rgba(255, 255, 255, 0.05) !important;
                                  border-radius: 12px !important; padding: 0.75rem 1.5rem !important; 
                                  color: #94a3b8 !important; font-weight: 600 !important; transition: all 0.3s ease}
    .stTabs [data-baseweb="tab"]:hover {background: rgba(30, 41, 59, 0.8) !important; color: #fff !important; 
                                       border-color: rgba(102, 126, 234, 0.3) !important}
    .stTabs [aria-selected="true"] {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; 
                                   color: #fff !important; border-color: transparent !important;
                                   box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important}
    
    /* CHARTS CONTAINER */
    .chart-container {background: rgba(30, 41, 59, 0.8); border-radius: 16px; padding: 1.5rem; 
                     border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 1.5rem}
    .chart-title {font-size: 1.125rem; font-weight: 700; color: #fff; margin-bottom: 1rem; 
                 display: flex; align-items: center; gap: 0.5rem}
    .charts-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 1.5rem}
    @media (max-width: 1200px) {.charts-grid {grid-template-columns: 1fr}}
    .chart-full {grid-column: 1 / -1}
    
    /* STRATEGY CARDS */
    .strategy-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 1.5rem}
    @media (max-width: 1200px) {.strategy-grid {grid-template-columns: 1fr}}
    .strategy-card {border-radius: 16px; padding: 1.5rem; color: #fff; 
                   border: 1px solid rgba(255, 255, 255, 0.1); position: relative; overflow: hidden;
                   transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1)}
    .strategy-card:hover {transform: translateY(-6px); box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3)}
    .strategy-header {display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem}
    .strategy-name {font-size: 1.5rem; font-weight: 800; margin: 0; line-height: 1.2}
    .priority-badge {padding: 0.375rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700;
                    text-transform: uppercase; letter-spacing: 0.05em; background: rgba(255, 255, 255, 0.2);
                    backdrop-filter: blur(10px)}
    .strategy-subtitle {font-size: 1rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; font-weight: 500}
    .tactics-section {background: rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 1rem; margin: 1rem 0;
                     backdrop-filter: blur(10px)}
    .tactics-title {font-size: 0.875rem; font-weight: 700; color: rgba(255, 255, 255, 0.9); margin-bottom: 0.75rem;
                   text-transform: uppercase; letter-spacing: 0.05em}
    .tactics-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem}
    @media (max-width: 768px) {.tactics-grid {grid-template-columns: 1fr}}
    .tactic-item {background: rgba(255, 255, 255, 0.15); border-radius: 8px; padding: 0.75rem; font-size: 0.875rem;
                 transition: all 0.2s ease; border-left: 3px solid transparent}
    .tactic-item:hover {background: rgba(255, 255, 255, 0.2); transform: translateX(4px); 
                       border-left-color: rgba(255, 255, 255, 0.5)}
    .kpis-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin: 1rem 0}
    .kpi-item {background: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 0.75rem; text-align: center;
              font-size: 0.875rem; font-weight: 600}
    .strategy-footer {display: flex; justify-content: space-between; margin-top: 1.5rem; padding-top: 1rem;
                     border-top: 1px solid rgba(255, 255, 255, 0.1)}
    .budget-item {text-align: center}
    .budget-label {font-size: 0.75rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem}
    .budget-value {font-size: 1.5rem; font-weight: 800}
    
    /* CHAMPION BREAKDOWN */
    .champion-section {background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 140, 0, 0.1) 100%); 
                      border: 1px solid rgba(255, 215, 0, 0.2); border-radius: 16px; padding: 1.5rem; margin: 1.5rem 0}
    .champion-title {font-size: 1.5rem; font-weight: 800; color: #FFD700; margin-bottom: 1rem; 
                    display: flex; align-items: center; gap: 0.5rem}
    .champion-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem}
    @media (max-width: 768px) {.champion-grid {grid-template-columns: 1fr}}
    .champion-card {background: rgba(255, 215, 0, 0.1); border: 1px solid rgba(255, 215, 0, 0.2); 
                   border-radius: 12px; padding: 1rem; transition: all 0.3s ease}
    .champion-card:hover {background: rgba(255, 215, 0, 0.15); transform: translateY(-2px)}
    .champion-number {font-size: 1.25rem; font-weight: 800; color: #FFD700; margin-bottom: 0.5rem}
    .champion-tier {font-size: 1rem; font-weight: 700; color: #fff; margin-bottom: 0.5rem}
    .champion-desc {font-size: 0.875rem; color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem}
    .champion-chars {font-size: 0.75rem; color: rgba(255, 215, 0, 0.9); background: rgba(255, 215, 0, 0.1);
                    padding: 0.5rem; border-radius: 6px}
    
    /* INSIGHTS SECTION */
    .insights-section {background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%);
                      border: 1px solid rgba(79, 172, 254, 0.2); border-radius: 16px; padding: 1.5rem; margin: 1.5rem 0}
    .insights-title {font-size: 1.5rem; font-weight: 800; color: #4facfe; margin-bottom: 1rem;
                    display: flex; align-items: center; gap: 0.5rem}
    .insights-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem}
    @media (max-width: 768px) {.insights-grid {grid-template-columns: 1fr}}
    .insight-card {background: rgba(79, 172, 254, 0.1); border: 1px solid rgba(79, 172, 254, 0.2); 
                  border-radius: 12px; padding: 1rem}
    .insight-heading {font-size: 1.125rem; font-weight: 700; color: #4facfe; margin-bottom: 0.75rem}
    .insight-list {list-style: none; padding: 0}
    .insight-list li {padding: 0.5rem 0; border-bottom: 1px solid rgba(79, 172, 254, 0.2); color: rgba(255, 255, 255, 0.9)}
    .insight-list li:last-child {border-bottom: none}
    
    /* FOOTER */
    .footer {text-align: center; padding: 1.5rem; margin-top: 2rem; color: #94a3b8; font-size: 0.875rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05)}
    
    /* UTILITY CLASSES */
    .empty-state {text-align: center; padding: 3rem; color: #94a3b8}
    .empty-icon {font-size: 3rem; margin-bottom: 1rem; opacity: 0.5}
    
    /* STREAMLIT WIDGET OVERRIDES */
    div[data-testid="stSelectbox"] > div {background: rgba(30, 41, 59, 0.8); border-color: rgba(255, 255, 255, 0.1)}
    div[data-testid="stSlider"] > div {background: rgba(30, 41, 59, 0.8)}
    .stSlider > div > div > div {background: linear-gradient(90deg, #667eea, #764ba2)}
</style>
""", unsafe_allow_html=True)

# Fungsi untuk membuat chart yang lebih modern
def create_charts(df):
    # Chart 1: Customer Distribution Donut
    cc = df['Cluster_Label'].value_counts()
    
    fig1 = go.Figure(go.Pie(
        labels=cc.index, 
        values=cc.values, 
        hole=0.6,
        marker=dict(
            colors=[colors.get(l, '#64748b') for l in cc.index],
            line=dict(color='#0f172a', width=2)
        ),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        textfont=dict(color='white'),
        insidetextorientation='radial'
    ))
    fig1.update_layout(
        title=dict(
            text="🎯 Customer Distribution",
            font=dict(color='white', size=16),
            x=0.5
        ),
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            font=dict(color='white'),
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )
    
    # Chart 2: Revenue by Segment
    if 'Monetary' in df.columns:
        rv = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
        
        fig2 = go.Figure(go.Bar(
            x=rv.values, 
            y=rv.index, 
            orientation='h',
            marker=dict(
                color=rv.values,
                colorscale='Viridis',
                line=dict(color='#0f172a', width=1)
            ),
            text=[f'£{v/1000:.1f}K' for v in rv.values],
            textposition='outside',
            textfont=dict(color='white')
        ))
        fig2.update_layout(
            title=dict(
                text="💰 Revenue by Segment",
                font=dict(color='white', size=16),
                x=0.5
            ),
            xaxis=dict(
                title=dict(text="Revenue (£)", font=dict(color='white')),
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                tickfont=dict(color='white')
            ),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    else:
        fig2 = go.Figure()
        fig2.update_layout(
            title=dict(text="💰 Revenue by Segment", font=dict(color='white', size=16)),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(
                text='No revenue data',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(color='white', size=14)
            )]
        )
    
    # Chart 3: 3D RFM Analysis dengan tema gelap
    if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary']):
        fig3 = go.Figure(go.Scatter3d(
            x=df['Recency'], 
            y=df['Frequency'], 
            z=df['Monetary'],
            mode='markers',
            marker=dict(
                size=6,
                color=df['Cluster_KMeans'],
                colorscale='Rainbow',
                opacity=0.8,
                line=dict(width=0)
            ),
            text=df['Cluster_Label'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Recency: %{x}d<br>' +
                         'Frequency: %{y}<br>' +
                         'Monetary: £%{z:.0f}<br>' +
                         '<extra></extra>'
        ))
        fig3.update_layout(
            title=dict(
                text="📈 3D RFM Analysis",
                font=dict(color='white', size=16),
                x=0.5
            ),
            height=600,
            scene=dict(
                xaxis=dict(
                    title='Recency (days)',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)'
                ),
                yaxis=dict(
                    title='Frequency',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)'
                ),
                zaxis=dict(
                    title='Monetary (£)',
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='rgba(0,0,0,0)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
    else:
        fig3 = go.Figure()
        fig3.update_layout(
            title=dict(text="📈 3D RFM Analysis", font=dict(color='white', size=16)),
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
    # Chart 4-6: Histograms dengan tema gelap
    def create_histogram(df, column, title, color):
        if column not in df.columns:
            fig = go.Figure()
            fig.update_layout(
                title=dict(text=title, font=dict(color='white', size=14)),
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            return fig
        
        fig = go.Figure(go.Histogram(
            x=df[column],
            nbinsx=30,
            marker_color=color,
            opacity=0.8,
            marker_line_color='#0f172a',
            marker_line_width=1
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(color='white', size=14)),
            height=300,
            bargap=0.1,
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='white')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    fig4 = create_histogram(df, 'Recency', '⏰ Recency Distribution', '#FF6B6B')
    fig5 = create_histogram(df, 'Frequency', '🔄 Frequency Distribution', '#4ECDC4')
    fig6 = create_histogram(df, 'Monetary', '💵 Monetary Distribution', '#45B7D1')
    
    # Chart 7: RFM Table - versi yang diperbaiki
    try:
        segment_counts = df.groupby('Cluster_Label').size().reset_index(name='Count')
        
        if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'RFM_Score']):
            rfm_stats = df.groupby('Cluster_Label').agg({
                'Recency': 'mean',
                'Frequency': 'mean', 
                'Monetary': 'mean',
                'AvgOrderValue': 'mean',
                'RFM_Score': 'mean'
            }).round(1).reset_index()
            
            segment_table = pd.merge(segment_counts, rfm_stats, on='Cluster_Label')
            
            segment_table['Recency'] = segment_table['Recency'].apply(lambda x: f"{x:.0f}d")
            segment_table['Frequency'] = segment_table['Frequency'].apply(lambda x: f"{x:.1f}")
            segment_table['Monetary'] = segment_table['Monetary'].apply(lambda x: f"£{x:,.0f}")
            segment_table['AvgOrderValue'] = segment_table['AvgOrderValue'].apply(lambda x: f"£{x:.0f}")
            segment_table['RFM_Score'] = segment_table['RFM_Score'].apply(lambda x: f"{x:.1f}")
            
            segment_table = segment_table[['Cluster_Label', 'Count', 'Recency', 'Frequency', 
                                         'Monetary', 'AvgOrderValue', 'RFM_Score']]
            
            fig7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>', '<b>Recency</b>', '<b>Frequency</b>',
                            '<b>Monetary</b>', '<b>Avg Order</b>', '<b>RFM Score</b>'],
                    fill_color='#1e293b',
                    align='center',
                    font=dict(color='white', size=12),
                    height=40,
                    line=dict(color='#334155')
                ),
                cells=dict(
                    values=[
                        segment_table['Cluster_Label'],
                        segment_table['Count'],
                        segment_table['Recency'],
                        segment_table['Frequency'],
                        segment_table['Monetary'],
                        segment_table['AvgOrderValue'],
                        segment_table['RFM_Score']
                    ],
                    fill_color=['rgba(30, 41, 59, 0.6)', 'rgba(30, 41, 59, 0.4)'],
                    align='center',
                    font=dict(size=11, color='white'),
                    height=35,
                    line=dict(color='#334155')
                )
            )])
        else:
            segment_table = segment_counts.copy()
            segment_table = segment_table.rename(columns={'Cluster_Label': 'Segment'})
            
            fig7 = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Segment</b>', '<b>Count</b>'],
                    fill_color='#1e293b',
                    align='center',
                    font=dict(color='white', size=12),
                    height=40,
                    line=dict(color='#334155')
                ),
                cells=dict(
                    values=[segment_table['Segment'], segment_table['Count']],
                    fill_color=['rgba(30, 41, 59, 0.6)', 'rgba(30, 41, 59, 0.4)'],
                    align='center',
                    font=dict(size=11, color='white'),
                    height=35,
                    line=dict(color='#334155')
                )
            )])
        
        fig7.update_layout(
            title=dict(
                text="📊 Segment Summary",
                font=dict(color='white', size=16),
                x=0.5
            ),
            height=400,
            margin=dict(t=50, b=20, l=20, r=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
    except Exception as e:
        fig7 = go.Figure()
        fig7.update_layout(
            title=dict(text="📊 Segment Summary", font=dict(color='white', size=16)),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(
                text=f'Error: {str(e)[:100]}',
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color='white')
            )]
        )
    
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    
    st.markdown("#### 📊 Data Settings")
    refresh_data = st.button("🔄 Refresh Data", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 🎨 Theme Settings")
    theme = st.selectbox(
        "Color Theme",
        ["Dark Professional", "Light Professional", "Blue Gradient"],
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("#### 📈 Chart Settings")
    chart_animation = st.toggle("Enable Chart Animations", value=True)
    chart_interactivity = st.toggle("Enhanced Interactivity", value=True)
    
    st.markdown("---")
    
    st.markdown("#### 📱 Display Settings")
    st.slider("Chart Quality", 1, 3, 2)
    
    st.markdown("---")
    
    st.markdown("### 📖 Help & Support")
    with st.expander("ℹ️ How to use this dashboard"):
        st.markdown("""
        1. **Filter** data using the filters above
        2. **Explore** segments in the Analytics tab
        3. **View** strategies in the Growth Strategies tab
        4. **Get insights** in the AI Insights tab
        """)

# Layout utama Streamlit
def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="main-header">
            <div>
                <h1 class="header-title">Customer Intelligence Hub</h1>
                <div class="header-subtitle">AI-Powered Customer Segmentation for Targeted Marketing</div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-value">{:,}</div>
                    <div class="stat-label">Customers</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{}</div>
                    <div class="stat-label">Segments</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">£{:.1f}M</div>
                    <div class="stat-label">Revenue</div>
                </div>
            </div>
        </div>
    </div>
    """.format(
        len(rfm),
        rfm['Cluster_KMeans'].nunique(),
        rfm['Monetary'].sum()/1e6 if 'Monetary' in rfm.columns else 0
    ), unsafe_allow_html=True)
    
    # Metrics Grid
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(rfm)
        segment_count = rfm['Cluster_KMeans'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{total_customers:,}</div>
            <div class="metric-label">Total Customers</div>
            <div class="metric-change change-positive">
                <span>↑ 12.5%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_rev = rfm['Monetary'].sum() if 'Monetary' in rfm.columns else 0
        avg_rev = rfm['Monetary'].mean() if 'Monetary' in rfm.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">£{total_rev/1e6:.1f}M</div>
            <div class="metric-label">Total Revenue</div>
            <div class="metric-change change-positive">
                <span>↑ 8.2%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_order = rfm['AvgOrderValue'].mean() if 'AvgOrderValue' in rfm.columns else 0
        max_order = rfm['AvgOrderValue'].max() if 'AvgOrderValue' in rfm.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-value">£{avg_order:.0f}</div>
            <div class="metric-label">Avg Order Value</div>
            <div class="metric-change change-positive">
                <span>↑ 5.7%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        champion_count = len(rfm[rfm['Cluster_Label'].str.contains('Champions')]) if 'Cluster_Label' in rfm.columns else 0
        champion_pct = (champion_count / len(rfm) * 100) if len(rfm) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏆</div>
            <div class="metric-value">{champion_pct:.1f}%</div>
            <div class="metric-label">Champion Ratio</div>
            <div class="metric-change change-positive">
                <span>↑ 3.4%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filters
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-title">🎛️ Smart Filters</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Segment Filter
        segment_options = [{'label': '🌐 All Segments', 'value': 'all'}]
        for c, p in profs.items():
            if p['name'] == '🏆 Champions' and c in champion_details:
                label = f"{p['name']} - {champion_details[c]['tier']}"
            else:
                label = p['name']
            segment_options.append({'label': label, 'value': c})
        
        segment_filter = st.selectbox(
            "🎨 Segment Filter",
            options=[opt['value'] for opt in segment_options],
            format_func=lambda x: next((opt['label'] for opt in segment_options if opt['value'] == x), x),
            index=0,
            key="segment_filter"
        )
    
    with col2:
        # RFM Score Range
        if 'RFM_Score' in rfm.columns:
            rfm_min = int(rfm['RFM_Score'].min())
            rfm_max = int(rfm['RFM_Score'].max())
            rfm_filter = st.slider(
                "📊 RFM Score Range",
                min_value=rfm_min,
                max_value=rfm_max,
                value=[rfm_min, rfm_max],
                key="rfm_filter"
            )
        else:
            rfm_filter = [0, 100]
            st.slider(
                "📊 RFM Score Range",
                min_value=0,
                max_value=100,
                value=[0, 100],
                key="rfm_filter"
            )
    
    with col3:
        # Priority Level
        priority_options = [
            {'label': '🌐 All Priorities', 'value': 'all'},
            {'label': '🔴 CRITICAL', 'value': 'CRITICAL'},
            {'label': '🔥 URGENT', 'value': 'URGENT'},
            {'label': '⚡ HIGH', 'value': 'HIGH'},
            {'label': '📊 MEDIUM', 'value': 'MEDIUM'}
        ]
        priority_filter = st.selectbox(
            "🔥 Priority Level",
            options=[opt['value'] for opt in priority_options],
            format_func=lambda x: next((opt['label'] for opt in priority_options if opt['value'] == x), x),
            index=0,
            key="priority_filter"
        )
    
    # Additional Filters in expander
    with st.expander("🔍 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'Monetary' in rfm.columns:
                monetary_min = float(rfm['Monetary'].min())
                monetary_max = float(rfm['Monetary'].max())
                monetary_filter = st.slider(
                    "💰 Monetary Value Range",
                    min_value=monetary_min,
                    max_value=monetary_max,
                    value=[monetary_min, monetary_max],
                    key="monetary_filter"
                )
        
        with col2:
            if 'Frequency' in rfm.columns:
                freq_min = int(rfm['Frequency'].min())
                freq_max = int(rfm['Frequency'].max())
                frequency_filter = st.slider(
                    "🔄 Frequency Range",
                    min_value=freq_min,
                    max_value=freq_max,
                    value=[freq_min, freq_max],
                    key="frequency_filter"
                )
        
        with col3:
            if 'Recency' in rfm.columns:
                recency_min = int(rfm['Recency'].min())
                recency_max = int(rfm['Recency'].max())
                recency_filter = st.slider(
                    "⏰ Recency Range (days)",
                    min_value=recency_min,
                    max_value=recency_max,
                    value=[recency_min, recency_max],
                    key="recency_filter"
                )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = rfm.copy()
    
    if 'RFM_Score' in rfm.columns:
        filtered_df = filtered_df[
            (filtered_df['RFM_Score'] >= rfm_filter[0]) & 
            (filtered_df['RFM_Score'] <= rfm_filter[1])
        ]
    
    if segment_filter != 'all':
        filtered_df = filtered_df[filtered_df['Cluster_KMeans'] == segment_filter]
    
    if priority_filter != 'all' and 'Priority' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]
    
    # Apply advanced filters if they exist
    if 'monetary_filter' in locals() and 'Monetary' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Monetary'] >= monetary_filter[0]) & 
            (filtered_df['Monetary'] <= monetary_filter[1])
        ]
    
    if 'frequency_filter' in locals() and 'Frequency' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Frequency'] >= frequency_filter[0]) & 
            (filtered_df['Frequency'] <= frequency_filter[1])
        ]
    
    if 'recency_filter' in locals() and 'Recency' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Recency'] >= recency_filter[0]) & 
            (filtered_df['Recency'] <= recency_filter[1])
        ]
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Growth Strategies", "💡 AI Insights"])
    
    with tab1:
        if len(filtered_df) > 0:
            # Generate charts
            fig1, fig2, fig3, fig4, fig5, fig6, fig7 = create_charts(filtered_df)
            
            # Row 1: Two charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': True})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': True})
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 2: Full width 3D chart
            st.markdown('<div class="chart-container chart-full">', unsafe_allow_html=True)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': True})
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 3: Three histograms
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Row 4: Full width table
            st.markdown('<div class="chart-container chart-full">', unsafe_allow_html=True)
            st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Data summary
            with st.expander("📋 Data Summary"):
                st.dataframe(
                    filtered_df.describe(),
                    use_container_width=True
                )
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>No Data Available</h3>
                <p>Try adjusting your filters to see data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # Champion Breakdown Section
        champion_clusters = [c for c in filtered_df['Cluster_KMeans'].unique() 
                            if c in profs and profs[c]['name'] == '🏆 Champions']
        
        if len(champion_clusters) > 0:
            st.markdown('<div class="champion-section">', unsafe_allow_html=True)
            st.markdown('<div class="champion-title">🏆 Champion Segments Breakdown</div>', unsafe_allow_html=True)
            
            cols = st.columns(2)
            for idx, cid in enumerate(sorted(champion_clusters)):
                if cid in champion_details:
                    det = champion_details[cid]
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div class="champion-card">
                            <div class="champion-number">Champion C{cid}</div>
                            <div class="champion-tier">🏅 {det['tier']}</div>
                            <div class="champion-desc">{det['desc']}</div>
                            <div class="champion-chars">📊 {det['char']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Strategy Cards
        strategy_cards_html = ""
        for cid, p in profs.items():
            if segment_filter == 'all' or segment_filter == cid:
                # Build tactics HTML
                tactics_html = ""
                for tactic in p['tactics']:
                    tactics_html += f'<div class="tactic-item">{tactic}</div>'
                
                # Build KPIs HTML
                kpis_html = ""
                for kpi in p['kpis']:
                    kpis_html += f'<div class="kpi-item">{kpi}</div>'
                
                strategy_cards_html += f"""
                <div class="strategy-card" style="background: {p['grad']}">
                    <div class="strategy-header">
                        <div>
                            <h3 class="strategy-name">{p['name']}</h3>
                            <div class="strategy-subtitle">{p['strategy']} Strategy</div>
                        </div>
                        <div class="priority-badge">{p['priority']}</div>
                    </div>
                    
                    <div class="tactics-section">
                        <div class="tactics-title">🎯 Key Tactics</div>
                        <div class="tactics-grid">
                            {tactics_html}
                        </div>
                    </div>
                    
                    <div class="tactics-section">
                        <div class="tactics-title">📊 Target KPIs</div>
                        <div class="kpis-grid">
                            {kpis_html}
                        </div>
                    </div>
                    
                    <div class="strategy-footer">
                        <div class="budget-item">
                            <div class="budget-label">Budget Allocation</div>
                            <div class="budget-value">{p['budget']}</div>
                        </div>
                        <div class="budget-item">
                            <div class="budget-label">Expected ROI</div>
                            <div class="budget-value">{p['roi']}</div>
                        </div>
                    </div>
                </div>
                """
        
        if strategy_cards_html:
            st.markdown(f'<div class="strategy-grid">{strategy_cards_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🎯</div>
                <h3>No Strategy Cards Available</h3>
                <p>Try selecting a different segment filter</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        if len(filtered_df) > 0:
            # Calculate insights
            if 'Cluster_Label' in filtered_df.columns:
                if 'Monetary' in filtered_df.columns:
                    highest_revenue = filtered_df.groupby('Cluster_Label')['Monetary'].sum()
                    highest_revenue_segment = highest_revenue.idxmax() if not highest_revenue.empty else "N/A"
                    highest_revenue_value = highest_revenue.max() if not highest_revenue.empty else 0
                else:
                    highest_revenue_segment = "N/A"
                    highest_revenue_value = 0
                
                largest_group = filtered_df['Cluster_Label'].value_counts()
                largest_group_segment = largest_group.idxmax() if not largest_group.empty else "N/A"
                largest_group_count = largest_group.max() if not largest_group.empty else 0
                
                if 'AvgOrderValue' in filtered_df.columns:
                    best_aov = filtered_df.groupby('Cluster_Label')['AvgOrderValue'].mean()
                    best_aov_segment = best_aov.idxmax() if not best_aov.empty else "N/A"
                    best_aov_value = best_aov.max() if not best_aov.empty else 0
                else:
                    best_aov_segment = "N/A"
                    best_aov_value = 0
                
                if 'Frequency' in filtered_df.columns:
                    most_frequent = filtered_df.groupby('Cluster_Label')['Frequency'].mean()
                    most_frequent_segment = most_frequent.idxmax() if not most_frequent.empty else "N/A"
                    most_frequent_value = most_frequent.max() if not most_frequent.empty else 0
                else:
                    most_frequent_segment = "N/A"
                    most_frequent_value = 0
            else:
                highest_revenue_segment = "N/A"
                highest_revenue_value = 0
                largest_group_segment = "N/A"
                largest_group_count = 0
                best_aov_segment = "N/A"
                best_aov_value = 0
                most_frequent_segment = "N/A"
                most_frequent_value = 0
            
            st.markdown('<div class="insights-section">', unsafe_allow_html=True)
            st.markdown('<div class="insights-title">🧠 AI-Powered Insights & Recommendations</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="insight-card">
                    <h4 class="insight-heading">📊 Performance Analysis</h4>
                    <ul class="insight-list">
                """, unsafe_allow_html=True)
                
                insights_list = [
                    f"🏆 Highest Revenue: {highest_revenue_segment} (£{highest_revenue_value/1000:.1f}K)",
                    f"👥 Largest Group: {largest_group_segment} ({largest_group_count:,} customers)",
                    f"💰 Best AOV: {best_aov_segment} (£{best_aov_value:.0f})",
                    f"🔄 Most Frequent: {most_frequent_segment} ({most_frequent_value:.1f} orders)"
                ]
                
                for insight in insights_list:
                    st.markdown(f"<li>{insight}</li>", unsafe_allow_html=True)
                
                st.markdown("""
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="insight-card">
                    <h4 class="insight-heading">💡 Strategic Recommendations</h4>
                    <ul class="insight-list">
                        <li>🎯 Launch retention programs for high-value segments</li>
                        <li>📧 Implement personalized win-back campaigns</li>
                        <li>🚀 Accelerate nurturing flows for potential customers</li>
                        <li>💎 Create VIP experiences for champion segments</li>
                        <li>📈 Develop cross-sell strategies for loyal customers</li>
                        <li>🔍 Monitor dormant segment reactivation rates</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional insights
            with st.expander("📈 Advanced Analytics"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "📊 Segment Concentration",
                        f"{(largest_group_count / len(filtered_df) * 100):.1f}%",
                        "+2.3%"
                    )
                    
                    if 'Monetary' in filtered_df.columns:
                        top_20_percent = filtered_df.nlargest(int(len(filtered_df) * 0.2), 'Monetary')
                        bottom_80_percent = filtered_df.nsmallest(int(len(filtered_df) * 0.8), 'Monetary')
                        
                        top_20_revenue = top_20_percent['Monetary'].sum()
                        total_revenue = filtered_df['Monetary'].sum()
                        
                        if total_revenue > 0:
                            revenue_concentration = (top_20_revenue / total_revenue) * 100
                            st.metric(
                                "💰 Revenue Concentration (Top 20%)",
                                f"{revenue_concentration:.1f}%",
                                "+1.5%"
                            )
                
                with col2:
                    if 'Recency' in filtered_df.columns:
                        avg_recency = filtered_df['Recency'].mean()
                        st.metric(
                            "⏰ Average Recency",
                            f"{avg_recency:.1f} days",
                            "-3.2 days"
                        )
                    
                    if 'Frequency' in filtered_df.columns:
                        avg_frequency = filtered_df['Frequency'].mean()
                        st.metric(
                            "🔄 Average Frequency",
                            f"{avg_frequency:.1f}",
                            "+0.8"
                        )
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">💡</div>
                <h3>No Insights Available</h3>
                <p>Try adjusting your filters to see insights</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        Customer Intelligence Hub v2.1 • Powered by AI Segmentation • Data Updated Daily • 
        <a href="#" style="color: #667eea; text-decoration: none;">Export Report</a> • 
        <a href="#" style="color: #667eea; text-decoration: none;">Schedule Delivery</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
