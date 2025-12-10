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

# Print debug info untuk Railway
print("=" * 80)
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")
print("=" * 80)

# Inisialisasi Flask server untuk Railway
server = Flask(__name__)

# Load & Prepare Data dengan error handling yang lebih baik
def load_data():
    try:
        # Coba beberapa kemungkinan nama file
        possible_files = [
            'final_customer_segments (1).csv',
            'final_customer_segments.csv',
            './final_customer_segments.csv',
            '/app/final_customer_segments.csv'
        ]
        
        rfm = None
        used_file = None
        
        for file_path in possible_files:
            if os.path.exists(file_path):
                print(f"📂 Found file: {file_path}, size: {os.path.getsize(file_path)} bytes")
                rfm = pd.read_csv(file_path, index_col=0)
                used_file = file_path
                break
        
        if rfm is None:
            print("⚠️  No CSV file found, creating dummy data for testing")
            # Buat data dummy yang lebih realistis untuk dashboard
            np.random.seed(42)
            n_customers = 1000
            
            data = {
                'Recency': np.random.randint(1, 365, n_customers),
                'Frequency': np.random.randint(1, 50, n_customers),
                'Monetary': np.random.randint(100, 10000, n_customers),
                'AvgOrderValue': np.random.randint(50, 500, n_customers),
                'RFM_Score': np.random.randint(1, 10, n_customers),
                'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], n_customers)
            }
            
            # Buat beberapa cluster dengan karakteristik berbeda
            data['Monetary'] = np.where(data['Cluster_KMeans'] == 3, 
                                       np.random.randint(5000, 50000, n_customers), 
                                       data['Monetary'])
            data['Frequency'] = np.where(data['Cluster_KMeans'] == 6, 
                                        np.random.randint(20, 200, n_customers), 
                                        data['Frequency'])
            
            rfm = pd.DataFrame(data)
            print(f"✅ Created dummy data with {len(rfm)} customers")
        else:
            print(f"✅ Loaded {len(rfm):,} customers from {used_file}")
            print(f"Columns: {rfm.columns.tolist()}")
            print(f"Sample data:\n{rfm.head()}")
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        traceback.print_exc()
        # Fallback ke data dummy
        np.random.seed(42)
        data = {
            'Recency': np.random.randint(1, 365, 1000),
            'Frequency': np.random.randint(1, 50, 1000),
            'Monetary': np.random.randint(100, 10000, 1000),
            'AvgOrderValue': np.random.randint(50, 500, 1000),
            'RFM_Score': np.random.randint(1, 10, 1000),
            'Cluster_KMeans': np.random.choice([0, 1, 2, 3, 4, 5, 6], 1000)
        }
        rfm = pd.DataFrame(data)
        print(f"✅ Fallback to dummy data with {len(rfm)} customers")
    
    return rfm

# Load data
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

def get_strat(cid,data):
    try:
        cd=data[data['Cluster_KMeans']==cid]
        if len(cd) == 0:
            return {**strats['standard'],'cluster_id':cid}
            
        r=cd['Recency'].mean() if 'Recency' in cd.columns else 100
        f=cd['Frequency'].mean() if 'Frequency' in cd.columns else 5
        m=cd['Monetary'].mean() if 'Monetary' in cd.columns else 500
        
        if r<50 and f>10 and m>1000: s='champions'
        elif r<50 and f>5: s='loyal'
        elif m>1500: s='big'
        elif r>100: s='dormant'
        elif r<50 and f<5: s='potential'
        else: s='standard'
        return {**strats[s],'cluster_id':cid}
    except Exception as e:
        print(f"Error in get_strat for cluster {cid}: {e}")
        return {**strats['standard'],'cluster_id':cid}

# Inisialisasi profil cluster
profs={}
for c in rfm['Cluster_KMeans'].unique():
    try:
        p=get_strat(c,rfm)
        profs[c]=p
        
        # Tambahkan kolom baru jika belum ada
        if 'Cluster_Label' not in rfm.columns:
            rfm['Cluster_Label'] = ''
        if 'Priority' not in rfm.columns:
            rfm['Priority'] = ''
            
        rfm.loc[rfm['Cluster_KMeans']==c,'Cluster_Label']=f"{p['name'][:2]} {p['name'][2:]} (C{c})"
        rfm.loc[rfm['Cluster_KMeans']==c,'Priority']=p['priority']
    except Exception as e:
        print(f"Error processing cluster {c}: {e}")

# Buat mapping warna
colors={}
for c,p in profs.items():
    try:
        label = f"{p['name'][:2]} {p['name'][2:]} (C{c})"
        colors[label] = p['color']
    except:
        pass

# Print info untuk debugging
print(f"📊 Loaded {len(rfm)} customers with {len(profs)} clusters")
print(f"Clusters: {list(profs.keys())}")

# Inisialisasi Dash app dengan server Flask
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Layout aplikasi
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("🎯 Customer Intelligence Hub", className="title"),
            html.P("Customer Segmentation for Personalized Retail Marketing", className="sub")
        ], className="hdr"),

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

        html.Div([
            html.Div("🎛️ Smart Filters", className="filt-t"),
            html.Div([
                html.Div([
                    html.Label("🎨 Segment Filter"),
                    dcc.Dropdown(
                        id='cf',
                        options=[{'label':'🌐 All Segments','value':'all'}] +
                                [{'label':f"{p['name']} - {champion_details[c]['tier']}" if p['name']=='🏆 Champions' and c in champion_details else p['name'],
                                  'value':c} for c,p in profs.items()],
                        value='all',
                        clearable=False,
                        style={'borderRadius':'12px'}
                    )
                ]),
                html.Div([
                    html.Label("📊 RFM Score Range"),
                    dcc.RangeSlider(
                        id='rf',
                        min=int(rfm['RFM_Score'].min()),
                        max=int(rfm['RFM_Score'].max()),
                        value=[int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())],
                        marks={i:{'label':str(i),'style':{'fontWeight':'600'}}
                              for i in range(int(rfm['RFM_Score'].min()), int(rfm['RFM_Score'].max())+1, 2)},
                        tooltip={'placement':'bottom','always_visible':False}
                    )
                ]),
                html.Div([
                    html.Label("🔥 Priority Level"),
                    dcc.Dropdown(
                        id='pf',
                        options=[
                            {'label':'🌐 All Priorities','value':'all'},
                            {'label':'🔴 CRITICAL','value':'CRITICAL'},
                            {'label':'🔥 URGENT','value':'URGENT'},
                            {'label':'⚡ HIGH','value':'HIGH'},
                            {'label':'📊 MEDIUM','value':'MEDIUM'}
                        ],
                        value='all',
                        clearable=False,
                        style={'borderRadius':'12px'}
                    )
                ])
            ], className="filt-g")
        ], className="filt"),

        dbc.Tabs([
            dbc.Tab(label="📊 Analytics Dashboard", children=[
                html.Div([
                    html.Div([
                        html.Div([dcc.Graph(id='g1', config={'displayModeBar':False})], className="chart"),
                        html.Div([dcc.Graph(id='g2', config={'displayModeBar':False})], className="chart")
                    ], className="charts"),
                    html.Div([dcc.Graph(id='g3', config={'displayModeBar':False})], className="chart chart-full"),
                    html.Div([
                        html.Div([dcc.Graph(id='g4', config={'displayModeBar':False})], className="chart"),
                        html.Div([dcc.Graph(id='g5', config={'displayModeBar':False})], className="chart"),
                        html.Div([dcc.Graph(id='g6', config={'displayModeBar':False})], className="chart")
                    ], style={'display':'grid','gridTemplateColumns':'repeat(3,1fr)','gap':'26px','marginBottom':'26px'}),
                    html.Div([dcc.Graph(id='g7', config={'displayModeBar':False})], className="chart chart-full")
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
    
    # Footer dengan info debug
    html.Div([
        html.P(f"Data loaded: {len(rfm)} customers | Clusters: {rfm['Cluster_KMeans'].nunique()}"),
        html.P(f"Running on Railway | Python {sys.version.split()[0]}"),
    ], className="foot")
])

# Callback untuk update dashboard
@app.callback(
    [Output('g1','figure'), Output('g2','figure'), Output('g3','figure'), 
     Output('g4','figure'), Output('g5','figure'), Output('g6','figure'), 
     Output('g7','figure'), Output('champ-detail','children'),
     Output('st','children'), Output('ins','children')],
    [Input('cf','value'), Input('rf','value'), Input('pf','value')]
)
def upd(sc, rr, sp):
    try:
        # Filter data
        df = rfm[(rfm['RFM_Score'] >= rr[0]) & (rfm['RFM_Score'] <= rr[1])]
        if sc != 'all':
            df = df[df['Cluster_KMeans'] == sc]
        if sp != 'all':
            df = df[df['Priority'] == sp]
        
        print(f"📈 Filtered to {len(df)} customers")
        
        # Chart 1: Customer Distribution Pie
        if 'Cluster_Label' in df.columns:
            cc = df['Cluster_Label'].value_counts()
        else:
            cc = df['Cluster_KMeans'].value_counts()
            
        f1 = go.Figure(go.Pie(
            labels=cc.index,
            values=cc.values,
            hole=.68,
            marker=dict(
                colors=[colors.get(l, '#95A5A6') for l in cc.index] if hasattr(colors, 'get') else None,
                line=dict(color='white', width=5)
            ),
            textfont=dict(size=14, family='Inter, Poppins', weight=700),
            textposition='outside',
            pull=[0.05]*len(cc)
        ))
        f1.update_layout(
            title={'text': "<b>🎯 Customer Distribution</b>", 'x':.5, 'font':{'size':20, 'family':'Inter, Poppins', 'color':'#2c3e50'}},
            height=420,
            annotations=[dict(
                text=f'<b>{len(df):,}</b><br><span style="font-size:14px">Customers</span>',
                x=.5, y=.5,
                font={'size':24, 'color':'#667eea', 'family':'Inter, Poppins'},
                showarrow=False
            )],
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        # Chart 2: Revenue by Segment
        if 'Monetary' in df.columns and 'Cluster_Label' in df.columns:
            rv = df.groupby('Cluster_Label')['Monetary'].sum().sort_values()
        else:
            rv = pd.Series([10000, 20000, 15000, 8000, 5000], 
                          index=['Segment A', 'Segment B', 'Segment C', 'Segment D', 'Segment E'])
            
        f2 = go.Figure(go.Bar(
            x=rv.values,
            y=rv.index,
            orientation='h',
            marker=dict(
                color=rv.values,
                colorscale='Sunset',
                line=dict(color='white', width=3)
            ),
            text=[f'£{v/1000:.1f}K' for v in rv.values],
            textposition='outside',
            textfont={'size':13, 'weight':700, 'family':'Inter, Poppins'}
        ))
        f2.update_layout(
            title={'text': "<b>💰 Revenue by Segment</b>", 'x':.5, 'font':{'size':20, 'family':'Inter, Poppins', 'color':'#2c3e50'}},
            xaxis={'title':'<b>Revenue (£)</b>', 'titlefont':{'size':14, 'family':'Inter, Poppins'}, 'gridcolor':'rgba(0,0,0,0.05)'},
            yaxis={'titlefont':{'size':14, 'family':'Inter, Poppins'}},
            height=420,
            plot_bgcolor='rgba(245,247,250,.6)',
            margin=dict(t=80, b=60, l=140, r=60)
        )
        
        # Chart 3: 3D RFM Analysis
        if all(col in df.columns for col in ['Recency', 'Frequency', 'Monetary']):
            f3 = go.Figure(go.Scatter3d(
                x=df['Recency'],
                y=df['Frequency'],
                z=df['Monetary'],
                mode='markers',
                marker=dict(
                    size=7,
                    color=df['Cluster_KMeans'],
                    colorscale='Rainbow',
                    showscale=True,
                    line=dict(width=.8, color='white'),
                    opacity=.88,
                    colorbar=dict(title='Cluster', thickness=20, len=0.7)
                ),
                text=df['Cluster_Label'] if 'Cluster_Label' in df.columns else df['Cluster_KMeans'],
                hovertemplate='<b>%{text}</b><br>Recency: %{x}<br>Frequency: %{y}<br>Monetary: £%{z:,.0f}<extra></extra>'
            ))
        else:
            # Fallback 3D plot dengan data dummy
            np.random.seed(42)
            n_points = 100
            f3 = go.Figure(go.Scatter3d(
                x=np.random.randn(n_points),
                y=np.random.randn(n_points),
                z=np.random.randn(n_points),
                mode='markers',
                marker=dict(size=5, color='blue', opacity=0.8)
            ))
            
        f3.update_layout(
            title={'text': "<b>📈 3D RFM Customer Analysis</b>", 'x':.5, 'font':{'size':20, 'family':'Inter, Poppins', 'color':'#2c3e50'}},
            height=650,
            scene=dict(
                xaxis=dict(title='<b>Recency (days)</b>', backgroundcolor='rgba(245,247,250,.4)', gridcolor='rgba(0,0,0,0.08)'),
                yaxis=dict(title='<b>Frequency</b>', backgroundcolor='rgba(245,247,250,.4)', gridcolor='rgba(0,0,0,0.08)'),
                zaxis=dict(title='<b>Monetary (£)</b>', backgroundcolor='rgba(245,247,250,.4)', gridcolor='rgba(0,0,0,0.08)'),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
            ),
            paper_bgcolor='rgba(245,247,250,.4)',
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        # Charts 4-6: Histograms
        def mh(d, col, ttl, clr):
            if col in d.columns:
                fig = go.Figure(go.Histogram(
                    x=d[col],
                    nbinsx=35,
                    marker=dict(color=clr, line=dict(color='white', width=2), opacity=.85)
                ))
            else:
                fig = go.Figure(go.Histogram(
                    x=np.random.randn(1000),
                    nbinsx=35,
                    marker=dict(color=clr, line=dict(color='white', width=2), opacity=.85)
                ))
                
            fig.update_layout(
                title={'text': f"<b>{ttl}</b>", 'x':.5, 'font':{'size':18, 'family':'Inter, Poppins', 'color':'#2c3e50'}},
                xaxis={'title': f'<b>{col}</b>', 'titlefont':{'size':13, 'family':'Inter, Poppins'}, 'gridcolor':'rgba(0,0,0,0.05)'},
                yaxis={'title':'<b>Count</b>', 'titlefont':{'size':13, 'family':'Inter, Poppins'}, 'gridcolor':'rgba(0,0,0,0.05)'},
                height=340,
                plot_bgcolor='rgba(245,247,250,.5)',
                margin=dict(t=70, b=50, l=60, r=40)
            )
            return fig
        
        f4 = mh(df, 'Recency', '⏰ Recency Distribution', '#ff6b6b')
        f5 = mh(df, 'Frequency', '🔄 Frequency Distribution', '#4ecdc4')
        f6 = mh(df, 'Monetary', '💵 Monetary Distribution', '#45b7d1')
        
        # Chart 7: Segment Summary Table
        if 'Cluster_Label' in df.columns:
            tb = df.groupby('Cluster_Label').agg({
                'Recency': 'mean',
                'Frequency': 'mean', 
                'Monetary': 'mean',
                'AvgOrderValue': 'mean',
                'RFM_Score': 'mean'
            }).round(1).reset_index()
            tb['Count'] = df.groupby('Cluster_Label').size().values
        else:
            tb = pd.DataFrame({
                'Cluster_Label': ['Segment A', 'Segment B', 'Segment C'],
                'Recency': [10, 50, 100],
                'Frequency': [5, 3, 1],
                'Monetary': [1000, 500, 200],
                'AvgOrderValue': [200, 167, 200],
                'RFM_Score': [8, 5, 2],
                'Count': [300, 400, 300]
            })
        
        f7 = go.Figure(go.Table(
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
                    tb['Cluster_Label'],
                    tb['Count'],
                    [f"{v:.0f}d" for v in tb['Recency']],
                    tb['Frequency'].round(1),
                    [f"£{v:,.0f}" for v in tb['Monetary']],
                    [f"£{v:.0f}" for v in tb['AvgOrderValue']],
                    tb['RFM_Score']
                ],
                fill_color=[['white', '#f8f9fc'] * len(tb)],
                align='center',
                font={'size':12, 'family':'Inter, Poppins'},
                height=38,
                line=dict(color='#e0e0e0', width=1)
            )
        ))
        f7.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
        
        # Champion Breakdown Section
        champion_clusters = [c for c in df['Cluster_KMeans'].unique() 
                           if c in profs and profs[c]['name'] == '🏆 Champions']
        champ_breakdown = None
        
        if len(champion_clusters) > 0:
            champ_cards = []
            for cid in sorted(champion_clusters):
                if cid in champion_details:
                    det = champion_details[cid]
                    champ_cards.append(html.Div([
                        html.Div(f"Champion C{cid}", className="champ-num"),
                        html.Div(f"🏅 {det['tier']}", className="champ-tier"),
                        html.Div(det['desc'], className="champ-desc"),
                        html.Div(f"📊 Characteristics: {det['char']}", className="champ-char")
                    ], className="champ-card"))
            
            if champ_cards:
                champ_breakdown = html.Div([
                    html.Div("🏆 Champion Segments Breakdown", className="champ-break-t"),
                    html.Div("Understanding the 4 Different Champion Tiers",
                            style={'textAlign':'center','fontSize':'1.1rem','marginBottom':'24px','opacity':'0.95'}),
                    html.Div(champ_cards, className="champ-grid")
                ], className="champ-break")
        
        # Strategy Cards
        st_cards = []
        for cid, p in profs.items():
            if sc == 'all' or sc == cid:
                st_cards.append(html.Div([
                    html.Div([
                        html.Div(p['name'], className="strat-name"),
                        html.Div(p['priority'], className="pri-badge")
                    ], className="strat-hdr"),
                    html.Div(f"📋 {p['strategy']} Strategy", className="strat-sub"),
                    html.Div([
                        html.Div("🎯 Key Tactics", className="tact-t"),
                        *[html.Div(t, className="tact") for t in p['tactics']]
                    ], className="tactics"),
                    html.Div([
                        html.Div("📊 Target KPIs", className="tact-t"),
                        html.Div([html.Div(k, className="kpi") for k in p['kpis']], className="kpi-g")
                    ], className="tactics"),
                    html.Div([
                        html.Div([
                            html.Div("Budget Allocation", className="budget-l"),
                            html.Div(p['budget'], className="budget-v")
                        ]),
                        html.Div([
                            html.Div("ROI Target", className="budget-l"),
                            html.Div(p['roi'], className="budget-v")
                        ])
                    ], className="budget")
                ], className="strat", style={'background': p['grad']}))
        
        # Insights
        if len(df) > 0:
            revenue_segment = df.groupby('Cluster_Label')['Monetary'].sum().idxmax() if 'Cluster_Label' in df.columns else "N/A"
            largest_group = df['Cluster_Label'].value_counts().idxmax() if 'Cluster_Label' in df.columns else "N/A"
            largest_count = df['Cluster_Label'].value_counts().max() if 'Cluster_Label' in df.columns else 0
            best_aov_segment = df.groupby('Cluster_Label')['AvgOrderValue'].mean().idxmax() if 'Cluster_Label' in df.columns else "N/A"
            best_aov_value = df.groupby('Cluster_Label')['AvgOrderValue'].mean().max() if 'Cluster_Label' in df.columns else 0
            most_frequent_segment = df.groupby('Cluster_Label')['Frequency'].mean().idxmax() if 'Cluster_Label' in df.columns else "N/A"
            most_frequent_value = df.groupby('Cluster_Label')['Frequency'].mean().max() if 'Cluster_Label' in df.columns else 0
        else:
            revenue_segment = largest_group = best_aov_segment = most_frequent_segment = "N/A"
            largest_count = best_aov_value = most_frequent_value = 0
        
        ins_cont = html.Div([
            html.Div("🧠 AI-Powered Insights & Recommendations", className="ins-t"),
            html.Div([
                html.Div([
                    html.Div("📊 Top Performers", className="ins-h"),
                    html.Ul([
                        html.Li(f"🏆 Highest Revenue: {revenue_segment}"),
                        html.Li(f"👥 Largest Group: {largest_group} ({largest_count:,} customers)"),
                        html.Li(f"💰 Best AOV: {best_aov_segment} (£{best_aov_value:.0f})"),
                        html.Li(f"🔄 Most Frequent: {most_frequent_segment} ({most_frequent_value:.1f} orders)")
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
        
        return f1, f2, f3, f4, f5, f6, f7, champ_breakdown, html.Div(st_cards, className="strat-g"), ins_cont
        
    except Exception as e:
        print(f"❌ Error in callback: {e}")
        traceback.print_exc()
        # Return empty figures and message in case of error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title={'text': "Error loading data", 'x':0.5},
            height=300
        )
        error_msg = html.Div([
            html.H3("⚠️ Error loading dashboard"),
            html.P(f"Error: {str(e)}"),
            html.P("Please check the server logs for details.")
        ], style={'textAlign': 'center', 'padding': '50px'})
        
        return [empty_fig] * 7 + [error_msg, error_msg, error_msg]

# Health check endpoint untuk Railway
@server.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Dashboard is running', 'customers': len(rfm)}, 200

# Setup and Run untuk Railway
if __name__ == '__main__':
    # Gunakan PORT dari environment variable Railway, default 8050
    port = int(os.environ.get("PORT", 8080))
    # Debug mode hanya jika bukan di production
    debug = os.environ.get("RAILWAY_ENVIRONMENT") != "production"
    
    print(f"\n{'='*80}")
    print(f"🚀 DASHBOARD STARTING ON PORT: {port}")
    print(f"📊 Debug mode: {debug}")
    print(f"👥 Data loaded: {len(rfm)} customers")
    print(f"{'='*80}\n")
    
    app.run_server(
        host='0.0.0.0',  # Penting untuk Railway
        port=port,
        debug=debug,
        dev_tools_hot_reload=False
    )
