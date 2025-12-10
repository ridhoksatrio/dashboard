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

# ... (rest of the code remains the same until the callback)

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
        
        # ... (rest of the callback remains the same for champion breakdown, strategy cards, and insights)
