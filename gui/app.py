"""
Streamlit GUI for Production Analytics Agent
"""

import streamlit as st
import requests
import json
import boto3
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Analytics Agent",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("🤖 Production Analytics Agent")
st.markdown("Ask questions about your data in natural language")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Agent endpoint configuration
    agent_endpoint = st.text_input(
        "Agent Endpoint URL",
        placeholder="https://your-agent-endpoint.amazonaws.com",
        help="Enter your AgentCore endpoint URL"
    )
    
    # AWS region
    aws_region = st.selectbox(
        "AWS Region",
        ["us-west-2", "us-east-1", "eu-west-1"],
        index=0
    )
    
    st.divider()
    
    # Connection status
    if agent_endpoint:
        st.success("✅ Endpoint configured")
    else:
        st.warning("⚠️ Configure endpoint to start")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Ask Your Question")
    
    # Query input
    user_query = st.text_area(
        "Enter your analytics query:",
        placeholder="Example: Summarize sales by region for Q2 and show trends",
        height=100
    )
    
    # Submit button
    if st.button("🚀 Analyze", type="primary", disabled=not agent_endpoint):
        if user_query:
            with st.spinner("Processing your request..."):
                try:
                    # For now, simulate the response since we don't have the endpoint yet
                    # In production, this would call the actual AgentCore endpoint
                    
                    response_data = {
                        "message": f"Received query: {user_query}",
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "agent_version": "1.0.0"
                    }
                    
                    st.success("✅ Analysis complete!")
                    
                    # Display results
                    st.subheader("Results")
                    st.json(response_data)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("Please enter a query first")

with col2:
    st.header("Quick Examples")
    
    example_queries = [
        "Show sales trends by month",
        "Compare revenue across regions",
        "Analyze customer segments",
        "Plot quarterly performance",
        "Summarize key metrics"
    ]
    
    st.markdown("**Try these examples:**")
    for query in example_queries:
        if st.button(f"📝 {query}", key=query):
            st.session_state.example_query = query
            st.rerun()

# Handle example query selection
if hasattr(st.session_state, 'example_query'):
    user_query = st.session_state.example_query
    del st.session_state.example_query

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Powered by Amazon Bedrock AgentCore | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)