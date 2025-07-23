"""
LangGraph Workflow for Intelligent Analytics Processing
Multi-step reasoning with memory and context awareness
Integrated with AgentCore Memory, Identity, Gateways, and MCP tools
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
try:
    from langgraph.prebuilt import ToolExecutor
except ImportError:
    # Fallback for newer versions
    try:
        from langgraph.prebuilt.tool_executor import ToolExecutor
    except ImportError:
        # Create a simple tool executor if not available
        class ToolExecutor:
            def __init__(self, tools):
                self.tools = tools
            
            def invoke(self, tool_call):
                return {"result": "Tool execution simulated"}
from analytics_engine import AnalyticsEngine
from conversation_memory import ConversationMemory
from mcp_analytics_tools import MCPAnalyticsTools
from agentcore_integration import AgentCoreIntegration
from context_engineering import get_context_engine

logger = logging.getLogger(__name__)

class AnalyticsState(TypedDict):
    """State object for the analytics workflow"""
    query: str
    session_id: Optional[str]
    user_id: Optional[str]
    intent: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    completed_tasks: List[str]
    results: Dict[str, Any]
    context: Dict[str, Any]
    recommendations: List[str]
    error: Optional[str]

class AnalyticsWorkflow:
    """
    LangGraph workflow for intelligent analytics processing
    Enhanced with AgentCore Memory, Identity, Gateways, and MCP tools
    """
    
    def __init__(self):
        self.analytics_engine = AnalyticsEngine()
        self.memory = ConversationMemory()
        self.agentcore = AgentCoreIntegration()
        self.mcp_tools = MCPAnalyticsTools()
        self.context_engine = get_context_engine(self.memory)
        self.workflow = self._create_workflow()
        
        # Setup AgentCore integrations
        self.identity_config = self.agentcore.setup_identity_integration()
        self.gateway_config = self.agentcore.setup_gateway_integration()
        
        logger.info("Enhanced AnalyticsWorkflow initialized with AgentCore, MCP, and Advanced Context Engineering")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        workflow = StateGraph(AnalyticsState)
        
        # Add nodes
        workflow.add_node("query_analyzer", self._analyze_query)
        workflow.add_node("context_retriever", self._retrieve_context)
        workflow.add_node("task_decomposer", self._decompose_tasks)
        workflow.add_node("mcp_enhancer", self._enhance_with_mcp)
        workflow.add_node("data_processor", self._process_data)
        workflow.add_node("result_synthesizer", self._synthesize_results)
        workflow.add_node("memory_updater", self._update_memory)
        workflow.add_node("error_handler", self._handle_error)
        
        # Define the flow
        workflow.set_entry_point("query_analyzer")
        
        workflow.add_edge("query_analyzer", "context_retriever")
        workflow.add_edge("context_retriever", "task_decomposer")
        workflow.add_edge("task_decomposer", "mcp_enhancer")
        workflow.add_edge("mcp_enhancer", "data_processor")
        workflow.add_edge("data_processor", "result_synthesizer")
        workflow.add_edge("result_synthesizer", "memory_updater")
        workflow.add_edge("memory_updater", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "data_processor",
            self._should_handle_error,
            {
                "error": "error_handler",
                "continue": "result_synthesizer"
            }
        )
        
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    def _analyze_query(self, state: AnalyticsState) -> AnalyticsState:
        """Analyze the user query to understand intent with advanced context engineering"""
        try:
            logger.info(f"Analyzing query with advanced context engineering: {state['query']}")
            
            # Get conversation history for context
            conversation_history = []
            if state.get('session_id'):
                conversation_history = self.memory.get_conversation_history(
                    state['session_id'], limit=5
                )
            
            # Use advanced context engineering for comprehensive analysis
            context_analysis = self.context_engine.analyze_query_context(
                query=state['query'],
                session_id=state.get('session_id'),
                user_id=state.get('user_id'),
                conversation_history=conversation_history
            )
            
            # Extract intent from context analysis
            intent = context_analysis['query_intent']
            
            # Enhance with additional context information
            intent['semantic_context'] = context_analysis['semantic_context']
            intent['temporal_context'] = context_analysis['temporal_context']
            intent['domain_context'] = context_analysis['domain_context']
            intent['complexity_analysis'] = context_analysis['complexity_analysis']
            intent['requires_decomposition'] = context_analysis['complexity_analysis']['overall_complexity'] > 0.6
            
            # Store full context analysis
            state['intent'] = intent
            state['context'] = context_analysis
            
            logger.info(f"Advanced query analysis completed - Intent: {intent['primary_intent']}, Complexity: {intent['complexity_analysis']['complexity_level']}")
            
        except Exception as e:
            logger.error(f"Error in advanced query analysis: {str(e)}")
            # Fallback to basic analysis
            intent = self.analytics_engine._parse_query_intent(state['query'])
            complexity_score = self._assess_query_complexity(state['query'])
            intent['complexity'] = complexity_score
            intent['requires_decomposition'] = complexity_score > 3
            state['intent'] = intent
            state['error'] = f"Advanced analysis failed, using fallback: {str(e)}"
        
        return state
    
    def _retrieve_context(self, state: AnalyticsState) -> AnalyticsState:
        """Retrieve and enhance conversation context with advanced context engineering"""
        try:
            logger.info("Retrieving enhanced conversation context")
            
            # Context was already analyzed in _analyze_query, so we enhance it here
            existing_context = state.get('context', {})
            
            # Add memory-based context
            if state.get('session_id'):
                # Get conversation history
                history = self.memory.get_conversation_history(
                    state['session_id'], 
                    limit=10  # Get more history for better context
                )
                
                if history:
                    # Enhanced context extraction
                    existing_context['conversation_history'] = history
                    existing_context['conversation_summary'] = self._extract_enhanced_context_summary(history)
                    existing_context['related_queries'] = [h.get('query', '') for h in history[-5:]]
                    existing_context['conversation_patterns'] = self._analyze_conversation_patterns(history)
                
                # Get user preferences with enhanced analysis
                if state.get('user_id'):
                    preferences = self.memory.get_user_preferences(state['user_id'])
                    existing_context['user_preferences'] = preferences
                    
                    # Get user context from context engine
                    user_context = self.context_engine._get_user_context(state['user_id'])
                    existing_context['user_profile'] = user_context
            
            # Add contextual insights
            existing_context['contextual_insights'] = self._generate_contextual_insights(existing_context)
            
            state['context'] = existing_context
            logger.info("Enhanced context retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error retrieving enhanced context: {str(e)}")
            # Keep existing context if available, otherwise provide fallback
            if not state.get('context'):
                state['context'] = {
                    "previous_context": "Context retrieval failed.",
                    "user_preferences": {},
                    "related_queries": []
                }
        
        return state
    
    def _decompose_tasks(self, state: AnalyticsState) -> AnalyticsState:
        """Decompose complex queries into manageable tasks"""
        try:
            logger.info("Decomposing query into tasks")
            
            intent = state['intent']
            query = state['query']
            
            tasks = []
            
            # Basic task for all queries
            tasks.append({
                "id": "primary_analysis",
                "type": intent['type'],
                "description": f"Perform {intent['type']} on the data",
                "priority": 1,
                "dependencies": []
            })
            
            # Add additional tasks based on complexity and intent
            if intent.get('requires_decomposition', False):
                
                # Time-based analysis
                if intent.get('time_period'):
                    tasks.append({
                        "id": "time_filtering",
                        "type": "data_filtering",
                        "description": f"Filter data for {intent['time_period']}",
                        "priority": 0,
                        "dependencies": []
                    })
                
                # Grouping analysis
                if intent.get('grouping'):
                    for group in intent['grouping']:
                        tasks.append({
                            "id": f"group_by_{group}",
                            "type": "grouping_analysis",
                            "description": f"Group analysis by {group}",
                            "priority": 2,
                            "dependencies": ["primary_analysis"]
                        })
                
                # Visualization tasks
                if intent.get('visualization') != 'auto':
                    tasks.append({
                        "id": "visualization",
                        "type": "chart_generation",
                        "description": f"Generate {intent['visualization']}",
                        "priority": 3,
                        "dependencies": ["primary_analysis"]
                    })
                
                # Advanced analytics
                if any(word in query.lower() for word in ["forecast", "predict", "trend"]):
                    tasks.append({
                        "id": "forecasting",
                        "type": "time_series_forecast",
                        "description": "Generate forecasts and predictions",
                        "priority": 3,
                        "dependencies": ["primary_analysis"]
                    })
                
                if any(word in query.lower() for word in ["anomaly", "outlier", "unusual"]):
                    tasks.append({
                        "id": "anomaly_detection",
                        "type": "anomaly_analysis",
                        "description": "Detect anomalies and outliers",
                        "priority": 2,
                        "dependencies": ["primary_analysis"]
                    })
            
            # Sort tasks by priority
            tasks.sort(key=lambda x: x['priority'])
            
            state['tasks'] = tasks
            state['completed_tasks'] = []
            
            logger.info(f"Query decomposed into {len(tasks)} tasks")
            
        except Exception as e:
            logger.error(f"Error in task decomposition: {str(e)}")
            state['error'] = f"Task decomposition failed: {str(e)}"
        
        return state
    
    def _enhance_with_mcp(self, state: AnalyticsState) -> AnalyticsState:
        """Enhance query processing with MCP tools"""
        try:
            logger.info("Enhancing query with MCP tools")
            
            query = state['query']
            intent = state['intent']
            tasks = state.get('tasks', [])
            
            mcp_enhancements = []
            
            # For now, we'll add simulated MCP enhancements based on query analysis
            # In production, this would call actual MCP servers
            
            # AWS documentation for AWS-related queries
            if any(aws_term in query.lower() for aws_term in ['aws', 'amazon', 's3', 'ec2', 'lambda', 'dynamodb', 'redshift', 'athena']):
                logger.info("Query contains AWS terms, adding AWS documentation enhancement")
                mcp_enhancements.append({
                    'tool': 'aws-docs',
                    'result': {
                        'success': True,
                        'documentation': f'AWS documentation context for: {query}',
                        'relevant_services': ['S3', 'DynamoDB', 'Lambda'],
                        'best_practices': ['Use IAM roles', 'Enable encryption', 'Monitor costs']
                    },
                    'relevance': 'high'
                })
            
            # Advanced data analysis for complex analytical queries
            if any(analysis_term in query.lower() for analysis_term in ['analyze', 'statistics', 'correlation', 'regression', 'forecast']):
                logger.info("Query requires advanced analysis, adding data analysis enhancement")
                mcp_enhancements.append({
                    'tool': 'data-analysis',
                    'result': {
                        'success': True,
                        'analysis_type': intent.get('type', 'comprehensive'),
                        'recommended_methods': ['statistical_analysis', 'correlation_matrix', 'trend_analysis'],
                        'data_quality_checks': ['missing_values', 'outliers', 'data_types']
                    },
                    'relevance': 'high'
                })
            
            # Visualization enhancement for chart-related queries
            if any(viz_term in query.lower() for viz_term in ['chart', 'graph', 'plot', 'visualize', 'dashboard']):
                logger.info("Query requires visualization, adding visualization enhancement")
                mcp_enhancements.append({
                    'tool': 'visualization',
                    'result': {
                        'success': True,
                        'chart_type': intent.get('visualization', 'auto'),
                        'recommended_charts': ['line', 'bar', 'scatter', 'heatmap'],
                        'design_principles': ['clear_labels', 'appropriate_colors', 'readable_fonts']
                    },
                    'relevance': 'medium'
                })
            
            # Database queries for data warehouse operations
            if any(db_term in query.lower() for db_term in ['database', 'sql', 'table', 'warehouse', 'query']):
                logger.info("Query involves database operations, adding database enhancement")
                mcp_enhancements.append({
                    'tool': 'database',
                    'result': {
                        'success': True,
                        'query_optimization': ['use_indexes', 'limit_results', 'avoid_wildcards'],
                        'available_tables': ['sales_data', 'customer_data', 'product_data'],
                        'performance_tips': ['Use EXPLAIN', 'Consider partitioning', 'Monitor query time']
                    },
                    'relevance': 'high'
                })
            
            # Store MCP enhancements in state
            if mcp_enhancements:
                state['mcp_enhancements'] = mcp_enhancements
                logger.info(f"Added {len(mcp_enhancements)} MCP enhancements")
                
                # Add MCP-enhanced recommendations
                mcp_recommendations = []
                for enhancement in mcp_enhancements:
                    if enhancement['relevance'] == 'high':
                        result = enhancement['result']
                        if 'best_practices' in result:
                            mcp_recommendations.extend(result['best_practices'])
                        if 'recommended_methods' in result:
                            mcp_recommendations.extend([f"Consider using {method}" for method in result['recommended_methods']])
                        if 'query_optimization' in result:
                            mcp_recommendations.extend([f"Optimize with: {tip}" for tip in result['query_optimization']])
                
                # Add to existing recommendations
                current_recommendations = state.get('recommendations', [])
                current_recommendations.extend(mcp_recommendations)
                state['recommendations'] = current_recommendations
                
            else:
                logger.info("No relevant MCP enhancements found for this query")
            
        except Exception as e:
            logger.error(f"Error in MCP enhancement: {str(e)}")
            # Don't fail the entire workflow for MCP errors
            state['mcp_error'] = f"MCP enhancement failed: {str(e)}"
        
        return state
    
    def _process_data(self, state: AnalyticsState) -> AnalyticsState:
        """Process data according to the decomposed tasks"""
        try:
            logger.info("Processing data with analytics engine")
            
            # Use the analytics engine to process the query
            result = self.analytics_engine.analyze_query(state['query'])
            
            if result['success']:
                state['results'] = result
                
                # Mark tasks as completed based on what was actually done
                completed = []
                
                if result.get('analysis'):
                    completed.append('primary_analysis')
                
                if result.get('visualizations'):
                    completed.append('visualization')
                
                if result.get('time_series_forecast'):
                    completed.append('forecasting')
                
                if result.get('anomaly_detection'):
                    completed.append('anomaly_detection')
                
                if result.get('clustering_analysis'):
                    completed.append('clustering_analysis')
                
                state['completed_tasks'] = completed
                
                logger.info(f"Data processing completed. Tasks done: {completed}")
                
            else:
                state['error'] = result.get('error', 'Data processing failed')
                logger.error(f"Analytics engine error: {state['error']}")
        
        except Exception as e:
            logger.error(f"Error in data processing: {str(e)}")
            state['error'] = f"Data processing failed: {str(e)}"
        
        return state
    
    def _synthesize_results(self, state: AnalyticsState) -> AnalyticsState:
        """Synthesize results and generate intelligent recommendations with advanced context awareness"""
        try:
            logger.info("Synthesizing results with advanced context awareness")
            
            results = state.get('results', {})
            context = state.get('context', {})
            intent = state.get('intent', {})
            
            # Generate context-aware recommendations
            recommendations = []
            
            # Base recommendations from analytics engine
            if results.get('recommendations'):
                recommendations.extend(results['recommendations'])
            
            # Add contextual recommendations from context engineering
            contextual_recs = context.get('contextual_recommendations', [])
            recommendations.extend(contextual_recs)
            
            # Add conversation continuity recommendations
            conversation_summary = context.get('conversation_summary', '')
            if 'focusing on' in conversation_summary:
                recommendations.append(
                    "Building on your ongoing analysis, consider exploring related dimensions or time periods"
                )
            
            # Add user expertise-based recommendations
            user_profile = context.get('user_profile', {})
            expertise_level = user_profile.get('expertise_level', 'intermediate')
            
            if expertise_level == 'beginner':
                recommendations.extend([
                    "Start with summary statistics to understand your data better",
                    "Consider visualizing key metrics before diving into complex analysis"
                ])
            elif expertise_level == 'advanced':
                recommendations.extend([
                    "Consider advanced statistical methods or machine learning approaches",
                    "Explore multivariate analysis for deeper insights"
                ])
            
            # Add domain-specific intelligent recommendations
            domain_context = intent.get('domain_context', {})
            primary_domain = domain_context.get('primary_domain', 'general')
            
            if primary_domain == 'sales':
                recommendations.extend([
                    "Analyze customer lifetime value and retention patterns",
                    "Segment customers by behavior for targeted strategies",
                    "Compare performance across different sales channels"
                ])
            elif primary_domain == 'marketing':
                recommendations.extend([
                    "Evaluate campaign ROI and attribution models",
                    "Analyze customer acquisition cost trends",
                    "Study conversion funnel optimization opportunities"
                ])
            elif primary_domain == 'finance':
                recommendations.extend([
                    "Include variance analysis and budget comparisons",
                    "Analyze cash flow patterns and seasonality",
                    "Consider risk assessment and scenario planning"
                ])
            
            # Add complexity-based recommendations
            complexity_analysis = intent.get('complexity_analysis', {})
            complexity_level = complexity_analysis.get('complexity_level', 'moderate')
            
            if complexity_level == 'very_complex':
                recommendations.append(
                    "Consider breaking this complex analysis into focused sub-analyses for clearer insights"
                )
            elif complexity_level == 'simple':
                recommendations.append(
                    "You might want to explore additional dimensions or drill deeper into specific areas"
                )
            
            # Add pattern-based recommendations
            pattern_matches = context.get('pattern_matches', [])
            for pattern in pattern_matches:
                if pattern.get('similarity', 0) > 0.8:
                    pattern_recs = pattern.get('recommendations', [])
                    recommendations.extend(pattern_recs[:2])  # Add top 2 from each pattern
            
            # Add temporal context recommendations
            temporal_context = intent.get('temporal_context', {})
            if temporal_context.get('requires_time_series'):
                recommendations.extend([
                    "Consider seasonal decomposition to understand underlying patterns",
                    "Add confidence intervals to your forecasts for better decision making"
                ])
            
            # Add contextual insights as recommendations
            contextual_insights = context.get('contextual_insights', [])
            for insight in contextual_insights:
                if 'prioritize' in insight or 'focus' in insight:
                    recommendations.append(f"Insight: {insight}")
            
            # Remove duplicates and prioritize
            unique_recommendations = []
            seen = set()
            for rec in recommendations:
                if rec not in seen and len(rec) > 10:  # Filter out very short recommendations
                    unique_recommendations.append(rec)
                    seen.add(rec)
            
            # Limit and prioritize recommendations
            state['recommendations'] = unique_recommendations[:7]  # Increased to 7 for richer context
            
            # Add synthesis metadata
            state['synthesis_metadata'] = {
                'context_sources_used': len([k for k in context.keys() if context[k]]),
                'recommendation_sources': ['analytics_engine', 'context_engineering', 'domain_knowledge', 'user_profile'],
                'complexity_level': complexity_level,
                'expertise_level': expertise_level,
                'primary_domain': primary_domain
            }
            
            logger.info(f"Generated {len(state['recommendations'])} context-aware recommendations from {len(recommendations)} total suggestions")
            
        except Exception as e:
            logger.error(f"Error in advanced result synthesis: {str(e)}")
            state['recommendations'] = [
                "Unable to generate context-aware recommendations due to processing error",
                "Try rephrasing your question or contact support if the issue persists"
            ]
        
        return state
    
    def _update_memory(self, state: AnalyticsState) -> AnalyticsState:
        """Update conversation memory and user preferences with context learning"""
        try:
            logger.info("Updating conversation memory with context learning")
            
            if state.get('session_id'):
                # Store conversation with enhanced context
                conversation_data = {
                    'query': state['query'],
                    'response': state.get('results', {}),
                    'intent': state.get('intent', {}),
                    'recommendations': state.get('recommendations', []),
                    'context_analysis': state.get('context', {}),
                    'synthesis_metadata': state.get('synthesis_metadata', {}),
                    'timestamp': int(time.time())
                }
                
                self.memory.store_conversation(
                    session_id=state['session_id'],
                    user_id=state.get('user_id'),
                    **conversation_data
                )
                
                # Update user preferences with enhanced data
                if state.get('user_id'):
                    intent = state.get('intent', {})
                    complexity_analysis = intent.get('complexity_analysis', {})
                    domain_context = intent.get('domain_context', {})
                    
                    interaction_data = {
                        'query_type': intent.get('primary_intent', 'unknown'),
                        'complexity': complexity_analysis.get('overall_complexity', 0.5),
                        'complexity_level': complexity_analysis.get('complexity_level', 'moderate'),
                        'domain': domain_context.get('primary_domain', 'general'),
                        'semantic_richness': intent.get('semantic_context', {}).get('richness_score', 0.1),
                        'timestamp': int(time.time())
                    }
                    
                    self.memory.update_user_preferences(
                        user_id=state['user_id'],
                        interaction_data=interaction_data
                    )
                
                # Use context engineering to learn from this interaction
                results = state.get('results', {})
                if results.get('success', False):
                    self.context_engine.learn_from_interaction(
                        query=state['query'],
                        response=results,
                        user_feedback=None,  # Could be added later
                        session_id=state['session_id'],
                        user_id=state.get('user_id')
                    )
                
                logger.info("Enhanced memory and context learning updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating enhanced memory: {str(e)}")
            # Don't fail the entire workflow for memory errors
        
        return state
    
    def _handle_error(self, state: AnalyticsState) -> AnalyticsState:
        """Handle errors gracefully"""
        logger.error(f"Handling workflow error: {state.get('error')}")
        
        # Provide fallback response
        state['results'] = {
            'success': False,
            'analysis': f"I encountered an issue processing your query: {state.get('error', 'Unknown error')}. Please try rephrasing your question or contact support if the issue persists.",
            'error': state.get('error')
        }
        
        state['recommendations'] = [
            "Try rephrasing your question with more specific terms",
            "Check if your data source is accessible",
            "Contact support if the issue continues"
        ]
        
        return state
    
    def _should_handle_error(self, state: AnalyticsState) -> str:
        """Determine if we should handle an error"""
        return "error" if state.get('error') else "continue"
    
    def _assess_query_complexity(self, query: str) -> int:
        """Assess query complexity on a scale of 1-5"""
        complexity = 1
        query_lower = query.lower()
        
        # Check for multiple analysis types
        analysis_types = ['sales', 'performance', 'trend', 'ranking', 'comparison']
        complexity += sum(1 for t in analysis_types if t in query_lower)
        
        # Check for time periods
        if any(period in query_lower for period in ['q1', 'q2', 'q3', 'q4', 'quarter', 'month', 'year']):
            complexity += 1
        
        # Check for grouping requirements
        if any(group in query_lower for group in ['by region', 'by product', 'by category']):
            complexity += 1
        
        # Check for advanced analytics
        if any(advanced in query_lower for advanced in ['forecast', 'predict', 'anomaly', 'cluster']):
            complexity += 1
        
        # Check for multiple questions
        complexity += query.count('?') - 1 if query.count('?') > 1 else 0
        complexity += query.count(' and ') 
        
        return min(complexity, 5)
    
    def _extract_context_summary(self, history: List[Dict]) -> str:
        """Extract a summary from conversation history"""
        if not history:
            return "No previous conversation context."
        
        recent_queries = [h.get('query', '') for h in history[-2:]]
        if recent_queries:
            return f"Previously discussed: {', '.join(recent_queries[:2])}"
        
        return "Previous conversation available but no clear context extracted."
    
    def _extract_enhanced_context_summary(self, history: List[Dict]) -> str:
        """Extract an enhanced summary from conversation history"""
        if not history:
            return "No previous conversation context."
        
        # Analyze conversation themes and patterns
        queries = [h.get('query', '') for h in history]
        intents = [h.get('intent', {}).get('type', 'unknown') for h in history if h.get('intent')]
        
        # Find dominant themes
        all_text = ' '.join(queries).lower()
        common_terms = []
        for term in ['sales', 'revenue', 'customer', 'product', 'performance', 'trend', 'analysis']:
            if term in all_text:
                common_terms.append(term)
        
        # Create enhanced summary
        summary_parts = []
        
        if len(history) > 1:
            summary_parts.append(f"Conversation includes {len(history)} interactions")
        
        if common_terms:
            summary_parts.append(f"focusing on {', '.join(common_terms[:3])}")
        
        if intents:
            from collections import Counter
            dominant_intent = Counter(intents).most_common(1)[0][0]
            summary_parts.append(f"with primary focus on {dominant_intent}")
        
        recent_query = queries[-1] if queries else ""
        if recent_query:
            summary_parts.append(f"Most recent: '{recent_query[:50]}{'...' if len(recent_query) > 50 else ''}'")
        
        return ". ".join(summary_parts) if summary_parts else "Previous conversation available."
    
    def _analyze_conversation_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in conversation history"""
        if not history:
            return {}
        
        patterns = {
            'query_evolution': [],
            'complexity_trend': 'stable',
            'domain_consistency': True,
            'intent_progression': []
        }
        
        try:
            # Track query evolution
            queries = [h.get('query', '') for h in history]
            if len(queries) > 1:
                patterns['query_evolution'] = [
                    {'query': q[:50] + '...' if len(q) > 50 else q, 'timestamp': h.get('timestamp')}
                    for q, h in zip(queries[-3:], history[-3:])
                ]
            
            # Track complexity trend
            complexities = []
            for h in history:
                query = h.get('query', '')
                complexity = self._assess_query_complexity(query)
                complexities.append(complexity)
            
            if len(complexities) > 1:
                if complexities[-1] > complexities[0]:
                    patterns['complexity_trend'] = 'increasing'
                elif complexities[-1] < complexities[0]:
                    patterns['complexity_trend'] = 'decreasing'
            
            # Track intent progression
            intents = [h.get('intent', {}).get('type', 'unknown') for h in history if h.get('intent')]
            if intents:
                patterns['intent_progression'] = intents[-3:]
                patterns['domain_consistency'] = len(set(intents)) <= 2
        
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {str(e)}")
        
        return patterns
    
    def _generate_contextual_insights(self, context: Dict[str, Any]) -> List[str]:
        """Generate insights based on context analysis"""
        insights = []
        
        try:
            # User profile insights
            user_profile = context.get('user_profile', {})
            if user_profile.get('expertise_level') == 'advanced':
                insights.append("User shows advanced analytics expertise - can handle complex queries")
            elif user_profile.get('expertise_level') == 'beginner':
                insights.append("User appears to be new to analytics - provide clear explanations")
            
            # Conversation pattern insights
            patterns = context.get('conversation_patterns', {})
            if patterns.get('complexity_trend') == 'increasing':
                insights.append("Query complexity is increasing - user is diving deeper")
            elif patterns.get('domain_consistency'):
                insights.append("User is focused on a specific domain - maintain context continuity")
            
            # Temporal insights
            temporal_context = context.get('temporal_context', {})
            if temporal_context.get('time_sensitivity', 0) > 0:
                insights.append("Query has time-sensitive elements - prioritize recent data")
            
            # Domain insights
            domain_context = context.get('domain_context', {})
            if domain_context.get('is_cross_domain'):
                insights.append("Query spans multiple business domains - provide comprehensive analysis")
        
        except Exception as e:
            logger.error(f"Error generating contextual insights: {str(e)}")
        
        return insights[:3]  # Limit to top 3 insights
    
    def process_query(self, query: str, session_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Main entry point for processing queries with the workflow
        """
        try:
            logger.info(f"Starting LangGraph workflow for query: {query}")
            
            # Initialize state
            initial_state = AnalyticsState(
                query=query,
                session_id=session_id,
                user_id=user_id,
                intent={},
                tasks=[],
                completed_tasks=[],
                results={},
                context={},
                recommendations=[],
                error=None
            )
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Return structured response
            return {
                "success": not bool(final_state.get('error')),
                "results": final_state.get('results', {}),
                "context": final_state.get('context', {}),
                "recommendations": final_state.get('recommendations', []),
                "completed_tasks": final_state.get('completed_tasks', []),
                "intent": final_state.get('intent', {}),
                "error": final_state.get('error')
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "results": {},
                "context": {},
                "recommendations": ["Please try again or contact support"],
                "completed_tasks": [],
                "intent": {}
            }

# Global workflow instance
_workflow_instance = None

def get_workflow() -> AnalyticsWorkflow:
    """Get or create the global workflow instance"""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = AnalyticsWorkflow()
    return _workflow_instance