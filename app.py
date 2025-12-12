import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Customer Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Poppins',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%)}
.stApp{background:rgba(255,255,255,0.98);border-radius:32px;padding:40px;box-shadow:0 40px 100px rgba(0,0,0,0.4);animation:fadeIn .8s ease-out}
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

/* TABS */
.tab-content{padding:28px 0}

/* CHARTS */
.chart{background:#fff;border-radius:24px;padding:32px;box-shadow:0 10px 35px rgba(0,0,0,.08);transition:all .35s ease;border:3px solid transparent;margin-bottom:26px}
.chart:hover{transform:translateY(-6px);box-shadow:0 20px 50px rgba(0,0,0,.15);border-color:#667eea}

/* STRATEGY CARDS */
.strat-g{display:grid;grid-template-columns:repeat(2,1fr);gap:26px;margin-bottom:26px}
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

/* RESPONSIVE */
@media(max-width:1200px){
    .metrics,.strat-g,.ins-g{grid-template-columns:repeat(2,1fr)}
    .chart-full{grid-column:1/-1}
}
@media(max-width:768px){
    .metrics,.strat-g,.ins-g{grid-template-columns:1fr}
    .title{font-size:2.8rem}
}
</style>
""", unsafe_allow_html=True)

# Load & Prepare Data
@st.cache_data
def load_data():
    try:
        rfm = pd.read_csv('final_customer_segments (1).csv', index_col=0)
    except:
        rfm = pd.read_csv('final_customer_segments.csv', index_col=0)
    return rfm

rfm = load_data()

# Cluster Strategies
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
    cd = data[data['Cluster_KMeans'] == cid]
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

profs = {}
for c in rfm['Cluster_KMeans'].unique():
    p = get_strat(c, rfm)
    profs[c] = p
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Cluster_Label'] = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
    rfm.loc[rfm['Cluster_KMeans'] == c, 'Priority'] = p['priority']

colors = {f"{p['name'][:2]} {p['name'][2:]} (C{c})": p['color'] for c, p in profs.items()}

# Header
st.markdown("""
<div class="hdr">
    <h1 class="title">🎯 Customer Intelligence Hub</h1>
    <p class="sub">Customer Segmentation for Personalized Retail Marketing</p>
</div>
""", unsafe_allow_html=True)

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="met">
        <div class="met-icon">👥</div>
        <div class="met-val">{len(rfm):,}</div>
        <div class="met-lbl">Customers</div>
        <div class="met-sub">Active Database</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="met">
        <div class="met-icon">🎯</div>
        <div class="met-val">{rfm['Cluster_KMeans'].nunique()}</div>
        <div class="met-lbl">Segments</div>
        <div class="met-sub">AI-Classified</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="met">
        <div class="met-icon">💰</div>
        <div class="met-val">£{rfm['Monetary'].sum()/1e6:.2f}M</div>
        <div class="met-lbl">Revenue</div>
        <div class="met-sub">Avg £{rfm['Monetary'].mean():.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="met">
        <div class="met-icon">📈</div>
        <div class="met-val">£{rfm['AvgOrderValue'].mean():.0f}</div>
        <div class="met-lbl">Avg Order</div>
        <div class="met-sub">Peak £{rfm['AvgOrderValue'].max():.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# Filters
st.markdown('<div class="filt">', unsafe_allow_html=True)
st.markdown('<div class="filt-t">🎛️ Smart Filters</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # Buat opsi untuk segment filter
    cluster_options = ['all'] + list(profs.keys())
    
    # Buat mapping untuk display names
    def get_cluster_display_name(cluster_id):
        if cluster_id == 'all':
            return '🌐 All Segments'
        else:
            p = profs[cluster_id]
            if p['name'] == '🏆 Champions' and cluster_id in champion_details:
                return f"{p['name']} - {champion_details[cluster_id]['tier']}"
            else:
                return p['name']
    
    selected_cluster = st.selectbox(
        "🎨 Segment Filter",
        options=cluster_options,
        format_func=get_cluster_display_name
    )

with col2:
    min_rfm = int(rfm['RFM_Score'].min())
    max_rfm = int(rfm['RFM_Score'].max())
    rfm_range = st.slider(
        "📊 RFM Score Range",
        min_value=min_rfm,
        max_value=max_rfm,
        value=(min_rfm, max_rfm),
        step=1
    )

with col3:
    # Priority options
    priority_options = {
        'all': '🌐 All Priorities',
        'CRITICAL': '🔴 CRITICAL',
        'URGENT': '🔥 URGENT',
        'HIGH': '⚡ HIGH',
        'MEDIUM': '📊 MEDIUM'
    }
    
    selected_priority = st.selectbox(
        "🔥 Priority Level",
        options=list(priority_options.keys()),
        format_func=lambda x: priority_options[x]
    )

st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
filtered_df = rfm[(rfm['RFM_Score'] >= rfm_range[0]) & (rfm['RFM_Score'] <= rfm_range[1])]
if selected_cluster != 'all':
    filtered_df = filtered_df[filtered_df['Cluster_KMeans'] == selected_cluster]
if selected_priority != 'all':
    filtered_df = filtered_df[filtered_df['Priority'] == selected_priority]

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🎯 Growth Strategies", "💡 AI Insights"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Chart 1: Customer Distribution Pie
    cluster_counts = filtered_df['Cluster_Label'].value_counts()
    fig1 = go.Figure(go.Pie(
        labels=cluster_counts.index,
        values=cluster_counts.values,
        hole=.68,
        marker=dict(colors=[colors.get(l, '#95A5A6') for l in cluster_counts.index],
                   line=dict(color='white', width=5)),
        textfont=dict(size=14, family='Inter, Poppins', weight=700),
        textposition='outside',
        pull=[0.05] * len(cluster_counts)
    ))
    fig1.update_layout(
        title={'text': "<b>🎯 Customer Distribution</b>", 'x': .5, 
               'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
        height=420,
        annotations=[dict(text=f'<b>{len(filtered_df):,}</b><br><span style="font-size:14px">Customers</span>',
                         x=.5, y=.5, font={'size': 24, 'color': '#667eea', 'family': 'Inter, Poppins'}, 
                         showarrow=False)],
        margin=dict(t=80, b=40, l=40, r=40)
    )
    
    # Chart 2: Revenue by Segment
    revenue_by_segment = filtered_df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
    fig2 = go.Figure(go.Bar(
        x=revenue_by_segment.values,
        y=revenue_by_segment.index,
        orientation='h',
        marker=dict(color=revenue_by_segment.values, colorscale='Sunset',
                   line=dict(color='white', width=3)),
        text=[f'£{v/1000:.1f}K' for v in revenue_by_segment.values],
        textposition='outside',
        textfont={'size': 13, 'weight': 700, 'family': 'Inter, Poppins'}
    ))
    fig2.update_layout(
        title={'text': "<b>💰 Revenue by Segment</b>", 'x': .5, 
               'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
        xaxis={'title': '<b>Revenue (£)</b>', 'titlefont': {'size': 14, 'family': 'Inter, Poppins'}, 
               'gridcolor': 'rgba(0,0,0,0.05)'},
        yaxis={'titlefont': {'size': 14, 'family': 'Inter, Poppins'}},
        height=420,
        plot_bgcolor='rgba(245,247,250,.6)',
        margin=dict(t=80, b=60, l=140, r=60)
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    with col2:
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    
    # Chart 3: 3D RFM Analysis
    fig3 = go.Figure(go.Scatter3d(
        x=filtered_df['Recency'],
        y=filtered_df['Frequency'],
        z=filtered_df['Monetary'],
        mode='markers',
        marker=dict(size=7, color=filtered_df['Cluster_KMeans'], colorscale='Rainbow', 
                   showscale=True, line=dict(width=.8, color='white'), opacity=.88,
                   colorbar=dict(title='Cluster', thickness=20, len=0.7)),
        text=filtered_df['Cluster_Label'],
        hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}<extra></extra>'
    ))
    fig3.update_layout(
        title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x': .5, 
               'font': {'size': 20, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
        height=650,
        scene=dict(
            xaxis=dict(title='<b>Recency (days)</b>', backgroundcolor='rgba(245,247,250,.4)', 
                      gridcolor='rgba(0,0,0,0.08)'),
            yaxis=dict(title='<b>Frequency</b>', backgroundcolor='rgba(245,247,250,.4)', 
                      gridcolor='rgba(0,0,0,0.08)'),
            zaxis=dict(title='<b>Monetary (£)</b>', backgroundcolor='rgba(245,247,250,.4)', 
                      gridcolor='rgba(0,0,0,0.08)'),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        paper_bgcolor='rgba(245,247,250,.4)',
        margin=dict(t=80, b=40, l=40, r=40)
    )
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    
    # Histograms
    def create_histogram(data, column, title, color):
        fig = go.Figure(go.Histogram(
            x=data[column], nbinsx=35,
            marker=dict(color=color, line=dict(color='white', width=2), opacity=.85)
        ))
        fig.update_layout(
            title={'text': f"<b>{title}</b>", 'x': .5, 
                   'font': {'size': 18, 'family': 'Inter, Poppins', 'color': '#2c3e50'}},
            xaxis={'title': f'<b>{column}</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 
                   'gridcolor': 'rgba(0,0,0,0.05)'},
            yaxis={'title': '<b>Count</b>', 'titlefont': {'size': 13, 'family': 'Inter, Poppins'}, 
                   'gridcolor': 'rgba(0,0,0,0.05)'},
            height=340,
            plot_bgcolor='rgba(245,247,250,.5)',
            margin=dict(t=70, b=50, l=60, r=40)
        )
        return fig
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fig4 = create_histogram(filtered_df, 'Recency', '⏰ Recency Distribution', '#ff6b6b')
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    with col2:
        fig5 = create_histogram(filtered_df, 'Frequency', '🔄 Frequency Distribution', '#4ecdc4')
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    with col3:
        fig6 = create_histogram(filtered_df, 'Monetary', '💵 Monetary Distribution', '#45b7d1')
        st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
    
    # Segment Summary Table
    summary_table = filtered_df.groupby('Cluster_Label').agg({
        'Recency': 'mean', 'Frequency': 'mean', 'Monetary': 'mean', 
        'AvgOrderValue': 'mean', 'RFM_Score': 'mean'
    }).round(1).reset_index()
    summary_table['Count'] = filtered_df.groupby('Cluster_Label').size().values
    
    fig7 = go.Figure(go.Table(
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
                summary_table['Cluster_Label'],
                summary_table['Count'],
                [f"{v:.0f}d" for v in summary_table['Recency']],
                summary_table['Frequency'].round(1),
                [f"£{v:,.0f}" for v in summary_table['Monetary']],
                [f"£{v:.0f}" for v in summary_table['AvgOrderValue']],
                summary_table['RFM_Score']
            ],
            fill_color=[['white', '#f8f9fc'] * len(summary_table)],
            align='center',
            font={'size': 12, 'family': 'Inter, Poppins'},
            height=38,
            line=dict(color='#e0e0e0', width=1)
        )
    ))
    fig7.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Champion Breakdown Section
    champion_clusters = [c for c in filtered_df['Cluster_KMeans'].unique() 
                        if profs[c]['name'] == '🏆 Champions']
    
    if len(champion_clusters) > 0:
        champ_cards = []
        for cid in sorted(champion_clusters):
            if cid in champion_details:
                det = champion_details[cid]
                champ_cards.append(f"""
                <div class="champ-card">
                    <div class="champ-num">Champion C{cid}</div>
                    <div class="champ-tier">🏅 {det['tier']}</div>
                    <div class="champ-desc">{det['desc']}</div>
                    <div class="champ-char">📊 Characteristics: {det['char']}</div>
                </div>
                """)
        
        if champ_cards:
            st.markdown("""
            <div class="champ-break">
                <div class="champ-break-t">🏆 Champion Segments Breakdown</div>
                <div style="text-align:center;font-size:1.1rem;margin-bottom:24px;opacity:0.95">
                    Understanding the 4 Different Champion Tiers
                </div>
                <div class="champ-grid">
            """ + "".join(champ_cards) + """
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Strategy Cards
    strategy_cards = []
    for cid, p in profs.items():
        if selected_cluster == 'all' or selected_cluster == cid:
            strategy_cards.append(f"""
            <div class="strat" style="background:{p['grad']}">
                <div class="strat-hdr">
                    <div class="strat-name">{p['name']}</div>
                    <div class="pri-badge">{p['priority']}</div>
                </div>
                <div class="strat-sub">📋 {p['strategy']} Strategy</div>
                <div class="tactics">
                    <div class="tact-t">🎯 Key Tactics</div>
                    {"".join([f'<div class="tact">{t}</div>' for t in p['tactics']])}
                </div>
                <div class="tactics">
                    <div class="tact-t">📊 Target KPIs</div>
                    <div class="kpi-g">
                        {"".join([f'<div class="kpi">{k}</div>' for k in p['kpis']])}
                    </div>
                </div>
                <div class="budget">
                    <div>
                        <div class="budget-l">Budget Allocation</div>
                        <div class="budget-v">{p['budget']}</div>
                    </div>
                    <div>
                        <div class="budget-l">ROI Target</div>
                        <div class="budget-v">{p['roi']}</div>
                    </div>
                </div>
            </div>
            """)
    
    st.markdown(f'<div class="strat-g">{"".join(strategy_cards)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Insights
    insights_content = f"""
    <div class="ins">
        <div class="ins-t">🧠 AI-Powered Insights & Recommendations</div>
        <div class="ins-g">
            <div class="ins-card">
                <div class="ins-h">📊 Top Performers</div>
                <ul class="ins-list">
                    <li>🏆 Highest Revenue: {filtered_df.groupby('Cluster_Label')['Monetary'].sum().idxmax() if len(filtered_df) > 0 else 'N/A'}</li>
                    <li>👥 Largest Group: {filtered_df['Cluster_Label'].value_counts().idxmax() if len(filtered_df) > 0 else 'N/A'} ({filtered_df['Cluster_Label'].value_counts().max() if len(filtered_df) > 0 else 0:,} customers)</li>
                    <li>💰 Best AOV: {filtered_df.groupby('Cluster_Label')['AvgOrderValue'].mean().idxmax() if len(filtered_df) > 0 else 'N/A'} (£{filtered_df.groupby('Cluster_Label')['AvgOrderValue'].mean().max() if len(filtered_df) > 0 else 0:.0f})</li>
                    <li>🔄 Most Frequent: {filtered_df.groupby('Cluster_Label')['Frequency'].mean().idxmax() if len(filtered_df) > 0 else 'N/A'} ({filtered_df.groupby('Cluster_Label')['Frequency'].mean().max() if len(filtered_df) > 0 else 0:.1f} orders)</li>
                </ul>
            </div>
            <div class="ins-card">
                <div class="ins-h">💡 Smart Recommendations</div>
                <ul class="ins-list">
                    <li>🎯 Prioritize high-value segment retention programs</li>
                    <li>📧 Launch win-back campaigns for dormant customers</li>
                    <li>🚀 Accelerate potential customer nurturing flows</li>
                    <li>💎 Create exclusive VIP experiences for champions</li>
                    <li>📈 Implement cross-sell strategies for loyal segments</li>
                </ul>
            </div>
        </div>
    </div>
    """
    st.markdown(insights_content, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;margin-top:50px;padding:26px;border-top:4px solid #667eea;color:#7f8c8d;font-size:1.05rem;font-weight:600;letter-spacing:0.5px">
    Customer Intelligence Hub v1.0 • Powered by Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
