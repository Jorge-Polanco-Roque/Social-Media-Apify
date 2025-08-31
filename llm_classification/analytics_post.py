import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Configure page
st.set_page_config(
    page_title="TikTok Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .kpi-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        margin: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process TikTok data"""
    try:
        # Load data
        df = pd.read_csv('../Extracción/tiktok_posts_clasedepost.csv')
        
        # Process authorMeta column to extract author name
        def extract_author_name(author_meta_str):
            try:
                # Convert string to dictionary
                author_dict = eval(author_meta_str)
                return author_dict.get('name', 'Unknown')
            except:
                return 'Unknown'
        
        # Extract author names
        df['author_name'] = df['authorMeta'].apply(extract_author_name)
        
        # Convert createTimeISO to datetime
        df['createTimeISO'] = pd.to_datetime(df['createTimeISO'])
        df['date'] = df['createTimeISO'].dt.date
        df['hour'] = df['createTimeISO'].dt.hour
        df['day_of_week'] = df['createTimeISO'].dt.day_name()
        
        # Calculate engagement metrics
        df['total_engagement'] = df['diggCount'] + df['shareCount'] + df['commentCount']
        df['engagement_rate'] = df['total_engagement'] / df['playCount'].replace(0, 1) * 100
        
        # Performance categories
        df['performance_category'] = pd.cut(
            df['total_engagement'], 
            bins=[0, 50, 200, 500, float('inf')], 
            labels=['Low', 'Medium', 'High', 'Viral']
        )
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def create_kpi_cards(df):
    """Create KPI cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="kpi-card">
                <h3>Total Posts</h3>
                <h2>{:,}</h2>
            </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        avg_engagement = df['total_engagement'].mean()
        st.markdown("""
            <div class="kpi-card">
                <h3>Avg Engagement</h3>
                <h2>{:.0f}</h2>
            </div>
        """.format(avg_engagement), unsafe_allow_html=True)
    
    with col3:
        total_views = df['playCount'].sum()
        st.markdown("""
            <div class="kpi-card">
                <h3>Total Views</h3>
                <h2>{:,.0f}</h2>
            </div>
        """.format(total_views), unsafe_allow_html=True)
    
    with col4:
        unique_authors = df['author_name'].nunique()
        st.markdown("""
            <div class="kpi-card">
                <h3>Unique Authors</h3>
                <h2>{}</h2>
            </div>
        """.format(unique_authors), unsafe_allow_html=True)

def create_performance_comparison(df):
    """Create performance comparison charts - Author focused"""
    st.subheader("👥 Author Performance Comparison")
    
    # Engagement breakdown selector
    engagement_options = {
        'Total Engagement': 'total_engagement',
        'Likes (Digg Count)': 'diggCount', 
        'Shares': 'shareCount',
        'Comments': 'commentCount',
        'Views': 'playCount',
        'Engagement Rate (%)': 'engagement_rate'
    }
    
    selected_metric = st.selectbox(
        "Select Engagement Metric to Analyze:",
        options=list(engagement_options.keys()),
        index=0
    )
    
    metric_column = engagement_options[selected_metric]
    
    # Author filter controls
    agg_method = st.selectbox("Aggregation Method:", ['mean', 'median', 'sum'], key='agg_method')
    
    # Calculate author statistics - safe approach
    # Create separate aggregations to avoid column conflicts
    main_metric = df.groupby('author_name')[metric_column].agg(agg_method).round(2)
    other_metrics = df.groupby('author_name').agg({
        'total_engagement': 'mean',
        'playCount': 'mean',
        'diggCount': 'mean',
        'shareCount': 'mean',
        'commentCount': 'mean'
    }).round(2)
    post_counts = df.groupby('author_name').size()
    
    # Combine all metrics
    author_stats = pd.concat([
        main_metric.rename(f'selected_metric_{agg_method}'),
        other_metrics.rename(columns={
            'total_engagement': 'total_engagement_mean',
            'playCount': 'playCount_mean',
            'diggCount': 'diggCount_mean', 
            'shareCount': 'shareCount_mean',
            'commentCount': 'commentCount_mean'
        }),
        post_counts.rename('post_count')
    ], axis=1).reset_index()
    
    # Filter authors with minimum posts (fixed at 3)
    author_stats_filtered = author_stats[author_stats['post_count'] >= 3]
    
    # Get top authors by selected metric
    max_authors = min(10, len(author_stats_filtered))
    top_authors = author_stats_filtered.sort_values(f'selected_metric_{agg_method}', ascending=False).head(max_authors).reset_index(drop=True)
    
    # Main author performance chart
    fig_main = px.bar(
        top_authors,
        x='author_name',
        y=f'selected_metric_{agg_method}',
        title=f'Top {len(top_authors)} Authors by {selected_metric} ({agg_method.title()})',
        color=f'selected_metric_{agg_method}',
        color_continuous_scale='viridis',
        text=f'selected_metric_{agg_method}',
        hover_data={
            'post_count': True,
            'total_engagement_mean': ':.1f',
            'playCount_mean': ':.0f'
        }
    )
    fig_main.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_main.update_layout(
        xaxis_tickangle=-45, 
        height=500,
        xaxis_title="Author",
        yaxis_title=f"{selected_metric} ({agg_method.title()})"
    )
    st.plotly_chart(fig_main, use_container_width=True)
    
    # Author KPI comparison table
    st.subheader("📊 Detailed Author KPIs")
    
    # Prepare detailed metrics table
    detailed_author_metrics = top_authors[[
        'author_name', 'post_count', 'total_engagement_mean', 'playCount_mean', 
        'diggCount_mean', 'shareCount_mean', 'commentCount_mean'
    ]].copy()
    
    detailed_author_metrics.columns = [
        'Author', 'Posts', 'Avg Engagement', 'Avg Views', 
        'Avg Likes', 'Avg Shares', 'Avg Comments'
    ]
    
    # Format numbers for better readability
    for col in ['Avg Engagement', 'Avg Views', 'Avg Likes', 'Avg Shares', 'Avg Comments']:
        detailed_author_metrics[col] = detailed_author_metrics[col].apply(lambda x: f"{x:,.1f}")
    
    st.dataframe(detailed_author_metrics, use_container_width=True, hide_index=True)
    
    # Multi-metric comparison
    st.subheader("🔍 Multi-Metric Author Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter plot: Engagement vs Views
        fig_scatter = px.scatter(
            top_authors,
            x='playCount_mean',
            y='total_engagement_mean',
            size='post_count',
            color='author_name',
            title='Engagement vs Views by Author',
            hover_data=['post_count'],
            labels={
                'playCount_mean': 'Average Views',
                'total_engagement_mean': 'Average Engagement'
            }
        )
        fig_scatter.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Radar chart for top 5 authors
        top_5_authors = top_authors.head(5)
        
        # Normalize metrics for radar chart (0-100 scale)
        metrics_for_radar = ['diggCount_mean', 'shareCount_mean', 'commentCount_mean', 'playCount_mean']
        radar_data = []
        
        for _, author in top_5_authors.iterrows():
            author_metrics = []
            for metric in metrics_for_radar:
                # Normalize to 0-100 scale within top authors
                max_val = top_authors[metric].max()
                min_val = top_authors[metric].min()
                if max_val > min_val:
                    normalized = ((author[metric] - min_val) / (max_val - min_val)) * 100
                else:
                    normalized = 50
                author_metrics.append(normalized)
            
            radar_data.append({
                'Author': author['author_name'],
                'Likes': author_metrics[0],
                'Shares': author_metrics[1],
                'Comments': author_metrics[2],
                'Views': author_metrics[3]
            })
        
        # Create radar chart
        fig_radar = go.Figure()
        
        for author_data in radar_data:
            fig_radar.add_trace(go.Scatterpolar(
                r=[author_data['Likes'], author_data['Shares'], 
                   author_data['Comments'], author_data['Views']],
                theta=['Likes', 'Shares', 'Comments', 'Views'],
                fill='toself',
                name=author_data['Author']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Top 5 Authors - Multi-Metric Comparison",
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)

def create_author_benchmarking(df):
    """Create comprehensive author benchmarking analysis"""
    st.subheader("🏆 Author Benchmarking & Rankings")
    
    # Calculate comprehensive author metrics
    author_metrics = df.groupby('author_name').agg({
        'diggCount': ['mean', 'sum', 'count'],
        'shareCount': ['mean', 'sum'],
        'commentCount': ['mean', 'sum'],
        'playCount': ['mean', 'sum'],
        'total_engagement': ['mean', 'sum'],
        'engagement_rate': 'mean'
    }).round(2)
    
    # Flatten columns
    author_metrics.columns = [
        'likes_mean', 'likes_sum', 'post_count',
        'shares_mean', 'shares_sum',
        'comments_mean', 'comments_sum',
        'views_mean', 'views_sum',
        'engagement_mean', 'engagement_sum',
        'engagement_rate_mean'
    ]
    
    # Filter authors with at least 3 posts
    author_metrics = author_metrics[author_metrics['post_count'] >= 3].reset_index()
    
    # Calculate ranks for different metrics
    metrics_to_rank = {
        'engagement_mean': 'Avg Engagement Rank',
        'likes_mean': 'Avg Likes Rank',
        'shares_mean': 'Avg Shares Rank',
        'comments_mean': 'Avg Comments Rank',
        'views_mean': 'Avg Views Rank',
        'engagement_rate_mean': 'Engagement Rate Rank'
    }
    
    for metric, rank_col in metrics_to_rank.items():
        author_metrics[rank_col] = author_metrics[metric].rank(ascending=False, method='min').astype(int)
    
    # Calculate overall performance score (weighted average of ranks)
    rank_columns = list(metrics_to_rank.values())
    author_metrics['Overall Score'] = author_metrics[rank_columns].mean(axis=1)
    author_metrics['Overall Rank'] = author_metrics['Overall Score'].rank(method='min').astype(int)
    
    # Top performers section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥇 Top 10 Overall Performers")
        top_performers = author_metrics.nsmallest(10, 'Overall Score')[
            ['author_name', 'Overall Rank', 'post_count', 'engagement_mean', 'views_mean']
        ].copy()
        top_performers.columns = ['Author', 'Rank', 'Posts', 'Avg Engagement', 'Avg Views']
        
        # Format numbers
        top_performers['Avg Engagement'] = top_performers['Avg Engagement'].apply(lambda x: f"{x:,.0f}")
        top_performers['Avg Views'] = top_performers['Avg Views'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(top_performers, hide_index=True, use_container_width=True)
    
    with col2:
        # Total engagement distribution by author (without outliers)
        fig_dist = px.box(
            df[df['author_name'].isin(author_metrics['author_name'].head(10))],
            x='author_name',
            y='total_engagement',
            color='author_name',
            title='Total Engagement Distribution by Top Authors',
            points=False  # Remove outliers for better visibility
        )
        fig_dist.update_layout(
            xaxis_title="Author",
            yaxis_title="Total Engagement",
            height=350,
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.caption("📝 *Note: Outliers removed for better distribution visibility*")
    
    # Detailed comparison matrix
    st.subheader("📈 Author Performance Matrix")
    
    # Select authors to compare
    available_authors = author_metrics['author_name'].tolist()
    selected_authors = st.multiselect(
        "Select authors to compare (max 8):",
        options=available_authors,
        default=available_authors[:5],
        max_selections=8
    )
    
    if selected_authors:
        comparison_data = author_metrics[author_metrics['author_name'].isin(selected_authors)]
        
        # Create comparison heatmap
        metrics_for_heatmap = ['likes_mean', 'shares_mean', 'comments_mean', 'views_mean', 'engagement_rate_mean']
        heatmap_data = comparison_data.set_index('author_name')[metrics_for_heatmap]
        
        # Normalize for better comparison
        heatmap_normalized = heatmap_data.div(heatmap_data.max(axis=0), axis=1) * 100
        
        fig_comparison = px.imshow(
            heatmap_normalized.T,
            title='Author Performance Heatmap (Normalized %)',
            color_continuous_scale='RdYlBu_r',
            aspect='auto',
            labels={'x': 'Author', 'y': 'Metric', 'color': '% of Best Performer'}
        )
        
        # Update layout
        fig_comparison.update_layout(
            height=400,
            yaxis=dict(
                ticktext=['Avg Likes', 'Avg Shares', 'Avg Comments', 'Avg Views', 'Engagement Rate'],
                tickvals=list(range(5))
            )
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Detailed metrics table for selected authors
        detailed_comparison = comparison_data[[
            'author_name', 'post_count', 'engagement_mean', 'likes_mean', 
            'shares_mean', 'comments_mean', 'views_mean', 'engagement_rate_mean'
        ]].copy()
        
        detailed_comparison.columns = [
            'Author', 'Posts', 'Avg Engagement', 'Avg Likes', 
            'Avg Shares', 'Avg Comments', 'Avg Views', 'Engagement Rate %'
        ]
        
        # Format numbers
        for col in ['Avg Engagement', 'Avg Likes', 'Avg Shares', 'Avg Comments', 'Avg Views']:
            detailed_comparison[col] = detailed_comparison[col].apply(lambda x: f"{x:,.1f}")
        detailed_comparison['Engagement Rate %'] = detailed_comparison['Engagement Rate %'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(detailed_comparison, hide_index=True, use_container_width=True)
    
    # Performance insights
    st.subheader("💡 Key Insights")
    
    # Calculate some insights
    top_engagement = author_metrics.loc[author_metrics['engagement_mean'].idxmax()]
    top_views = author_metrics.loc[author_metrics['views_mean'].idxmax()]
    most_consistent = author_metrics.nsmallest(1, 'Overall Score').iloc[0]
    
    insights_col1, insights_col2, insights_col3 = st.columns(3)
    
    with insights_col1:
        st.metric(
            "🔥 Highest Avg Engagement",
            top_engagement['author_name'],
            f"{top_engagement['engagement_mean']:,.0f}"
        )
    
    with insights_col2:
        st.metric(
            "👁️ Most Views on Average",
            top_views['author_name'],
            f"{top_views['views_mean']:,.0f}"
        )
    
    with insights_col3:
        st.metric(
            "⭐ Most Consistent Performer",
            most_consistent['author_name'],
            f"Rank #{most_consistent['Overall Rank']}"
        )

def create_time_series_analysis(df):
    """Create time series analysis"""
    st.subheader("⏰ Time Series Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Posts over time by type
        daily_posts = df.groupby(['date', 'clase_llm']).size().reset_index(name='post_count')
        
        fig_time_series = px.line(
            daily_posts,
            x='date',
            y='post_count',
            color='clase_llm',
            title='Posts Over Time by Type',
            markers=True
        )
        fig_time_series.update_layout(height=400)
        st.plotly_chart(fig_time_series, use_container_width=True)
    
    with col2:
        # Engagement over time
        daily_engagement = df.groupby('date')['total_engagement'].mean().reset_index()
        
        fig_engagement_time = px.line(
            daily_engagement,
            x='date',
            y='total_engagement',
            title='Average Engagement Over Time',
            markers=True,
            line_shape='spline'
        )
        fig_engagement_time.update_traces(line_color='#ff6b6b')
        fig_engagement_time.update_layout(height=400)
        st.plotly_chart(fig_engagement_time, use_container_width=True)

def create_engagement_heatmap(df):
    """Create engagement heatmap by day and hour with complete time grid"""
    st.subheader("🔥 Engagement Heatmap")
    
    # Create complete time grid (all days and hours)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = list(range(24))
    
    # Create all possible combinations
    import itertools
    all_combinations = list(itertools.product(day_order, hours))
    complete_grid = pd.DataFrame(all_combinations, columns=['day_of_week', 'hour'])
    
    # Calculate actual engagement data
    heatmap_data = df.groupby(['day_of_week', 'hour'])['total_engagement'].mean().reset_index()
    
    # Merge with complete grid to fill missing combinations with 0
    complete_heatmap = complete_grid.merge(heatmap_data, on=['day_of_week', 'hour'], how='left')
    complete_heatmap['total_engagement'] = complete_heatmap['total_engagement'].fillna(0)
    
    # Create pivot table
    heatmap_pivot = complete_heatmap.pivot(index='day_of_week', columns='hour', values='total_engagement')
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    
    # Only create heatmap if we have data
    if not heatmap_pivot.empty:
        # Custom color scale
        fig_heatmap = px.imshow(
            heatmap_pivot,
            title='Average Engagement by Day and Hour',
            color_continuous_scale='Viridis',
            aspect='auto',
            labels={'x': 'Hour', 'y': 'Day', 'color': 'Avg Engagement'}
        )
        
        # Improve layout and formatting
        fig_heatmap.update_layout(
            height=450,
            font_size=12,
            coloraxis_colorbar=dict(
                title=dict(
                    text="Average<br>Engagement",
                    side="right"
                ),
                tickformat=".0f"
            ),
            xaxis=dict(
                title="Hour of Day",
                tickmode='linear',
                dtick=2  # Show every 2 hours
            ),
            yaxis=dict(
                title="Day of Week"
            )
        )
        
        # Add hover template for better interactivity
        fig_heatmap.update_traces(
            hovertemplate='Day: %{y}<br>Hour: %{x}<br>Avg Engagement: %{z:.1f}<extra></extra>'
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Add interpretation help
        st.info("💡 **Tip:** Darker colors indicate higher engagement. Zero values (dark blue) represent times with no posts or zero engagement.")
    else:
        st.warning("Not enough data to create engagement heatmap.")

def create_content_analysis(df):
    """Create content analysis"""
    st.subheader("📝 Content Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Post type distribution
        type_distribution = df['clase_llm'].value_counts()
        
        fig_pie = px.pie(
            values=type_distribution.values,
            names=type_distribution.index,
            title='Distribution of Post Types'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Performance category distribution with ranges
        performance_dist = df['performance_category'].value_counts()
        
        fig_performance_pie = px.pie(
            values=performance_dist.values,
            names=performance_dist.index,
            title='Performance Category Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_performance_pie, use_container_width=True)
        
        # Add performance category ranges explanation
        st.info("""
        📊 **Performance Category Ranges:**
        - **Low**: 0-50 total engagement
        - **Medium**: 51-200 total engagement  
        - **High**: 201-500 total engagement
        - **Viral**: 500+ total engagement
        """)

def create_detailed_metrics_table(df):
    """Create detailed metrics table"""
    st.subheader("📊 Detailed Metrics by Post Type")
    
    detailed_metrics = df.groupby('clase_llm').agg({
        'playCount': ['mean', 'median', 'max'],
        'diggCount': ['mean', 'median', 'max'],
        'shareCount': ['mean', 'median', 'max'],
        'commentCount': ['mean', 'median', 'max'],
        'total_engagement': ['mean', 'median', 'max'],
        'engagement_rate': ['mean', 'median', 'max']
    }).round(2)
    
    # Flatten column names
    detailed_metrics.columns = ['_'.join(col).strip() for col in detailed_metrics.columns.values]
    
    st.dataframe(detailed_metrics, use_container_width=True)

def create_statistical_analysis(df):
    """Create statistical analysis of engagement by post category"""
    st.subheader("📈 Statistical Analysis: Engagement vs Post Categories")
    
    # Import required libraries
    try:
        from scipy.stats import f_oneway, kruskal
        from scipy import stats
    except ImportError:
        st.error("scipy is required for statistical analysis. Please install it.")
        return
    
    # Overall ANOVA test
    st.subheader("🧪 Overall Statistical Tests")
    
    # Group data by post category
    categories = df['clase_llm'].unique()
    category_groups = [df[df['clase_llm'] == cat]['total_engagement'].dropna() for cat in categories]
    
    # Remove empty groups
    category_groups = [group for group in category_groups if len(group) > 0]
    
    if len(category_groups) < 2:
        st.warning("Need at least 2 categories with data for statistical analysis.")
        return
    
    # Perform ANOVA (parametric) and Kruskal-Wallis (non-parametric)
    try:
        f_stat, p_value_anova = f_oneway(*category_groups)
        h_stat, p_value_kruskal = kruskal(*category_groups)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "🔬 ANOVA F-statistic", 
                f"{f_stat:.4f}",
                f"p-value: {p_value_anova:.6f}"
            )
            
            if p_value_anova < 0.05:
                st.success("✅ Significant difference between categories (α=0.05)")
            else:
                st.info("ℹ️ No significant difference between categories (α=0.05)")
        
        with col2:
            st.metric(
                "🔬 Kruskal-Wallis H-statistic",
                f"{h_stat:.4f}", 
                f"p-value: {p_value_kruskal:.6f}"
            )
            
            if p_value_kruskal < 0.05:
                st.success("✅ Significant difference (non-parametric, α=0.05)")
            else:
                st.info("ℹ️ No significant difference (non-parametric, α=0.05)")
    
    except Exception as e:
        st.error(f"Error in statistical tests: {e}")
        return
    
    # Visualization of distributions
    st.subheader("📊 Engagement Distribution by Post Category")
    
    fig_violin = px.violin(
        df,
        x='clase_llm',
        y='total_engagement',
        color='clase_llm',
        title='Total Engagement Distribution by Post Category',
        box=True,
        points=False  # Remove outliers for better visibility
    )
    fig_violin.update_layout(
        height=400,
        showlegend=False,
        xaxis_tickangle=-45,
        xaxis_title="Post Category",
        yaxis_title="Total Engagement"
    )
    st.plotly_chart(fig_violin, use_container_width=True)
    st.caption("📝 *Note: Outliers removed for better distribution visibility*")
    
    # Author-level analysis
    st.subheader("👥 Author-Level Statistical Analysis")
    
    # Get authors with sufficient posts
    author_post_counts = df['author_name'].value_counts()
    authors_with_multiple_posts = author_post_counts[author_post_counts >= 5].index.tolist()
    
    if len(authors_with_multiple_posts) == 0:
        st.warning("No authors with 5+ posts for individual analysis.")
        return
    
    # Analyze each author individually
    author_results = []
    
    for author in authors_with_multiple_posts[:10]:  # Top 10 authors only
        author_data = df[df['author_name'] == author]
        author_categories = author_data['clase_llm'].unique()
        
        if len(author_categories) >= 2:  # Need at least 2 categories
            author_groups = [
                author_data[author_data['clase_llm'] == cat]['total_engagement'].dropna() 
                for cat in author_categories
            ]
            author_groups = [group for group in author_groups if len(group) > 0]
            
            if len(author_groups) >= 2:
                try:
                    _, p_val = kruskal(*author_groups)
                    author_results.append({
                        'Author': author,
                        'Categories': len(author_categories),
                        'Total Posts': len(author_data),
                        'P-value': p_val,
                        'Significant': 'Yes' if p_val < 0.05 else 'No'
                    })
                except:
                    continue
    
    if author_results:
        results_df = pd.DataFrame(author_results)
        results_df['P-value'] = results_df['P-value'].apply(lambda x: f"{x:.6f}")
        
        st.dataframe(results_df, hide_index=True, use_container_width=True)
        
        # Summary statistics
        significant_authors = sum(1 for result in author_results if result['P-value'] < 0.05)
        total_authors = len(author_results)
        
        st.info(f"📊 **Summary**: {significant_authors}/{total_authors} authors show significant differences in engagement across post categories (α=0.05)")
        
        # Visualization of author-level significance
        fig_author_significance = px.bar(
            results_df,
            x='Author',
            y='Categories',
            color='Significant',
            title='Authors with Significant Category Differences',
            color_discrete_map={'Yes': '#2ecc71', 'No': '#e74c3c'}
        )
        fig_author_significance.update_layout(
            height=400,
            xaxis_tickangle=-45,
            xaxis_title="Author",
            yaxis_title="Number of Post Categories"
        )
        st.plotly_chart(fig_author_significance, use_container_width=True)
    else:
        st.warning("No authors have sufficient data across multiple categories for individual analysis.")

def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">📊 TikTok Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_and_process_data()
    
    if df.empty:
        st.error("No data available. Please check the CSV file.")
        return
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )
    
    # Post type filter
    selected_types = st.sidebar.multiselect(
        "Select Post Types",
        options=df['clase_llm'].unique(),
        default=df['clase_llm'].unique()
    )
    
    # Author filter
    selected_authors = st.sidebar.multiselect(
        "Select Authors",
        options=df['author_name'].unique(),
        default=df['author_name'].unique()[:10] if len(df['author_name'].unique()) > 10 else df['author_name'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['date'] >= date_range[0]) & 
        (df['date'] <= date_range[1]) &
        (df['clase_llm'].isin(selected_types)) &
        (df['author_name'].isin(selected_authors))
    ]
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return
    
    # 1. Executive Summary - KPIs Overview
    st.header("📈 Executive Summary")
    create_kpi_cards(filtered_df)
    
    st.markdown("---")
    
    # 2. Content Performance Analysis
    st.header("📝 Content Performance Overview")
    create_content_analysis(filtered_df)
    
    st.markdown("---")
    
    # 3. Author Performance Deep Dive
    st.header("👥 Author Performance Analysis")
    create_performance_comparison(filtered_df)
    
    st.markdown("---")
    
    # 4. Author Benchmarking & Rankings
    create_author_benchmarking(filtered_df)
    
    st.markdown("---")
    
    # 5. Temporal Analysis - When to Post
    st.header("⏰ Temporal Analysis")
    create_time_series_analysis(filtered_df)
    
    st.markdown("---")
    
    # 6. Optimal Timing - Engagement Heatmap
    create_engagement_heatmap(filtered_df)
    
    st.markdown("---")
    
    # 7. Statistical Insights
    st.header("🧪 Statistical Analysis")
    create_statistical_analysis(filtered_df)
    
    st.markdown("---")
    
    # 8. Detailed Reference Data
    st.header("📊 Reference Data")
    create_detailed_metrics_table(filtered_df)
    
    # Raw data section
    with st.expander("🔍 View Raw Data"):
        st.dataframe(filtered_df, use_container_width=True)
    
    # Download filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f'filtered_tiktok_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main()