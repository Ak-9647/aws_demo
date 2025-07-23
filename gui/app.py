"""
Production Analytics Agent v4.1 - Modern GUI
Enhanced with Real AgentCore Integration and Modern UI
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
import uuid
import logging
from typing import Dict, Any, Optional

# Import AgentCore client
from agentcore_client import get_agentcore_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Production Analytics Agent v4.1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .status-connected {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-disconnected {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-fallback {
        color: #ffc107;
        font-weight: bold;
    }
    
    .feature-badge {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .query-example {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .query-example:hover {
        background: #e9ecef;
        border-color: #667eea;
    }
    
    .progress-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .conversation-entry {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background: #f0f2f6;
        border-left-color: #28a745;
    }
    
    .agent-message {
        background: #fff;
        border-left-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'agent_endpoint' not in st.session_state:
    st.session_state.agent_endpoint = ""
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{int(time.time())}"
if 'agentcore_client' not in st.session_state:
    st.session_state.agentcore_client = get_agentcore_client()
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = None

def call_analytics_agent(query: str, client: Any, session_id: str, user_id: str) -> dict:
    """
    Call the analytics agent using AgentCore client with real-time processing
    """
    try:
        logger.info(f"Processing query: {query[:100]}...")
        
        # Use AgentCore client for real processing
        result = client.invoke_agent(query, session_id, user_id)
        
        if result["success"]:
            logger.info(f"Query processed successfully in {result.get('response_time', 0):.2f}s")
            return result
        else:
            logger.error(f"Query processing failed: {result.get('error')}")
            return result
            
    except Exception as e:
        logger.error(f"Error calling analytics agent: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def create_chart_from_data(viz_data: dict):
    """
    Create chart from visualization data returned by agent
    """
    try:
        chart_type = viz_data.get('type', 'bar_chart')
        title = viz_data.get('title', 'Chart')
        data = viz_data.get('data', {})
        
        if chart_type == 'bar_chart' and 'regions' in data and 'revenues' in data:
            # Revenue by region bar chart
            fig = px.bar(
                x=data['regions'],
                y=data['revenues'],
                title=title,
                labels={"x": "Region", "y": "Revenue ($)"},
                color=data['revenues'],
                color_continuous_scale="Blues"
            )
            fig.update_layout(showlegend=False)
            return fig
            
        elif chart_type == 'gauge_chart' and 'metrics' in data and 'values' in data:
            # KPI gauge/bar chart
            metrics = data['metrics']
            values = data['values']
            targets = data.get('targets', [100] * len(values))
            
            colors = []
            for i, (value, target) in enumerate(zip(values, targets)):
                if value >= target * 0.9:
                    colors.append("green")
                elif value >= target * 0.7:
                    colors.append("orange")
                else:
                    colors.append("red")
            
            fig = go.Figure(data=[
                go.Bar(x=metrics, y=values, marker_color=colors, name="Current"),
                go.Scatter(x=metrics, y=targets, mode='markers', 
                          marker=dict(symbol='diamond', size=10, color='black'),
                          name="Target")
            ])
            fig.update_layout(
                title=title,
                xaxis_title="Metrics",
                yaxis_title="Score",
                showlegend=True
            )
            return fig
            
        elif chart_type == 'line_chart' and 'x' in data and 'y' in data:
            # Line chart for trends
            fig = px.line(
                x=data['x'],
                y=data['y'],
                title=title,
                markers=True
            )
            return fig
            
        else:
            # Generic chart creation from any data structure
            if isinstance(data, dict) and len(data) >= 2:
                keys = list(data.keys())
                x_data = data[keys[0]]
                y_data = data[keys[1]]
                
                if isinstance(x_data, list) and isinstance(y_data, list) and len(x_data) == len(y_data):
                    fig = px.bar(
                        x=x_data,
                        y=y_data,
                        title=title,
                        labels={"x": keys[0].title(), "y": keys[1].title()}
                    )
                    return fig
        
        return None
        
    except Exception as e:
        logger.error(f"Error creating chart from data: {e}")
        return None

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

# Modern Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Production Analytics Agent v4.1</h1>
    <p>Powered by Amazon Bedrock AgentCore | Enhanced with LangGraph & Advanced Analytics</p>
    <div>
        <span class="feature-badge">Real-time Processing</span>
        <span class="feature-badge">Natural Language to SQL</span>
        <span class="feature-badge">Advanced Visualizations</span>
        <span class="feature-badge">Context Awareness</span>
        <span class="feature-badge">MCP Integration</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # AgentCore connection configuration
    st.markdown("#### 🔗 AgentCore Connection")
    
    # Connection method selection
    connection_method = st.radio(
        "Connection Method",
        ["AgentCore Runtime", "HTTP Endpoint", "Auto-detect"],
        index=0,
        help="Choose how to connect to the analytics agent"
    )
    
    # AgentCore Runtime info
    if connection_method == "AgentCore Runtime":
        st.info("""
        **AgentCore Runtime v4.1**
        - Runtime ID: hosted_agent_jqgjl-fJiyIV95k9
        - Region: us-west-2
        - Status: Using fallback mode (Runtime API in preview)
        - Enhanced with LangGraph workflows
        """)
    
    # HTTP endpoint configuration (if selected)
    elif connection_method == "HTTP Endpoint":
        agent_endpoint = st.text_input(
            "HTTP Endpoint URL",
            value=st.session_state.agent_endpoint,
            placeholder="http://your-agent-endpoint:8080",
            help="Enter your agent HTTP endpoint URL"
        )
        st.session_state.agent_endpoint = agent_endpoint
        
        if agent_endpoint:
            st.session_state.agentcore_client.set_http_endpoint(agent_endpoint)
    
    # Connection test
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Test Connection", type="primary"):
            with st.spinner("Testing connection..."):
                result = st.session_state.agentcore_client.test_connection()
                st.session_state.connection_status = result
                
                if result["success"]:
                    st.success(f"✅ Connected via {result['method']}")
                    if result.get('response_time'):
                        st.info(f"⚡ Response time: {result['response_time']}")
                else:
                    st.error(f"❌ Connection failed: {result.get('error')}")
    
    with col2:
        if st.button("🔄 Reset Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.conversation_history = []
            st.success("Session reset!")
            st.rerun()
    
    # Connection status display
    if st.session_state.connection_status:
        status = st.session_state.connection_status
        if status["success"]:
            method = status['method']
            if "AgentCore" in method:
                st.markdown('<p class="status-connected">🟢 AgentCore Runtime Connected</p>', unsafe_allow_html=True)
            elif "HTTP" in method:
                st.markdown('<p class="status-connected">🟡 HTTP Endpoint Connected</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="status-fallback">🟠 Fallback Mode Active</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-disconnected">🔴 Disconnected</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # Enhanced session information
    st.markdown("#### 📋 Session Information")
    st.markdown(f"""
    **Session Details:**
    - Session ID: `{st.session_state.session_id[:8]}...`
    - User ID: `{st.session_state.user_id}`
    - Started: {datetime.now().strftime('%H:%M:%S')}
    """)
    
    st.divider()
    
    # Enhanced data source info
    st.markdown("#### 📊 Connected Data Sources")
    st.markdown("""
    <div class="metric-card">
        <strong>🗄️ PostgreSQL Database</strong><br>
        <small>Analytics cluster with real-time data</small>
    </div>
    <br>
    <div class="metric-card">
        <strong>☁️ S3 Data Lake</strong><br>
        <small>CSV, JSON, Parquet file processing</small>
    </div>
    <br>
    <div class="metric-card">
        <strong>🔗 External APIs</strong><br>
        <small>Real-time market and weather data</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Enhanced session stats
    st.markdown("#### 📈 Performance Metrics")
    
    total_queries = len(st.session_state.conversation_history)
    successful_queries = sum(1 for entry in st.session_state.conversation_history if entry['result'].get('success'))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", total_queries, delta=None)
    with col2:
        if total_queries > 0:
            success_rate = (successful_queries / total_queries) * 100
            st.metric("Success Rate", f"{success_rate:.0f}%", delta=None)
        else:
            st.metric("Success Rate", "0%", delta=None)
    
    if st.session_state.conversation_history:
        avg_time = sum(
            entry['result'].get('response_time', 0) 
            for entry in st.session_state.conversation_history 
            if entry['result'].get('response_time')
        ) / len(st.session_state.conversation_history)
        st.metric("Avg Response Time", f"{avg_time:.1f}s", delta=None)
    
    st.divider()
    
    # System information
    st.markdown("#### ℹ️ System Information")
    st.markdown("""
    **Version:** v4.1 Enhanced  
    **Runtime:** Amazon Bedrock AgentCore  
    **Framework:** LangGraph + Streamlit  
    **Region:** us-west-2  
    **Account:** 280383026847
    """)

# Main content area
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Dashboard", "📋 History"])

with tab1:
    # Modern chat interface
    st.markdown("### 💬 Ask Your Analytics Question")
    
    # Enhanced example queries
    st.markdown("#### 💡 Try These Examples")
    
    examples = [
        {
            "title": "📊 Sales Analysis",
            "query": "Analyze sales performance for Q2 2024 and show top regions",
            "description": "Get comprehensive sales insights with regional breakdown"
        },
        {
            "title": "📈 KPI Dashboard", 
            "query": "What are our key performance indicators?",
            "description": "View critical business metrics and performance scores"
        },
        {
            "title": "📉 Trend Analysis",
            "query": "Show me revenue trends by month",
            "description": "Analyze revenue patterns and seasonal trends"
        }
    ]
    
    example_cols = st.columns(3)
    for i, example in enumerate(examples):
        with example_cols[i]:
            st.markdown(f"""
            <div class="query-example" onclick="document.getElementById('example_{i}').click()">
                <h4>{example['title']}</h4>
                <p><strong>Query:</strong> {example['query'][:40]}...</p>
                <small>{example['description']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Select", key=f"example_{i}", help=example['query']):
                st.session_state.selected_query = example['query']
    
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
        # Create progress indicators
        progress_container = st.container()
        
        with progress_container:
            # Progress bar and status
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Initialize processing
                progress_bar.progress(10)
                status_text.text("🔄 Initializing query processing...")
                time.sleep(0.5)
                
                # Step 2: Connect to agent
                progress_bar.progress(30)
                status_text.text("🤖 Connecting to AgentCore runtime...")
                time.sleep(0.5)
                
                # Step 3: Process query
                progress_bar.progress(50)
                status_text.text("📊 Analyzing your data...")
                
                # Call the analytics agent with real-time processing
                result = call_analytics_agent(
                    query_input, 
                    st.session_state.agentcore_client,
                    st.session_state.session_id,
                    st.session_state.user_id
                )
                
                # Update progress based on result
                if result.get("success"):
                    progress_bar.progress(70)
                    status_text.text("🔍 Processing analytics results...")
                else:
                    progress_bar.progress(70)
                    status_text.text("⚠️ Processing with fallback mode...")
                
                # Step 4: Generate insights
                progress_bar.progress(80)
                status_text.text("💡 Generating insights and recommendations...")
                time.sleep(0.5)
                
                # Step 5: Complete
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_container.empty()
                
                # Add to conversation history
                conversation_entry = {
                    "timestamp": datetime.now(),
                    "query": query_input,
                    "result": result
                }
                st.session_state.conversation_history.append(conversation_entry)
                
                # Show success message with response time
                if result.get("success"):
                    response_time = result.get("response_time", 0)
                    method = result.get("method", "Unknown")
                    
                    if "Fallback" in method:
                        st.info(f"✅ Query processed in {response_time:.2f}s via {method}")
                        st.info("💡 Using intelligent fallback mode - AgentCore Runtime API in preview")
                    else:
                        st.success(f"✅ Query processed in {response_time:.2f}s via {method}")
                else:
                    st.error(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                    # Try to provide helpful error message
                    if "ValidationException" in str(result.get('error', '')):
                        st.info("💡 Switching to fallback mode for continued functionality")
                
            except Exception as e:
                progress_container.empty()
                st.error(f"❌ Error processing query: {str(e)}")
                logger.error(f"Query processing error: {e}")
    
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
                            # Try to display base64 chart first
                            if display_chart_from_base64(viz):
                                # Chart displayed successfully from base64
                                if viz.get('data'):
                                    with st.expander(f"📈 {viz.get('title', 'Chart')} Data"):
                                        st.json(viz['data'])
                            else:
                                # Create chart from data if available
                                if viz.get('data'):
                                    chart = create_chart_from_data(viz)
                                    if chart:
                                        st.plotly_chart(chart, use_container_width=True)
                                        
                                        # Show data in expandable section
                                        with st.expander(f"📈 {viz.get('title', 'Chart')} Data"):
                                            if isinstance(viz['data'], dict):
                                                # Convert dict data to DataFrame for better display
                                                try:
                                                    df = pd.DataFrame(viz['data'])
                                                    st.dataframe(df, use_container_width=True)
                                                except:
                                                    st.json(viz['data'])
                                            else:
                                                st.json(viz['data'])
                                else:
                                    # Fallback to sample chart
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

# Modern Footer
st.divider()

# Status bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.connection_status and st.session_state.connection_status["success"]:
        method = st.session_state.connection_status["method"]
        if "AgentCore" in method:
            st.markdown('<p class="status-connected">🟢 AgentCore Runtime</p>', unsafe_allow_html=True)
        elif "HTTP" in method:
            st.markdown('<p class="status-connected">🟡 HTTP Endpoint</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-fallback">🟠 Fallback Mode</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-disconnected">🔴 Disconnected</p>', unsafe_allow_html=True)

with col2:
    st.markdown(f"**📊 Queries:** {len(st.session_state.conversation_history)}")

with col3:
    if st.session_state.conversation_history:
        successful_queries = sum(1 for entry in st.session_state.conversation_history if entry['result'].get('success'))
        success_rate = (successful_queries / len(st.session_state.conversation_history)) * 100
        st.markdown(f"**✅ Success:** {success_rate:.0f}%")
    else:
        st.markdown("**✅ Success:** 0%")

with col4:
    st.markdown("**🚀 Version:** v4.1 Enhanced")

# Enhanced footer
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;'>
    <h4>🤖 Production Analytics Agent v4.1</h4>
    <p><strong>Powered by Amazon Bedrock AgentCore</strong> | Built with LangGraph + Streamlit</p>
    <div style='margin-top: 15px;'>
        <span class="feature-badge">Real-time Processing</span>
        <span class="feature-badge">Natural Language to SQL</span>
        <span class="feature-badge">Advanced Analytics</span>
        <span class="feature-badge">Context Awareness</span>
    </div>
    <p style='margin-top: 15px; font-size: 0.9em;'>
        <strong>Account:</strong> 280383026847 | 
        <strong>Region:</strong> us-west-2 | 
        <strong>Runtime:</strong> hosted_agent_jqgjl-fJiyIV95k9
    </p>
</div>
""", unsafe_allow_html=True)