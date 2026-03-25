"""
Streamlit Dashboard for E-Commerce Analytics
Interactive dashboard displaying all insights
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #fff;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    h2 {
        color: #34495e;
        font-weight: 600;
    }
    h3 {
        color: #7f8c8d;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and cache all datasets"""
    try:
        df = pd.read_csv('data/cleaned_ecommerce_data.csv')
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        rfm = pd.read_csv('data/rfm_analysis.csv')
        
        # Handle both old and new segment_summary formats
        segments = pd.read_csv('data/segment_summary.csv')
        # If 'segment' column exists, use it; otherwise assume first column is segment
        if 'segment' not in segments.columns and len(segments.columns) > 0:
            segments = segments.rename(columns={segments.columns[0]: 'segment'})
        segments = segments.set_index('segment')
        
        return df, rfm, segments
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None


def calculate_kpis(df):
    """Calculate key performance indicators"""
    # Filter out returns for KPI calculations
    sales_df = df[df['quantity'] > 0]
    
    kpis = {
        'total_revenue': sales_df['total_amount'].sum(),
        'total_profit': sales_df['profit'].sum(),
        'total_orders': sales_df['transaction_id'].nunique(),
        'unique_customers': sales_df['customer_id'].nunique(),
        'avg_order_value': sales_df['total_amount'].mean(),
        'profit_margin': (sales_df['profit'].sum() / sales_df['total_amount'].sum()) * 100,
        'total_units_sold': sales_df['quantity'].sum(),
        'return_rate': (df[df['quantity'] < 0]['quantity'].abs().sum() / 
                       df[df['quantity'] > 0]['quantity'].sum()) * 100
    }
    
    # Monthly growth
    monthly = sales_df.groupby('year_month')['total_amount'].sum().reset_index()
    if len(monthly) > 1:
        kpis['monthly_growth'] = ((monthly['total_amount'].iloc[-1] - monthly['total_amount'].iloc[-2]) 
                                  / monthly['total_amount'].iloc[-2] * 100)
    else:
        kpis['monthly_growth'] = 0
    
    return kpis


def render_header():
    """Render dashboard header"""
    st.title("📊 E-Commerce Analytics Dashboard")
    st.markdown("Comprehensive business intelligence for data-driven decisions")
    st.markdown("---")


def render_kpi_metrics(kpis):
    """Render KPI metric cards"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${kpis['total_revenue']:,.0f}",
            delta=f"{kpis['monthly_growth']:.1f}% vs last month"
        )
    
    with col2:
        st.metric(
            label="Total Profit",
            value=f"${kpis['total_profit']:,.0f}",
            delta=f"{kpis['profit_margin']:.1f}% margin"
        )
    
    with col3:
        st.metric(
            label="Total Orders",
            value=f"{kpis['total_orders']:,}"
        )
    
    with col4:
        st.metric(
            label="Unique Customers",
            value=f"{kpis['unique_customers']:,}"
        )
    
    with col5:
        st.metric(
            label="Avg Order Value",
            value=f"${kpis['avg_order_value']:.2f}"
        )


def render_overview_tab(df, kpis):
    """Render Overview tab content"""
    st.header("📈 Business Overview")
    
    # Monthly revenue trend
    monthly = df[df['quantity'] > 0].groupby('year_month').agg({
        'total_amount': 'sum',
        'profit': 'sum',
        'transaction_id': 'nunique'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=monthly['year_month'], y=monthly['total_amount'], 
               name='Revenue', marker_color='#3498db', opacity=0.7),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=monthly['year_month'], y=monthly['profit'], 
                  name='Profit', line=dict(color='#2ecc71', width=3), mode='lines+markers'),
        secondary_y=True
    )
    
    fig.update_layout(
        title_text="Monthly Revenue & Profit Trends",
        template='plotly_white',
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Revenue by category and geography
    col1, col2 = st.columns(2)
    
    with col1:
        category_data = df[df['quantity'] > 0].groupby('category')['total_amount'].sum().reset_index()
        fig_pie = px.pie(category_data, values='total_amount', names='category',
                        title='Revenue by Category', hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Spectral)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        geo_data = df[df['quantity'] > 0].groupby('country')['total_amount'].sum().reset_index()
        fig_geo = px.bar(geo_data.sort_values('total_amount', ascending=True), 
                        x='total_amount', y='country', orientation='h',
                        title='Revenue by Country', color='total_amount',
                        color_continuous_scale='Viridis')
        fig_geo.update_layout(height=400)
        st.plotly_chart(fig_geo, use_container_width=True)


def render_customers_tab(df, rfm, segments):
    """Render Customers tab content"""
    st.header("👥 Customer Analytics")
    
    # RFM Distribution
    st.subheader("RFM Analysis - Customer Segmentation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_recency = px.histogram(rfm, x='recency', nbins=30, 
                                  title='Recency Distribution (Days since last purchase)',
                                  color_discrete_sequence=['#3498db'])
        fig_recency.update_layout(height=350)
        st.plotly_chart(fig_recency, use_container_width=True)
    
    with col2:
        fig_frequency = px.histogram(rfm[rfm['frequency'] <= 20], x='frequency', nbins=20,
                                    title='Frequency Distribution (Number of orders)',
                                    color_discrete_sequence=['#2ecc71'])
        fig_frequency.update_layout(height=350)
        st.plotly_chart(fig_frequency, use_container_width=True)
    
    with col3:
        monetary_95 = rfm[rfm['monetary'] <= rfm['monetary'].quantile(0.95)]
        fig_monetary = px.histogram(monetary_95, x='monetary', nbins=30,
                                   title='Monetary Distribution (95th percentile)',
                                   color_discrete_sequence=['#e74c3c'])
        fig_monetary.update_layout(height=350)
        st.plotly_chart(fig_monetary, use_container_width=True)
    
    # Customer Segments
    st.subheader("Customer Segments")
    
    col1, col2 = st.columns(2)
    
    with col1:
        segments_reset = segments.reset_index()
        fig_segments = px.treemap(segments_reset, path=['segment'], values='count',
                                 color='total_revenue', hover_data=['percentage'],
                                 title='Customer Segments by Count & Revenue',
                                 color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_segments, use_container_width=True)
    
    with col2:
        fig_segment_bar = px.bar(segments_reset.sort_values('total_revenue'), 
                                x='segment', y='total_revenue',
                                title='Revenue by Customer Segment',
                                color='total_revenue', color_continuous_scale='Viridis')
        fig_segment_bar.update_layout(xaxis_tickangle=-45, height=450)
        st.plotly_chart(fig_segment_bar, use_container_width=True)
    
    # Segment recommendations
    st.subheader("📋 Segment Recommendations")
    
    segment_recommendations = {
        'Champions': 'Reward with VIP programs, use as brand advocates',
        'Loyal Customers': 'Upsell, offer loyalty rewards, maintain engagement',
        'Potential Loyalists': 'Nurture with onboarding, offer membership programs',
        'New Customers': 'Provide excellent onboarding, welcome discounts',
        'At Risk': 'Deploy win-back campaigns, offer significant discounts',
        'Cannot Lose Them': 'Immediate personal outreach, high-value incentives',
        'Lost': 'Attempt revival with discounts, conduct exit surveys'
    }
    
    for segment, rec in segment_recommendations.items():
        if segment in segments.index:
            count = int(segments.loc[segment, 'count'])
            revenue = segments.loc[segment, 'total_revenue']
            st.info(f"**{segment}** ({count} customers, ${revenue:,.0f} revenue): {rec}")


def render_products_tab(df):
    """Render Products tab content"""
    st.header("🛍️ Product Performance")
    
    # Top products
    top_products = df[df['quantity'] > 0].groupby(['product_name', 'category']).agg({
        'total_amount': 'sum',
        'quantity': 'sum',
        'profit': 'sum',
        'customer_id': 'nunique'
    }).reset_index().nlargest(15, 'total_amount')
    
    fig_products = px.bar(top_products, x='total_amount', y='product_name', 
                         color='category', orientation='h',
                         title='Top 15 Products by Revenue',
                         hover_data=['quantity', 'profit', 'customer_id'])
    fig_products.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_products, use_container_width=True)
    
    # Category performance
    col1, col2 = st.columns(2)
    
    with col1:
        category_perf = df[df['quantity'] > 0].groupby('category').agg({
            'total_amount': 'sum',
            'profit': 'sum',
            'quantity': 'sum',
            'transaction_id': 'nunique'
        }).reset_index()
        
        fig_category = px.scatter(category_perf, x='total_amount', y='profit',
                                 size='quantity', color='category',
                                 title='Category Performance: Revenue vs Profit',
                                 hover_data=['transaction_id'])
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # Price tier analysis
        price_analysis = df[df['quantity'] > 0].groupby('price_tier').agg({
            'total_amount': 'sum',
            'transaction_id': 'nunique',
            'customer_id': 'nunique'
        }).reset_index()
        
        fig_price = px.bar(price_analysis, x='price_tier', y='total_amount',
                          title='Revenue by Price Tier',
                          color='price_tier', text='transaction_id')
        fig_price.update_traces(texttemplate='%{text} orders', textposition='outside')
        st.plotly_chart(fig_price, use_container_width=True)


def render_operations_tab(df):
    """Render Operations tab content"""
    st.header("⚙️ Operational Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Payment methods
        payment_data = df[df['quantity'] > 0].groupby('payment_method').agg({
            'transaction_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        
        fig_payment = px.pie(payment_data, values='transaction_id', names='payment_method',
                            title='Transaction Distribution by Payment Method',
                            hole=0.3)
        st.plotly_chart(fig_payment, use_container_width=True)
    
    with col2:
        # Shipping methods
        shipping_data = df[df['quantity'] > 0].groupby('shipping_method').agg({
            'transaction_id': 'count',
            'total_amount': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        fig_shipping = px.bar(shipping_data, x='shipping_method', y='transaction_id',
                             color='profit', title='Orders by Shipping Method',
                             color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_shipping, use_container_width=True)
    
    # Sales by day of week
    st.subheader("Sales Patterns")
    
    daily_data = df[df['quantity'] > 0].groupby('day_of_week').agg({
        'total_amount': 'sum',
        'transaction_id': 'count'
    }).reset_index()
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_data['day_name'] = daily_data['day_of_week'].apply(lambda x: day_names[int(x)])
    
    fig_daily = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_daily.add_trace(
        go.Bar(x=daily_data['day_name'], y=daily_data['total_amount'], 
               name='Revenue', marker_color='#3498db'),
        secondary_y=False
    )
    
    fig_daily.add_trace(
        go.Scatter(x=daily_data['day_name'], y=daily_data['transaction_id'],
                  name='Transactions', line=dict(color='#e74c3c', width=3),
                  mode='lines+markers'),
        secondary_y=True
    )
    
    fig_daily.update_layout(
        title_text="Sales by Day of Week",
        template='plotly_white',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Discount analysis
    st.subheader("💰 Discount Impact Analysis")
    
    discount_df = df[df['quantity'] > 0].copy()
    discount_df['discount_bin'] = pd.cut(discount_df['discount'],
                                        bins=[0, 0.01, 0.1, 0.2, 0.5, 1.0],
                                        labels=['No Discount', '1-10%', '10-20%', '20-50%', '50%+'],
                                        include_lowest=True)
    
    discount_summary = discount_df.groupby('discount_bin').agg({
        'total_amount': ['sum', 'mean'],
        'quantity': 'sum',
        'transaction_id': 'count'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_discount_revenue = px.bar(discount_summary, x='discount_bin', 
                                      y=('total_amount', 'sum'),
                                      title='Revenue by Discount Level',
                                      color=('total_amount', 'sum'),
                                      color_continuous_scale='Viridis')
        st.plotly_chart(fig_discount_revenue, use_container_width=True)
    
    with col2:
        fig_discount_aov = px.bar(discount_summary, x='discount_bin',
                                 y=('total_amount', 'mean'),
                                 title='Average Order Value by Discount Level',
                                 color=('total_amount', 'mean'),
                                 color_continuous_scale='Plasma')
        st.plotly_chart(fig_discount_aov, use_container_width=True)


def render_recommendations_tab(segments, kpis):
    """Render Business Recommendations tab"""
    st.header("💡 Business Recommendations")
    
    st.markdown("""
    Based on the comprehensive analysis of your e-commerce data, here are the key recommendations:
    """)
    
    # Priority recommendations based on data
    st.subheader("🎯 Priority Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Customer Retention**
        - Focus on 'At Risk' and 'Cannot Lose Them' segments with personalized win-back campaigns
        - Implement loyalty program for 'Champions' and 'Loyal Customers'
        - Create onboarding program for 'New Customers' to increase retention
        
        **Revenue Growth**
        - Optimize pricing strategy based on price tier performance
        - Focus marketing spend on high-performing categories
        - Expand successful product lines in top-performing subcategories
        """)
    
    with col2:
        st.markdown(f"""
        **Operational Efficiency**
        - Current profit margin is {kpis['profit_margin']:.1f}% - consider cost optimization
        - Return rate is {kpis['return_rate']:.1f}% - investigate quality issues
        - Payment method distribution suggests opportunities for optimization
        
        **Inventory Management**
        - Monitor low-stock high-demand products for reordering
        - Optimize stock levels based on category performance
        - Consider seasonal adjustments for inventory planning
        """)
    
    # Segment-specific recommendations
    st.subheader("📊 Segment-Specific Strategies")
    
    segments_reset = segments.reset_index()
    
    for _, row in segments_reset.iterrows():
        segment = row['segment']
        count = int(row['count'])
        revenue = row['total_revenue']
        
        with st.expander(f"{segment} ({count} customers, ${revenue:,.0f} revenue)"):
            if segment == 'Champions':
                st.markdown("""
                - **VIP Treatment**: Offer exclusive early access to new products
                - **Referral Program**: Leverage as brand advocates with incentives
                - **Premium Support**: Dedicated account manager or priority support
                """)
            elif segment == 'Loyal Customers':
                st.markdown("""
                - **Cross-sell/Upsell**: Recommend complementary products
                - **Loyalty Rewards**: Points system or tier-based benefits
                - **Personalized Offers**: Based on purchase history
                """)
            elif segment == 'At Risk':
                st.markdown("""
                - **Win-back Campaign**: Aggressive discounting (15-25%)
                - **Personal Outreach**: Email or phone call from customer service
                - **Feedback Survey**: Understand reasons for decreased activity
                """)
            elif segment == 'New Customers':
                st.markdown("""
                - **Welcome Series**: Email sequence with product education
                - **Next Purchase Incentive**: 10-15% discount on second order
                - **Onboarding Guide**: Help them get maximum value
                """)
            else:
                st.markdown("""
                - **Engagement Campaign**: Regular communication with relevant offers
                - **Product Recommendations**: AI-driven personalized suggestions
                - **Reactivation Offers**: Time-limited promotions to drive purchases
                """)
    
    # Data-driven insights
    st.subheader("📈 Key Insights from Data")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.metric("Avg Order Value", f"${kpis['avg_order_value']:.2f}")
        st.caption("Benchmark against industry standards")
    
    with insight_col2:
        st.metric("Profit Margin", f"{kpis['profit_margin']:.1f}%")
        st.caption("Monitor for sustainability")
    
    with insight_col3:
        st.metric("Customer Base", f"{kpis['unique_customers']:,}")
        st.caption("Focus on retention & acquisition")


def main():
    """Main dashboard application"""
    
    render_header()
    
    # Load data
    df, rfm, segments = load_data()
    
    if df is None:
        st.error("Unable to load data. Please run the data generation and cleaning scripts first.")
        st.markdown("""
        **To get started:**
        1. Run `python data_generation.py` to create sample data
        2. Run `python data_cleaning.py` to clean the data
        3. Run `python rfm_analysis.py` for customer segmentation
        4. Then return to this dashboard
        """)
        return
    
    # Calculate KPIs
    kpis = calculate_kpis(df)
    
    # Render KPIs
    render_kpi_metrics(kpis)
    
    st.markdown("---")
    
    # Create tabs
    tabs = st.tabs(["📊 Overview", "👥 Customers", "🛍️ Products", "⚙️ Operations", "💡 Recommendations"])
    
    with tabs[0]:
        render_overview_tab(df, kpis)
    
    with tabs[1]:
        if rfm is not None and segments is not None:
            render_customers_tab(df, rfm, segments)
        else:
            st.warning("RFM analysis data not available. Please run rfm_analysis.py")
    
    with tabs[2]:
        render_products_tab(df)
    
    with tabs[3]:
        render_operations_tab(df)
    
    with tabs[4]:
        if segments is not None:
            render_recommendations_tab(segments, kpis)
        else:
            st.warning("Segment data not available")
    
    # Footer
    st.markdown("---")
    st.caption("E-Commerce Analytics Dashboard | Built with Streamlit | Data last updated: " + 
              pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'))


if __name__ == "__main__":
    main()
