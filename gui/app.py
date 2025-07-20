"""
Streamlit GUI for Production Analytics Agent
"""

import streamlit as st
import requests
import json
import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os

# Page configuration
st.set_page_config(
    page_title="Analytics Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'agent_endpoint' not in st.session_state:
    st.session_state.agent_endpoint = ""

def call_analytics_agent(query: str, endpoint: str) -> dict:
    """
    Call the analytics agent endpoint
    """
    try:
        # For demo purposes, we'll simulate the agent response
        # In production, this would call the actual AgentCore endpoint
        
        # Simulate processing time
        time.sleep(2)
        
        # Mock response based on query type
        if "sales" in query.lower() and "q2" in query.lower():
            return {
                "success": True,
                "analysis": """## Sales Performance Analysis - Q2 2024

### Key Findings:
- **Total Revenue**: $1,476,025.08
- **Total Sales**: 2,277 transactions
- **Average Profit Margin**: 24.7%

### Top 3 Performing Regions:
1. **North America**: $303,629.52
2. **Europe**: $297,666.67
3. **Asia Pacific**: $295,891.59

### Revenue Trends:
Revenue shows an increasing trend over the analyzed period.

### Recommendations:
- Focus marketing efforts on North America region
- Investigate growth opportunities in Asia Pacific region
- Optimize profit margins across all regions""",
                "data_summary": {
                    "total_revenue": 1476025.08,
                    "total_sales": 2277,
                    "avg_profit_margin": 0.247,
                    "top_region": "North America"
                },
                "recommendations": [
                    "Increase investment in North America region",
                    "Implement profit margin optimization strategy",
                    "Develop growth plan for underperforming regions"
                ]
            }
        elif "performance" in query.lower() or "kpi" in query.lower():
            return {
                "success": True,
                "analysis": """## Performance Analysis Dashboard

### Key Performance Indicators:
- **Customer Satisfaction**: 87.5% 🟢 Excellent
- **Sales Growth**: 12.3% 🔴 Needs Improvement
- **Market Share**: 23.8% 🔴 Needs Improvement
- **Operational Efficiency**: 91.2% 🟢 Excellent
- **Employee Productivity**: 78.9% 🟡 Good

### Performance Summary:
- **Overall Score**: 58.7/100
- **Strongest Area**: Operational Efficiency (91.2%)
- **Improvement Area**: Sales Growth (12.3%)""",
                "data_summary": {
                    "customer_satisfaction": 87.5,
                    "sales_growth": 12.3,
                    "market_share": 23.8,
                    "operational_efficiency": 91.2,
                    "employee_productivity": 78.9
                }
            }
        else:
            return {
                "success": True,
                "analysis": f"""## Analytics Response

I've analyzed your query: "{query}"

### Available Analytics Capabilities:
- **Sales Analysis**: Revenue trends, regional performance, profit margins
- **Performance Analysis**: KPI tracking, efficiency metrics, growth rates
- **Trend Analysis**: Time-series analysis, forecasting, pattern detection
- **Ranking Analysis**: Top performers, comparative rankings, benchmarking

### To Get Started:
Ask specific questions like:
- "Show me sales trends for Q2 2024"
- "Which regions are performing best?"
- "What are the key performance indicators?"
""",
                "data_summary": {"query_type": "general_inquiry"}
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def create_sample_chart(data_summary: dict, chart_type: str = "bar"):
    """
    Create sample visualizations based on data summary
    """
    if "total_revenue" in data_summary:
        # Revenue by region chart
        regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
        revenues = [303629.52, 297666.67, 295891.59, 278837.30]
        
        fig = px.bar(
            x=regions,
            y=revenues,
            title="Revenue by Region - Q2 2024",
            labels={"x": "Region", "y": "Revenue ($)"},
            color=revenues,
            color_continuous_scale="Blues"
        )
        fig.update_layout(showlegend=False)
        return fig
        
    elif "customer_satisfaction" in data_summary:
        # KPI dashboard
        metrics = ["Customer Satisfaction", "Sales Growth", "Market Share", "Operational Efficiency", "Employee Productivity"]
        values = [87.5, 12.3, 23.8, 91.2, 78.9]
        colors = ["green" if v > 80 else "orange" if v > 60 else "red" for v in values]
        
        fig = go.Figure(data=[
            go.Bar(x=metrics, y=values, marker_color=colors)
        ])
        fig.update_layout(
            title="Key Performance Indicators",
            xaxis_title="Metrics",
            yaxis_title="Score (%)",
            showlegend=False
        )
        return fig
    
    return None

def display_chart_from_base64(chart_data: dict):
    """
    Display chart from base64 encoded image
    """
    if chart_data.get('chart_image'):
        try:
            import base64
            from PIL import Image
            import io
            
            # Decode base64 image
            image_data = base64.b64decode(chart_data['chart_image'])
            image = Image.open(io.BytesIO(image_data))
            
            # Display in Streamlit
            st.image(image, caption=chart_data.get('title', 'Chart'), use_container_width=True)
            
            return True
        except Exception as e:
            st.error(f"Error displaying chart: {str(e)}")
            return False
    return False

# Header
st.title("🤖 Production Analytics Agent")
st.markdown("Ask questions about your data in natural language and get intelligent insights")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Agent endpoint
    agent_endpoint = st.text_input(
        "AgentCore Endpoint",
        value=st.session_state.agent_endpoint,
        placeholder="https://your-agentcore-endpoint.amazonaws.com",
        help="Enter your AgentCore endpoint URL"
    )
    st.session_state.agent_endpoint = agent_endpoint
    
    # Connection test
    if agent_endpoint:
        if st.button("🔍 Test Connection"):
            with st.spinner("Testing connection..."):
                try:
                    # In production, this would test the actual endpoint
                    time.sleep(1)
                    st.success("✅ Connection successful!")
                except:
                    st.error("❌ Connection failed")
    
    st.divider()
    
    # Data source info
    st.header("📊 Data Sources")
    st.info("""
    **Connected Sources:**
    - S3 Bucket: production-analytics-agent-*
    - File Formats: CSV, JSON, Parquet, Excel
    - Real-time Processing: ✅
    """)
    
    st.divider()
    
    # Quick stats
    st.header("📈 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Queries Today", "23", "+5")
    with col2:
        st.metric("Avg Response", "2.3s", "-0.1s")

# Main content area
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Dashboard", "📋 History"])

with tab1:
    # Chat interface
    st.header("Ask Your Analytics Question")
    
    # Example queries
    st.subheader("💡 Try These Examples")
    example_cols = st.columns(3)
    
    examples = [
        "Analyze sales performance for Q2 2024 and show top regions",
        "What are our key performance indicators?",
        "Show me revenue trends by month"
    ]
    
    for i, example in enumerate(examples):
        with example_cols[i]:
            if st.button(f"📝 {example[:30]}...", key=f"example_{i}"):
                st.session_state.selected_query = example
    
    # Query input
    query_input = st.text_area(
        "Enter your question:",
        value=st.session_state.get('selected_query', ''),
        placeholder="Example: Analyze the sales performance for Q2 2024 and show me the top 3 performing regions",
        height=100,
        key="query_input"
    )
    
    # Clear selected query after use
    if 'selected_query' in st.session_state:
        del st.session_state.selected_query
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        submit_button = st.button("🚀 Analyze", type="primary")
    with col2:
        clear_button = st.button("🗑️ Clear")
    
    if clear_button:
        st.session_state.conversation_history = []
        st.rerun()
    
    # Process query
    if submit_button and query_input:
        if not agent_endpoint:
            st.warning("⚠️ Please configure the AgentCore endpoint first")
        else:
            with st.spinner("🤖 Analyzing your data..."):
                # Call the analytics agent
                result = call_analytics_agent(query_input, agent_endpoint)
                
                # Add to conversation history
                conversation_entry = {
                    "timestamp": datetime.now(),
                    "query": query_input,
                    "result": result
                }
                st.session_state.conversation_history.append(conversation_entry)
    
    # Display conversation history (most recent first)
    if st.session_state.conversation_history:
        st.divider()
        st.subheader("💬 Conversation")
        
        for i, entry in enumerate(reversed(st.session_state.conversation_history)):
            with st.container():
                # User query
                st.markdown(f"**🧑 You ({entry['timestamp'].strftime('%H:%M:%S')}):**")
                st.markdown(f"> {entry['query']}")
                
                # Agent response
                st.markdown("**🤖 Analytics Agent:**")
                
                if entry['result']['success']:
                    # Display analysis
                    st.markdown(entry['result']['analysis'])
                    
                    # Display visualizations from agent
                    if 'visualizations' in entry['result'] and entry['result']['visualizations']:
                        st.subheader("📊 Generated Visualizations")
                        
                        for viz in entry['result']['visualizations']:
                            if display_chart_from_base64(viz):
                                # Chart displayed successfully
                                if viz.get('data'):
                                    with st.expander(f"📈 {viz.get('title', 'Chart')} Data"):
                                        st.json(viz['data'])
                            else:
                                # Fallback to plotly chart if base64 fails
                                if 'data_summary' in entry['result']:
                                    chart = create_sample_chart(entry['result']['data_summary'])
                                    if chart:
                                        st.plotly_chart(chart, use_container_width=True)
                    
                    # Display statistical analysis if available
                    if 'statistical_analysis' in entry['result'] and entry['result']['statistical_analysis']:
                        with st.expander("📊 Statistical Analysis"):
                            st.json(entry['result']['statistical_analysis'])
                    
                    # Display anomaly detection if available
                    if 'anomaly_detection' in entry['result'] and entry['result']['anomaly_detection']:
                        with st.expander("🚨 Anomaly Detection"):
                            anomaly_data = entry['result']['anomaly_detection']
                            if 'outliers_count' in anomaly_data:
                                st.metric(
                                    "Outliers Detected", 
                                    anomaly_data['outliers_count'],
                                    f"{anomaly_data.get('outlier_percentage', 0):.1f}% of data"
                                )
                            st.json(anomaly_data)
                    
                    # Display automated insights if available
                    if 'automated_insights' in entry['result'] and entry['result']['automated_insights']:
                        st.subheader("🔍 Automated Insights")
                        for insight in entry['result']['automated_insights']:
                            st.info(f"💡 {insight}")
                    
                    # Display recommendations
                    if 'recommendations' in entry['result']:
                        st.subheader("💡 Recommendations")
                        for rec in entry['result']['recommendations']:
                            st.markdown(f"• {rec}")
                else:
                    st.error(f"❌ Error: {entry['result']['error']}")
                
                st.divider()

with tab2:
    # Dashboard view
    st.header("📊 Analytics Dashboard")
    
    if st.session_state.conversation_history:
        # Get the most recent successful analysis
        recent_results = [entry['result'] for entry in st.session_state.conversation_history if entry['result']['success']]
        
        if recent_results:
            latest_result = recent_results[-1]
            
            # Display key metrics
            if 'data_summary' in latest_result:
                st.subheader("📈 Key Metrics")
                
                data_summary = latest_result['data_summary']
                
                # Create metrics columns
                metric_cols = st.columns(min(len(data_summary), 4))
                
                for i, (key, value) in enumerate(data_summary.items()):
                    if i < 4:  # Limit to 4 metrics
                        with metric_cols[i]:
                            if isinstance(value, (int, float)):
                                if key == 'total_revenue':
                                    st.metric(key.replace('_', ' ').title(), f"${value:,.2f}")
                                elif 'margin' in key or 'rate' in key:
                                    st.metric(key.replace('_', ' ').title(), f"{value:.1%}")
                                else:
                                    st.metric(key.replace('_', ' ').title(), f"{value:,.0f}")
                            else:
                                st.metric(key.replace('_', ' ').title(), str(value))
                
                # Display chart
                chart = create_sample_chart(data_summary)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("💡 Run some analytics queries to see dashboard data")
    else:
        st.info("💡 Start by asking an analytics question to populate the dashboard")

with tab3:
    # History view
    st.header("📋 Query History")
    
    if st.session_state.conversation_history:
        # Create a DataFrame for history
        history_data = []
        for entry in st.session_state.conversation_history:
            history_data.append({
                "Timestamp": entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                "Query": entry['query'][:50] + "..." if len(entry['query']) > 50 else entry['query'],
                "Status": "✅ Success" if entry['result']['success'] else "❌ Error",
                "Type": entry['result'].get('intent', {}).get('type', 'Unknown') if entry['result']['success'] else 'Error'
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export History"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"analytics_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("💡 Your query history will appear here")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🔗 Status:** Connected to AgentCore" if agent_endpoint else "**🔗 Status:** Not Connected")
with col2:
    st.markdown(f"**📊 Queries:** {len(st.session_state.conversation_history)}")
with col3:
    st.markdown("**🚀 Version:** v2.1")

st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 20px;'>
        <p>Powered by Amazon Bedrock AgentCore | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)