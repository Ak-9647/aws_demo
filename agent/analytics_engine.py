"""
Analytics Engine - Core data processing and analysis capabilities
"""

import boto3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """
    Core analytics engine for processing data and generating insights
    """
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.supported_formats = ['.csv', '.json', '.parquet', '.xlsx']
        
    def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point for analyzing user queries
        """
        try:
            logger.info(f"Analyzing query: {user_query}")
            
            # Parse the query to understand intent
            intent = self._parse_query_intent(user_query)
            logger.info(f"Detected intent: {intent}")
            
            # Try to use real data if available, otherwise use sample data
            result = self._analyze_with_real_data(user_query, intent)
            
            return {
                "success": True,
                "query": user_query,
                "intent": intent,
                "analysis": result["analysis"],
                "visualizations": result.get("visualizations", []),
                "data_summary": result.get("data_summary", {}),
                "recommendations": result.get("recommendations", []),
                "data_source": result.get("data_source", "sample")
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_query: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": user_query
            }
    
    def _analyze_with_real_data(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Try to analyze with real data from S3, fall back to sample data
        """
        try:
            # Try to load real data from S3
            bucket_name = "production-analytics-agent-agent-logs-839dae02"
            data_key = "data/sample_sales_data.csv"
            
            logger.info(f"Attempting to load real data from s3://{bucket_name}/{data_key}")
            df = self.read_s3_data(bucket_name, data_key)
            
            logger.info(f"Successfully loaded real data: {len(df)} rows, columns: {list(df.columns)}")
            
            # Analyze real data based on intent
            if intent["type"] == "sales_analysis":
                return self._analyze_real_sales_data(df, intent)
            else:
                # For other types, still use sample analysis but mention real data is available
                result = self._generate_sample_analysis(query, intent)
                result["data_source"] = "real_data_available"
                result["analysis"] = f"**Note: Real sales data detected in S3**\n\n{result['analysis']}"
                return result
                
        except Exception as e:
            logger.warning(f"Could not load real data, using sample data: {str(e)}")
            # Fall back to sample data
            result = self._generate_sample_analysis(query, intent)
            result["data_source"] = "sample"
            return result
    
    def _analyze_real_sales_data(self, df: pd.DataFrame, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze real sales data from S3
        """
        logger.info("Analyzing real sales data")
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.strftime('%B')
        
        # Filter by time period if specified
        if intent["time_period"] == "Q2":
            df = df[df['date'].dt.quarter == 2]
        
        # Perform analysis
        total_revenue = df['revenue'].sum()
        total_sales = df['sales_count'].sum()
        avg_profit_margin = df['profit_margin'].mean()
        
        # Top performing regions
        top_regions = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
        
        # Monthly trends
        monthly_revenue = df.groupby('month')['revenue'].sum().sort_index()
        
        # Product performance
        product_performance = df.groupby('product')['revenue'].sum().sort_values(ascending=False)
        
        analysis_text = f"""
## Real Sales Data Analysis - {intent.get('time_period', 'Full Period')}
*Based on actual data from S3*

### Key Findings:
- **Total Revenue**: ${total_revenue:,.2f}
- **Total Sales**: {total_sales:,} transactions
- **Average Profit Margin**: {avg_profit_margin:.1%}
- **Data Period**: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}

### Top Performing Regions:
"""
        
        for i, (region, revenue) in enumerate(top_regions.head(3).items(), 1):
            analysis_text += f"{i}. **{region}**: ${revenue:,.2f}\n"
        
        analysis_text += f"""
### Product Performance:
"""
        for product, revenue in product_performance.items():
            analysis_text += f"- **{product}**: ${revenue:,.2f}\n"
        
        analysis_text += f"""
### Monthly Revenue Trends:
"""
        for month, revenue in monthly_revenue.items():
            analysis_text += f"- **{month}**: ${revenue:,.2f}\n"
        
        # Calculate growth rate
        if len(monthly_revenue) > 1:
            growth_rate = ((monthly_revenue.iloc[-1] - monthly_revenue.iloc[0]) / monthly_revenue.iloc[0]) * 100
            trend_direction = "increasing" if growth_rate > 0 else "decreasing"
            analysis_text += f"""
### Growth Analysis:
- **Revenue Trend**: {trend_direction.title()} ({growth_rate:+.1f}%)
- **Best Month**: {monthly_revenue.idxmax()} (${monthly_revenue.max():,.2f})
- **Lowest Month**: {monthly_revenue.idxmin()} (${monthly_revenue.min():,.2f})
"""
        
        # Generate automated insights
        automated_insights = self._generate_insights(df, "sales_analysis")
        
        analysis_text += f"""
### Automated Insights:
"""
        for insight in automated_insights:
            analysis_text += f"- {insight}\n"
        
        analysis_text += f"""
### Recommendations:
- Focus marketing efforts on {top_regions.index[0]} region
- {product_performance.index[0]} is the top-performing product
- {"Continue growth momentum" if growth_rate > 0 else "Address declining trend"}
- Optimize profit margins across all regions
        """
        
        # Generate visualizations
        visualizations = []
        
        # Revenue by region chart
        revenue_chart = self._create_revenue_chart(df)
        visualizations.append(revenue_chart)
        
        # Trend chart if we have time data
        if len(monthly_revenue) > 1:
            trend_chart = self._create_trend_chart(df)
            visualizations.append(trend_chart)
        
        # Profit margin chart
        profit_chart = self._create_profit_margin_chart(df)
        visualizations.append(profit_chart)
        
        # Time series forecasting
        forecast_results = self._perform_time_series_forecast(df, 'revenue', 5)
        if 'error' not in forecast_results:
            forecast_chart = self._create_forecast_chart(forecast_results)
            visualizations.append(forecast_chart)
        
        # Clustering analysis
        clustering_results = self._perform_clustering_analysis(df)
        
        # Statistical analysis
        stats_results = self._perform_statistical_analysis(df)
        
        # Anomaly detection on revenue
        anomalies = self._detect_anomalies(df, 'revenue')
        
        return {
            "analysis": analysis_text.strip(),
            "data_source": "real_s3_data",
            "visualizations": visualizations,
            "statistical_analysis": stats_results,
            "anomaly_detection": anomalies,
            "time_series_forecast": forecast_results,
            "clustering_analysis": clustering_results,
            "automated_insights": automated_insights,
            "data_summary": {
                "total_revenue": float(total_revenue),
                "total_sales": int(total_sales),
                "avg_profit_margin": float(avg_profit_margin),
                "top_region": top_regions.index[0],
                "top_product": product_performance.index[0],
                "data_rows": len(df),
                "date_range": f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
            },
            "recommendations": [
                f"Increase investment in {top_regions.index[0]} region",
                f"Leverage success of {product_performance.index[0]}",
                "Implement profit margin optimization strategy",
                "Monitor monthly performance trends"
            ]
        }

    def _parse_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Parse user query to understand what they want to analyze
        """
        query_lower = query.lower()
        
        intent = {
            "type": "general",
            "metrics": [],
            "time_period": None,
            "grouping": [],
            "visualization": "auto"
        }
        
        # Detect analysis type
        if any(word in query_lower for word in ["sales", "revenue", "profit", "income"]):
            intent["type"] = "sales_analysis"
            intent["metrics"] = ["revenue", "sales_count", "profit_margin"]
            
        elif any(word in query_lower for word in ["performance", "kpi", "metrics"]):
            intent["type"] = "performance_analysis"
            intent["metrics"] = ["performance_score", "efficiency", "growth_rate"]
            
        elif any(word in query_lower for word in ["trend", "time", "over time", "monthly", "quarterly"]):
            intent["type"] = "trend_analysis"
            intent["visualization"] = "line_chart"
            
        elif any(word in query_lower for word in ["top", "best", "highest", "ranking"]):
            intent["type"] = "ranking_analysis"
            intent["visualization"] = "bar_chart"
            
        elif any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            intent["type"] = "comparison_analysis"
            intent["visualization"] = "comparison_chart"
        
        # Detect time periods
        if "q1" in query_lower or "quarter 1" in query_lower:
            intent["time_period"] = "Q1"
        elif "q2" in query_lower or "quarter 2" in query_lower:
            intent["time_period"] = "Q2"
        elif "q3" in query_lower or "quarter 3" in query_lower:
            intent["time_period"] = "Q3"
        elif "q4" in query_lower or "quarter 4" in query_lower:
            intent["time_period"] = "Q4"
        elif "2024" in query_lower:
            intent["time_period"] = "2024"
        elif "2023" in query_lower:
            intent["time_period"] = "2023"
        
        # Detect grouping
        if "region" in query_lower:
            intent["grouping"].append("region")
        if "product" in query_lower:
            intent["grouping"].append("product")
        if "category" in query_lower:
            intent["grouping"].append("category")
        if "month" in query_lower:
            intent["grouping"].append("month")
        
        return intent
    
    def _generate_sample_analysis(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate sample analysis based on query intent
        This simulates real data analysis - in production would use actual data
        """
        
        if intent["type"] == "sales_analysis":
            return self._generate_sales_analysis(intent)
        elif intent["type"] == "performance_analysis":
            return self._generate_performance_analysis(intent)
        elif intent["type"] == "trend_analysis":
            return self._generate_trend_analysis(intent)
        elif intent["type"] == "ranking_analysis":
            return self._generate_ranking_analysis(intent)
        elif intent["type"] == "comparison_analysis":
            return self._generate_comparison_analysis(intent)
        else:
            return self._generate_general_analysis(query, intent)
    
    def _generate_sales_analysis(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample sales analysis"""
        
        # Create sample sales data
        regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        
        data = []
        for region in regions:
            for month in months:
                revenue = np.random.normal(100000, 20000)
                sales_count = np.random.poisson(150)
                data.append({
                    "region": region,
                    "month": month,
                    "revenue": max(revenue, 50000),
                    "sales_count": sales_count,
                    "profit_margin": np.random.uniform(0.15, 0.35)
                })
        
        df = pd.DataFrame(data)
        
        # Perform analysis
        if intent["time_period"] == "Q2":
            df = df[df["month"].isin(["Apr", "May", "Jun"])]
        
        # Top performing regions
        top_regions = df.groupby("region")["revenue"].sum().sort_values(ascending=False).head(3)
        
        analysis_text = f"""
## Sales Performance Analysis - {intent.get('time_period', 'Full Period')}

### Key Findings:
- **Total Revenue**: ${df['revenue'].sum():,.2f}
- **Total Sales**: {df['sales_count'].sum():,} transactions
- **Average Profit Margin**: {df['profit_margin'].mean():.1%}

### Top 3 Performing Regions:
1. **{top_regions.index[0]}**: ${top_regions.iloc[0]:,.2f}
2. **{top_regions.index[1]}**: ${top_regions.iloc[1]:,.2f}
3. **{top_regions.index[2]}**: ${top_regions.iloc[2]:,.2f}

### Revenue Trends:
{self._analyze_trends(df)}

### Recommendations:
- Focus marketing efforts on {top_regions.index[0]} region
- Investigate growth opportunities in {top_regions.index[-1]} region
- Optimize profit margins across all regions
        """
        
        # Generate visualization
        viz_data = self._create_revenue_chart(df)
        
        # Generate additional visualizations
        visualizations = [viz_data]
        
        # Add trend chart if we have time data
        if 'month' in df.columns:
            trend_chart = self._create_trend_chart(df)
            visualizations.append(trend_chart)
        
        # Add profit margin chart
        profit_chart = self._create_profit_margin_chart(df)
        visualizations.append(profit_chart)
        
        return {
            "analysis": analysis_text.strip(),
            "visualizations": visualizations,
            "data_summary": {
                "total_revenue": float(df['revenue'].sum()),
                "total_sales": int(df['sales_count'].sum()),
                "avg_profit_margin": float(df['profit_margin'].mean()),
                "top_region": top_regions.index[0]
            },
            "recommendations": [
                f"Increase investment in {top_regions.index[0]} region",
                "Implement profit margin optimization strategy",
                "Develop growth plan for underperforming regions"
            ]
        }
    
    def _generate_performance_analysis(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample performance analysis"""
        
        metrics = {
            "Customer Satisfaction": 87.5,
            "Sales Growth": 12.3,
            "Market Share": 23.8,
            "Operational Efficiency": 91.2,
            "Employee Productivity": 78.9
        }
        
        analysis_text = f"""
## Performance Analysis Dashboard

### Key Performance Indicators:
"""
        
        for metric, value in metrics.items():
            status = "🟢 Excellent" if value > 85 else "🟡 Good" if value > 70 else "🔴 Needs Improvement"
            analysis_text += f"- **{metric}**: {value}% {status}\n"
        
        analysis_text += f"""
### Performance Summary:
- **Overall Score**: {np.mean(list(metrics.values())):.1f}/100
- **Strongest Area**: {max(metrics, key=metrics.get)} ({max(metrics.values()):.1f}%)
- **Improvement Area**: {min(metrics, key=metrics.get)} ({min(metrics.values()):.1f}%)

### Insights:
- Performance is strong across most metrics
- Focus needed on {min(metrics, key=metrics.get).lower()}
- Maintain excellence in {max(metrics, key=metrics.get).lower()}
        """
        
        # Generate radar chart for performance metrics
        radar_chart = self._create_performance_radar_chart(metrics)
        
        return {
            "analysis": analysis_text.strip(),
            "visualizations": [radar_chart],
            "data_summary": metrics,
            "recommendations": [
                f"Prioritize improvement in {min(metrics, key=metrics.get)}",
                f"Leverage strengths in {max(metrics, key=metrics.get)}",
                "Implement regular performance monitoring"
            ]
        }
    
    def _generate_trend_analysis(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample trend analysis"""
        
        # Generate time series data
        dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')
        values = np.cumsum(np.random.randn(len(dates))) + 100
        
        df = pd.DataFrame({
            'date': dates,
            'value': values,
            'month': dates.strftime('%B')
        })
        
        # Calculate trends
        monthly_avg = df.groupby('month')['value'].mean()
        trend_direction = "upward" if values[-1] > values[0] else "downward"
        trend_strength = abs(values[-1] - values[0]) / values[0] * 100
        
        analysis_text = f"""
## Trend Analysis - {intent.get('time_period', '2024')}

### Trend Overview:
- **Direction**: {trend_direction.title()} trend
- **Strength**: {trend_strength:.1f}% change over period
- **Current Value**: {values[-1]:.2f}
- **Starting Value**: {values[0]:.2f}

### Monthly Averages:
"""
        
        for month, avg in monthly_avg.items():
            analysis_text += f"- **{month}**: {avg:.2f}\n"
        
        analysis_text += f"""
### Key Insights:
- {'Strong positive momentum' if trend_direction == 'upward' else 'Declining trend requires attention'}
- Peak performance in {monthly_avg.idxmax()}
- Lowest performance in {monthly_avg.idxmin()}
        """
        
        return {
            "analysis": analysis_text.strip(),
            "data_summary": {
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "current_value": float(values[-1]),
                "peak_month": monthly_avg.idxmax()
            }
        }
    
    def _generate_ranking_analysis(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample ranking analysis"""
        
        items = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        scores = sorted(np.random.uniform(60, 95, len(items)), reverse=True)
        
        ranking_data = list(zip(items, scores))
        
        analysis_text = f"""
## Top Performers Ranking

### Rankings:
"""
        
        for i, (item, score) in enumerate(ranking_data, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            analysis_text += f"{medal} **{item}**: {score:.1f} points\n"
        
        analysis_text += f"""
### Analysis:
- **Top Performer**: {ranking_data[0][0]} with {ranking_data[0][1]:.1f} points
- **Performance Gap**: {ranking_data[0][1] - ranking_data[-1][1]:.1f} points between top and bottom
- **Average Score**: {np.mean(scores):.1f} points

### Recommendations:
- Replicate success factors from {ranking_data[0][0]}
- Provide additional support to lower-ranked items
- Set performance improvement targets
        """
        
        return {
            "analysis": analysis_text.strip(),
            "data_summary": {
                "top_performer": ranking_data[0][0],
                "top_score": ranking_data[0][1],
                "average_score": float(np.mean(scores)),
                "performance_gap": ranking_data[0][1] - ranking_data[-1][1]
            }
        }
    
    def _generate_comparison_analysis(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample comparison analysis"""
        
        categories = ["Category A", "Category B"]
        metrics = ["Revenue", "Growth Rate", "Market Share", "Customer Satisfaction"]
        
        comparison_data = {}
        for category in categories:
            comparison_data[category] = {
                metric: np.random.uniform(50, 100) for metric in metrics
            }
        
        analysis_text = f"""
## Comparison Analysis

### Side-by-Side Comparison:
"""
        
        for metric in metrics:
            cat_a_val = comparison_data["Category A"][metric]
            cat_b_val = comparison_data["Category B"][metric]
            winner = "Category A" if cat_a_val > cat_b_val else "Category B"
            
            analysis_text += f"""
**{metric}:**
- Category A: {cat_a_val:.1f}
- Category B: {cat_b_val:.1f}
- Winner: {winner} 🏆
"""
        
        # Overall winner
        a_total = sum(comparison_data["Category A"].values())
        b_total = sum(comparison_data["Category B"].values())
        overall_winner = "Category A" if a_total > b_total else "Category B"
        
        analysis_text += f"""
### Overall Performance:
- **Category A Total**: {a_total:.1f} points
- **Category B Total**: {b_total:.1f} points
- **Overall Winner**: {overall_winner} 🏆

### Key Insights:
- {overall_winner} shows superior overall performance
- Both categories have strengths in different areas
- Consider best practices sharing between categories
        """
        
        return {
            "analysis": analysis_text.strip(),
            "data_summary": {
                "category_a_total": a_total,
                "category_b_total": b_total,
                "overall_winner": overall_winner,
                "comparison_data": comparison_data
            }
        }
    
    def _generate_general_analysis(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general analysis for unspecified queries"""
        
        analysis_text = f"""
## Analytics Response

I've analyzed your query: "{query}"

### Available Analytics Capabilities:
- **Sales Analysis**: Revenue trends, regional performance, profit margins
- **Performance Analysis**: KPI tracking, efficiency metrics, growth rates
- **Trend Analysis**: Time-series analysis, forecasting, pattern detection
- **Ranking Analysis**: Top performers, comparative rankings, benchmarking
- **Comparison Analysis**: Side-by-side comparisons, competitive analysis

### Sample Data Sources I Can Analyze:
- CSV files from S3 buckets
- JSON data exports
- Excel spreadsheets
- Parquet files for large datasets

### To Get Started:
1. Upload your data to the configured S3 bucket
2. Ask specific questions like:
   - "Show me sales trends for Q2 2024"
   - "Which regions are performing best?"
   - "Compare product performance across categories"
   - "What are the key performance indicators?"

### Next Steps:
Please provide more specific details about what you'd like to analyze, or upload data files for me to process.
        """
        
        return {
            "analysis": analysis_text.strip(),
            "data_summary": {
                "query_type": "general_inquiry",
                "capabilities_shown": True
            },
            "recommendations": [
                "Specify the type of analysis you need",
                "Upload data files to S3 for processing",
                "Ask more targeted questions about your data"
            ]
        }
    
    def _analyze_trends(self, df: pd.DataFrame) -> str:
        """Analyze trends in the data"""
        if 'month' in df.columns and 'revenue' in df.columns:
            monthly_revenue = df.groupby('month')['revenue'].sum()
            trend = "increasing" if monthly_revenue.iloc[-1] > monthly_revenue.iloc[0] else "decreasing"
            return f"Revenue shows an {trend} trend over the analyzed period."
        return "Trend analysis requires time-series data."
    
    def _create_revenue_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a revenue chart visualization"""
        
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import seaborn as sns
            import io
            import base64
            
            # Set style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data
            chart_data = df.groupby('region')['revenue'].sum().sort_values(ascending=False)
            
            # Create bar chart
            bars = ax.bar(chart_data.index, chart_data.values)
            
            # Customize chart
            ax.set_title('Revenue by Region', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Region', fontsize=12)
            ax.set_ylabel('Revenue ($)', fontsize=12)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom', fontweight='bold')
            
            # Rotate x-axis labels if needed
            plt.xticks(rotation=45, ha='right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                "type": "bar_chart",
                "title": "Revenue by Region",
                "data": chart_data.to_dict(),
                "chart_image": chart_base64,
                "description": "Bar chart showing total revenue by region"
            }
            
        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            # Fallback to data only
            chart_data = df.groupby('region')['revenue'].sum().to_dict()
            return {
                "type": "bar_chart",
                "title": "Revenue by Region",
                "data": chart_data,
                "description": "Bar chart showing total revenue by region (chart generation failed)"
            }
    
    def read_s3_data(self, bucket: str, key: str) -> pd.DataFrame:
        """
        Read data from S3 bucket
        """
        try:
            logger.info(f"Reading data from s3://{bucket}/{key}")
            
            # Get file extension
            file_ext = key.lower().split('.')[-1]
            
            # Download file from S3
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read()
            
            # Parse based on file type
            if file_ext == 'csv':
                df = pd.read_csv(io.BytesIO(content))
            elif file_ext == 'json':
                df = pd.read_json(io.BytesIO(content))
            elif file_ext == 'parquet':
                df = pd.read_parquet(io.BytesIO(content))
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            logger.info(f"Successfully loaded {len(df)} rows from {key}")
            return df
            
        except Exception as e:
            logger.error(f"Error reading S3 data: {str(e)}", exc_info=True)
            raise
    
    def _create_trend_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a trend chart for time-series data"""
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import seaborn as sns
            import io
            import base64
            
            # Set style
            plt.style.use('seaborn-v0_8')
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Prepare data - group by month and sum revenue
            monthly_data = df.groupby('month')['revenue'].sum()
            
            # Create line chart
            ax.plot(monthly_data.index, monthly_data.values, marker='o', linewidth=3, markersize=8)
            
            # Customize chart
            ax.set_title('Revenue Trend Over Time', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Revenue ($)', fontsize=12)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add value labels on points
            for i, (month, value) in enumerate(monthly_data.items()):
                ax.annotate(f'${value:,.0f}', 
                           (i, value), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontweight='bold')
            
            # Add grid
            ax.grid(True, alpha=0.3)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                "type": "line_chart",
                "title": "Revenue Trend Over Time",
                "data": monthly_data.to_dict(),
                "chart_image": chart_base64,
                "description": "Line chart showing revenue trends by month"
            }
            
        except Exception as e:
            logger.error(f"Error creating trend chart: {str(e)}")
            return {
                "type": "line_chart",
                "title": "Revenue Trend Over Time",
                "data": {},
                "description": "Trend chart generation failed"
            }
    
    def _create_profit_margin_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a profit margin comparison chart"""
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import seaborn as sns
            import io
            import base64
            
            # Set style
            plt.style.use('seaborn-v0_8')
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data - average profit margin by region
            margin_data = df.groupby('region')['profit_margin'].mean().sort_values(ascending=True)
            
            # Create horizontal bar chart
            bars = ax.barh(margin_data.index, margin_data.values * 100)  # Convert to percentage
            
            # Color bars based on performance
            colors = ['red' if x < 0.2 else 'orange' if x < 0.25 else 'green' for x in margin_data.values]
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            # Customize chart
            ax.set_title('Profit Margin by Region', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Profit Margin (%)', fontsize=12)
            ax.set_ylabel('Region', fontsize=12)
            
            # Add value labels on bars
            for i, (region, value) in enumerate(margin_data.items()):
                ax.text(value * 100 + 0.5, i, f'{value:.1%}',
                       va='center', fontweight='bold')
            
            # Add target line at 25%
            ax.axvline(x=25, color='blue', linestyle='--', alpha=0.7, label='Target (25%)')
            ax.legend()
            
            # Set x-axis limits
            ax.set_xlim(0, max(margin_data.values * 100) + 5)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                "type": "horizontal_bar_chart",
                "title": "Profit Margin by Region",
                "data": {k: f"{v:.1%}" for k, v in margin_data.items()},
                "chart_image": chart_base64,
                "description": "Horizontal bar chart showing profit margins by region"
            }
            
        except Exception as e:
            logger.error(f"Error creating profit margin chart: {str(e)}")
            return {
                "type": "horizontal_bar_chart",
                "title": "Profit Margin by Region",
                "data": {},
                "description": "Profit margin chart generation failed"
            }
    
    def _create_performance_radar_chart(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Create a radar chart for performance metrics"""
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import numpy as np
            import io
            import base64
            
            # Set style
            plt.style.use('seaborn-v0_8')
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # Prepare data
            categories = list(metrics.keys())
            values = list(metrics.values())
            
            # Number of variables
            N = len(categories)
            
            # Compute angle for each axis
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Complete the circle
            
            # Add values
            values += values[:1]  # Complete the circle
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, label='Performance')
            ax.fill(angles, values, alpha=0.25)
            
            # Add category labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            
            # Set y-axis limits
            ax.set_ylim(0, 100)
            
            # Add grid lines for reference
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
            ax.grid(True)
            
            # Add title
            ax.set_title('Performance Metrics Radar Chart', size=16, fontweight='bold', pad=20)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                "type": "radar_chart",
                "title": "Performance Metrics Radar Chart",
                "data": metrics,
                "chart_image": chart_base64,
                "description": "Radar chart showing performance across multiple metrics"
            }
            
        except Exception as e:
            logger.error(f"Error creating radar chart: {str(e)}")
            return {
                "type": "radar_chart",
                "title": "Performance Metrics Radar Chart",
                "data": metrics,
                "description": "Radar chart generation failed"
            }
    
    def _perform_statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical analysis on the dataset"""
        
        try:
            import scipy.stats as stats
            
            # Get numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            statistical_results = {}
            
            for col in numeric_cols:
                data = df[col].dropna()
                
                statistical_results[col] = {
                    "mean": float(data.mean()),
                    "median": float(data.median()),
                    "std": float(data.std()),
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "skewness": float(stats.skew(data)),
                    "kurtosis": float(stats.kurtosis(data)),
                    "normality_test": {
                        "statistic": float(stats.normaltest(data)[0]),
                        "p_value": float(stats.normaltest(data)[1]),
                        "is_normal": stats.normaltest(data)[1] > 0.05
                    }
                }
            
            # Correlation analysis
            if len(numeric_cols) > 1:
                correlation_matrix = df[numeric_cols].corr()
                statistical_results["correlations"] = correlation_matrix.to_dict()
            
            return statistical_results
            
        except Exception as e:
            logger.error(f"Error in statistical analysis: {str(e)}")
            return {"error": "Statistical analysis failed"}
    
    def _detect_anomalies(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Detect anomalies in a numeric column using IQR method"""
        
        try:
            data = df[column].dropna()
            
            # Calculate IQR
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            # Define outlier bounds
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Find outliers
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            return {
                "column": column,
                "total_points": len(data),
                "outliers_count": len(outliers),
                "outlier_percentage": (len(outliers) / len(data)) * 100,
                "outlier_values": outliers.tolist(),
                "bounds": {
                    "lower": float(lower_bound),
                    "upper": float(upper_bound)
                },
                "quartiles": {
                    "Q1": float(Q1),
                    "Q2": float(data.median()),
                    "Q3": float(Q3)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {"error": "Anomaly detection failed"}
    
    def _generate_insights(self, df: pd.DataFrame, analysis_type: str) -> List[str]:
        """Generate automated insights based on data analysis"""
        
        insights = []
        
        try:
            # Revenue insights
            if 'revenue' in df.columns:
                total_revenue = df['revenue'].sum()
                avg_revenue = df['revenue'].mean()
                revenue_std = df['revenue'].std()
                
                if revenue_std / avg_revenue > 0.5:  # High variability
                    insights.append(f"Revenue shows high variability (CV: {revenue_std/avg_revenue:.1%}), indicating inconsistent performance")
                
                # Growth analysis if we have time data
                if 'month' in df.columns:
                    monthly_revenue = df.groupby('month')['revenue'].sum()
                    if len(monthly_revenue) > 1:
                        growth_rate = (monthly_revenue.iloc[-1] - monthly_revenue.iloc[0]) / monthly_revenue.iloc[0]
                        if growth_rate > 0.1:
                            insights.append(f"Strong revenue growth of {growth_rate:.1%} over the period")
                        elif growth_rate < -0.1:
                            insights.append(f"Revenue decline of {abs(growth_rate):.1%} requires immediate attention")
            
            # Regional insights
            if 'region' in df.columns and 'revenue' in df.columns:
                regional_performance = df.groupby('region')['revenue'].sum()
                top_region = regional_performance.idxmax()
                bottom_region = regional_performance.idxmin()
                performance_gap = (regional_performance.max() - regional_performance.min()) / regional_performance.mean()
                
                if performance_gap > 0.5:
                    insights.append(f"Significant performance gap between {top_region} and {bottom_region} regions")
            
            # Profit margin insights
            if 'profit_margin' in df.columns:
                avg_margin = df['profit_margin'].mean()
                if avg_margin < 0.2:
                    insights.append("Profit margins below 20% indicate potential pricing or cost issues")
                elif avg_margin > 0.3:
                    insights.append("Strong profit margins above 30% indicate healthy pricing strategy")
            
            # Seasonal patterns
            if 'month' in df.columns and len(df['month'].unique()) > 3:
                monthly_avg = df.groupby('month')['revenue'].mean() if 'revenue' in df.columns else None
                if monthly_avg is not None:
                    peak_month = monthly_avg.idxmax()
                    low_month = monthly_avg.idxmin()
                    insights.append(f"Seasonal pattern detected: Peak in {peak_month}, lowest in {low_month}")
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            insights.append("Automated insight generation encountered an error")
        
        return insights if insights else ["No significant patterns detected in the current dataset"]
    
    def _perform_time_series_forecast(self, df: pd.DataFrame, target_column: str = 'revenue', periods: int = 3) -> Dict[str, Any]:
        """Perform time series forecasting using simple exponential smoothing"""
        
        try:
            from scipy import optimize
            
            if 'date' not in df.columns:
                return {"error": "Date column required for time series forecasting"}
            
            # Prepare time series data
            df_ts = df.copy()
            df_ts['date'] = pd.to_datetime(df_ts['date'])
            df_ts = df_ts.sort_values('date')
            
            # Aggregate by date if multiple entries per date
            daily_data = df_ts.groupby('date')[target_column].sum()
            
            if len(daily_data) < 3:
                return {"error": "Insufficient data points for forecasting"}
            
            # Simple exponential smoothing
            alpha = 0.3  # Smoothing parameter
            forecast_values = []
            smoothed_values = [daily_data.iloc[0]]
            
            # Calculate smoothed values
            for i in range(1, len(daily_data)):
                smoothed = alpha * daily_data.iloc[i] + (1 - alpha) * smoothed_values[-1]
                smoothed_values.append(smoothed)
            
            # Generate forecasts
            last_smoothed = smoothed_values[-1]
            trend = (daily_data.iloc[-1] - daily_data.iloc[-3]) / 2  # Simple trend calculation
            
            for i in range(periods):
                forecast = last_smoothed + trend * (i + 1)
                forecast_values.append(max(forecast, 0))  # Ensure non-negative
            
            # Create forecast dates
            last_date = daily_data.index[-1]
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods, freq='D')
            
            return {
                "historical_data": {
                    "dates": [d.strftime('%Y-%m-%d') for d in daily_data.index],
                    "values": daily_data.tolist(),
                    "smoothed_values": smoothed_values
                },
                "forecast": {
                    "dates": [d.strftime('%Y-%m-%d') for d in forecast_dates],
                    "values": forecast_values,
                    "confidence_interval": {
                        "lower": [v * 0.8 for v in forecast_values],
                        "upper": [v * 1.2 for v in forecast_values]
                    }
                },
                "metrics": {
                    "alpha": alpha,
                    "trend": float(trend),
                    "last_value": float(daily_data.iloc[-1]),
                    "forecast_period": periods
                }
            }
            
        except Exception as e:
            logger.error(f"Error in time series forecasting: {str(e)}")
            return {"error": f"Time series forecasting failed: {str(e)}"}
    
    def _perform_clustering_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering analysis on numeric data"""
        
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            from sklearn.decomposition import PCA
            
            # Get numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) < 2:
                return {"error": "Insufficient numeric columns for clustering"}
            
            # Prepare data
            data = df[numeric_cols].dropna()
            
            if len(data) < 4:
                return {"error": "Insufficient data points for clustering"}
            
            # Standardize data
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(data)
            
            # Determine optimal number of clusters (2-5)
            max_clusters = min(5, len(data) - 1)
            inertias = []
            
            for k in range(2, max_clusters + 1):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(data_scaled)
                inertias.append(kmeans.inertia_)
            
            # Choose optimal k (simple elbow method)
            optimal_k = 2
            if len(inertias) > 1:
                # Find the point with maximum decrease in inertia
                decreases = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
                optimal_k = decreases.index(max(decreases)) + 2
            
            # Perform final clustering
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(data_scaled)
            
            # Add cluster labels to original data
            data_with_clusters = data.copy()
            data_with_clusters['cluster'] = cluster_labels
            
            # Analyze clusters
            cluster_analysis = {}
            for cluster_id in range(optimal_k):
                cluster_data = data_with_clusters[data_with_clusters['cluster'] == cluster_id]
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    "size": len(cluster_data),
                    "percentage": (len(cluster_data) / len(data)) * 100,
                    "characteristics": {
                        col: {
                            "mean": float(cluster_data[col].mean()),
                            "std": float(cluster_data[col].std()),
                            "min": float(cluster_data[col].min()),
                            "max": float(cluster_data[col].max())
                        } for col in numeric_cols
                    }
                }
            
            # PCA for visualization (if more than 2 dimensions)
            pca_data = None
            if len(numeric_cols) > 2:
                pca = PCA(n_components=2)
                pca_result = pca.fit_transform(data_scaled)
                pca_data = {
                    "x": pca_result[:, 0].tolist(),
                    "y": pca_result[:, 1].tolist(),
                    "clusters": cluster_labels.tolist(),
                    "explained_variance": pca.explained_variance_ratio_.tolist()
                }
            
            return {
                "optimal_clusters": optimal_k,
                "cluster_analysis": cluster_analysis,
                "pca_visualization": pca_data,
                "features_used": numeric_cols,
                "total_data_points": len(data)
            }
            
        except ImportError:
            return {"error": "Scikit-learn not available for clustering analysis"}
        except Exception as e:
            logger.error(f"Error in clustering analysis: {str(e)}")
            return {"error": f"Clustering analysis failed: {str(e)}"}
    
    def _create_forecast_chart(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a forecast visualization chart"""
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            import io
            import base64
            from datetime import datetime
            
            # Set style
            plt.style.use('seaborn-v0_8')
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Parse historical data
            hist_dates = [datetime.strptime(d, '%Y-%m-%d') for d in forecast_data['historical_data']['dates']]
            hist_values = forecast_data['historical_data']['values']
            smoothed_values = forecast_data['historical_data']['smoothed_values']
            
            # Parse forecast data
            forecast_dates = [datetime.strptime(d, '%Y-%m-%d') for d in forecast_data['forecast']['dates']]
            forecast_values = forecast_data['forecast']['values']
            lower_bound = forecast_data['forecast']['confidence_interval']['lower']
            upper_bound = forecast_data['forecast']['confidence_interval']['upper']
            
            # Plot historical data
            ax.plot(hist_dates, hist_values, 'o-', label='Historical Data', color='blue', linewidth=2)
            ax.plot(hist_dates, smoothed_values, '--', label='Smoothed Trend', color='green', alpha=0.7)
            
            # Plot forecast
            ax.plot(forecast_dates, forecast_values, 's-', label='Forecast', color='red', linewidth=2)
            
            # Plot confidence interval
            ax.fill_between(forecast_dates, lower_bound, upper_bound, alpha=0.3, color='red', label='Confidence Interval')
            
            # Customize chart
            ax.set_title('Time Series Forecast', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            
            # Format dates on x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(hist_dates) // 5)))
            plt.xticks(rotation=45)
            
            # Add legend and grid
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                "type": "forecast_chart",
                "title": "Time Series Forecast",
                "data": forecast_data,
                "chart_image": chart_base64,
                "description": "Time series forecast with confidence intervals"
            }
            
        except Exception as e:
            logger.error(f"Error creating forecast chart: {str(e)}")
            return {
                "type": "forecast_chart",
                "title": "Time Series Forecast",
                "data": forecast_data,
                "description": "Forecast chart generation failed"
            }