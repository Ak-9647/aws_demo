"""
Advanced Context Engineering Module
Sophisticated context management, pattern recognition, and intelligent reasoning
for the Production Analytics Agent v4.1
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
import hashlib

logger = logging.getLogger(__name__)

class ContextPattern:
    """Represents a recognized pattern in user interactions"""
    
    def __init__(self, pattern_type: str, pattern_data: Dict[str, Any], confidence: float):
        self.pattern_type = pattern_type
        self.pattern_data = pattern_data
        self.confidence = confidence
        self.created_at = datetime.now()
        self.usage_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pattern_type': self.pattern_type,
            'pattern_data': self.pattern_data,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'usage_count': self.usage_count
        }

class ContextVector:
    """Semantic representation of context for similarity matching"""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None):
        self.content = content
        self.metadata = metadata or {}
        self.vector = self._create_simple_vector(content)
        self.timestamp = datetime.now()
    
    def _create_simple_vector(self, text: str) -> List[float]:
        """Create a simple vector representation of text"""
        # Simple TF-IDF-like approach for demonstration
        # In production, use proper embeddings (OpenAI, Sentence Transformers, etc.)
        words = re.findall(r'\w+', text.lower())
        word_counts = Counter(words)
        
        # Common analytics terms for weighting
        analytics_terms = {
            'sales': 2.0, 'revenue': 2.0, 'profit': 2.0, 'customer': 1.8,
            'product': 1.8, 'region': 1.5, 'time': 1.5, 'trend': 2.0,
            'analysis': 1.8, 'performance': 1.8, 'growth': 1.8, 'forecast': 2.0,
            'anomaly': 2.0, 'correlation': 2.0, 'segment': 1.5, 'dashboard': 1.5
        }
        
        # Create weighted vector
        vector = []
        for term in sorted(analytics_terms.keys()):
            weight = analytics_terms.get(term, 1.0)
            count = word_counts.get(term, 0)
            vector.append(count * weight)
        
        # Normalize
        magnitude = sum(x**2 for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        return vector
    
    def similarity(self, other: 'ContextVector') -> float:
        """Calculate cosine similarity with another context vector"""
        if len(self.vector) != len(other.vector):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        return max(0.0, min(1.0, dot_product))

class ContextEngineering:
    """
    Advanced context engineering system for intelligent analytics processing
    Provides sophisticated context awareness, pattern recognition, and reasoning
    """
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.context_cache = {}
        self.pattern_cache = {}
        self.context_vectors = []
        self.user_profiles = defaultdict(dict)
        self.session_contexts = defaultdict(dict)
        
        # Context analysis configuration
        self.max_context_history = 10
        self.pattern_confidence_threshold = 0.7
        self.similarity_threshold = 0.6
        
        logger.info("Advanced Context Engineering system initialized")
    
    def analyze_query_context(self, query: str, session_id: str = None, 
                            user_id: str = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive context analysis for a query
        Returns rich context information for enhanced processing
        """
        try:
            logger.info(f"Analyzing context for query: {query[:100]}...")
            
            context_analysis = {
                'query_intent': self._analyze_query_intent(query),
                'semantic_context': self._extract_semantic_context(query),
                'temporal_context': self._analyze_temporal_context(query),
                'domain_context': self._identify_domain_context(query),
                'complexity_analysis': self._analyze_complexity(query),
                'user_context': self._get_user_context(user_id) if user_id else {},
                'session_context': self._get_session_context(session_id) if session_id else {},
                'conversation_context': self._analyze_conversation_context(conversation_history) if conversation_history else {},
                'pattern_matches': self._find_pattern_matches(query, user_id),
                'contextual_recommendations': []
            }
            
            # Generate contextual recommendations
            context_analysis['contextual_recommendations'] = self._generate_contextual_recommendations(
                context_analysis, query
            )
            
            # Update context caches
            if session_id:
                self._update_session_context(session_id, context_analysis)
            
            if user_id:
                self._update_user_context(user_id, context_analysis)
            
            logger.info("Context analysis completed successfully")
            return context_analysis
            
        except Exception as e:
            logger.error(f"Error in context analysis: {str(e)}")
            return self._get_fallback_context(query)
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Advanced query intent analysis"""
        query_lower = query.lower()
        
        # Intent categories with confidence scoring
        intent_patterns = {
            'sales_analysis': {
                'keywords': ['sales', 'revenue', 'selling', 'sold', 'purchase'],
                'patterns': [r'sales?\s+by\s+\w+', r'revenue\s+analysis', r'top\s+selling'],
                'confidence_base': 0.8
            },
            'performance_analysis': {
                'keywords': ['performance', 'kpi', 'metric', 'benchmark'],
                'patterns': [r'performance\s+of', r'how\s+well', r'compare\s+performance'],
                'confidence_base': 0.8
            },
            'trend_analysis': {
                'keywords': ['trend', 'pattern', 'over time', 'growth', 'decline'],
                'patterns': [r'trend\s+in', r'over\s+time', r'growth\s+rate'],
                'confidence_base': 0.8
            },
            'forecasting': {
                'keywords': ['forecast', 'predict', 'future', 'projection', 'estimate'],
                'patterns': [r'forecast\s+for', r'predict\s+\w+', r'next\s+quarter'],
                'confidence_base': 0.9
            },
            'anomaly_detection': {
                'keywords': ['anomaly', 'outlier', 'unusual', 'abnormal', 'strange'],
                'patterns': [r'detect\s+anomal', r'find\s+outlier', r'unusual\s+pattern'],
                'confidence_base': 0.9
            },
            'comparison_analysis': {
                'keywords': ['compare', 'versus', 'vs', 'difference', 'between'],
                'patterns': [r'compare\s+\w+\s+to', r'\w+\s+vs\s+\w+', r'difference\s+between'],
                'confidence_base': 0.8
            },
            'segmentation': {
                'keywords': ['segment', 'group', 'category', 'cluster', 'classify'],
                'patterns': [r'segment\s+by', r'group\s+customers', r'categorize\s+\w+'],
                'confidence_base': 0.8
            }
        }
        
        intent_scores = {}
        
        for intent_type, config in intent_patterns.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in config['keywords'] if keyword in query_lower)
            if keyword_matches > 0:
                score += config['confidence_base'] * (keyword_matches / len(config['keywords']))
            
            # Pattern matching
            pattern_matches = sum(1 for pattern in config['patterns'] if re.search(pattern, query_lower))
            if pattern_matches > 0:
                score += 0.2 * pattern_matches
            
            if score > 0:
                intent_scores[intent_type] = min(1.0, score)
        
        # Determine primary intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1]) if intent_scores else ('general_analysis', 0.5)
        
        return {
            'primary_intent': primary_intent[0],
            'confidence': primary_intent[1],
            'all_intents': intent_scores,
            'is_multi_intent': len([s for s in intent_scores.values() if s > 0.6]) > 1
        }
    
    def _extract_semantic_context(self, query: str) -> Dict[str, Any]:
        """Extract semantic context from the query"""
        query_lower = query.lower()
        
        # Entity extraction
        entities = {
            'time_periods': re.findall(r'\b(?:q[1-4]|quarter|month|year|week|day)\b', query_lower),
            'metrics': re.findall(r'\b(?:sales|revenue|profit|cost|price|volume|count)\b', query_lower),
            'dimensions': re.findall(r'\b(?:region|product|customer|category|channel)\b', query_lower),
            'operations': re.findall(r'\b(?:sum|average|count|max|min|total)\b', query_lower),
            'comparisons': re.findall(r'\b(?:compare|versus|vs|against|between)\b', query_lower)
        }
        
        # Semantic relationships
        relationships = []
        if entities['metrics'] and entities['dimensions']:
            for metric in entities['metrics']:
                for dimension in entities['dimensions']:
                    relationships.append(f"{metric}_by_{dimension}")
        
        # Context richness score
        richness_score = sum(len(v) for v in entities.values()) / 10.0
        
        return {
            'entities': entities,
            'relationships': relationships,
            'richness_score': min(1.0, richness_score),
            'semantic_complexity': len(relationships)
        }
    
    def _analyze_temporal_context(self, query: str) -> Dict[str, Any]:
        """Analyze temporal aspects of the query"""
        query_lower = query.lower()
        
        # Time period detection
        time_patterns = {
            'specific_periods': re.findall(r'\b(?:q[1-4]\s+20\d{2}|january|february|march|april|may|june|july|august|september|october|november|december)\b', query_lower),
            'relative_periods': re.findall(r'\b(?:last|this|next|current|previous)\s+(?:quarter|month|year|week)\b', query_lower),
            'time_ranges': re.findall(r'\b(?:from|between)\s+\w+\s+(?:to|and)\s+\w+\b', query_lower),
            'temporal_modifiers': re.findall(r'\b(?:daily|weekly|monthly|quarterly|yearly|annual)\b', query_lower)
        }
        
        # Temporal complexity
        temporal_complexity = sum(len(v) for v in time_patterns.values())
        
        # Time sensitivity
        time_sensitive_terms = ['real-time', 'current', 'latest', 'recent', 'now', 'today']
        time_sensitivity = sum(1 for term in time_sensitive_terms if term in query_lower)
        
        return {
            'time_patterns': time_patterns,
            'temporal_complexity': temporal_complexity,
            'time_sensitivity': time_sensitivity,
            'requires_time_series': any(term in query_lower for term in ['trend', 'over time', 'growth', 'forecast'])
        }
    
    def _identify_domain_context(self, query: str) -> Dict[str, Any]:
        """Identify the business domain context"""
        query_lower = query.lower()
        
        domain_indicators = {
            'sales': ['sales', 'revenue', 'selling', 'purchase', 'order', 'transaction'],
            'marketing': ['marketing', 'campaign', 'lead', 'conversion', 'acquisition', 'retention'],
            'finance': ['profit', 'cost', 'expense', 'budget', 'roi', 'margin'],
            'operations': ['inventory', 'supply', 'logistics', 'fulfillment', 'shipping'],
            'customer': ['customer', 'client', 'user', 'satisfaction', 'churn', 'loyalty'],
            'product': ['product', 'feature', 'catalog', 'category', 'brand'],
            'hr': ['employee', 'staff', 'team', 'performance', 'productivity'],
            'technology': ['system', 'application', 'database', 'api', 'performance']
        }
        
        domain_scores = {}
        for domain, indicators in domain_indicators.items():
            score = sum(1 for indicator in indicators if indicator in query_lower)
            if score > 0:
                domain_scores[domain] = score / len(indicators)
        
        primary_domain = max(domain_scores.items(), key=lambda x: x[1]) if domain_scores else ('general', 0.1)
        
        return {
            'primary_domain': primary_domain[0],
            'domain_confidence': primary_domain[1],
            'all_domains': domain_scores,
            'is_cross_domain': len([s for s in domain_scores.values() if s > 0.3]) > 1
        }
    
    def _analyze_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity across multiple dimensions"""
        query_lower = query.lower()
        
        # Syntactic complexity
        word_count = len(query.split())
        sentence_count = query.count('.') + query.count('?') + query.count('!') + 1
        avg_sentence_length = word_count / sentence_count
        
        # Semantic complexity
        question_words = len(re.findall(r'\b(?:what|how|when|where|why|which|who)\b', query_lower))
        conjunctions = len(re.findall(r'\b(?:and|or|but|however|also|additionally)\b', query_lower))
        
        # Analytical complexity
        analytical_terms = ['analyze', 'compare', 'correlate', 'forecast', 'predict', 'segment', 'cluster']
        analytical_complexity = sum(1 for term in analytical_terms if term in query_lower)
        
        # Overall complexity score
        complexity_score = (
            min(word_count / 20, 1.0) * 0.3 +
            min(question_words / 3, 1.0) * 0.2 +
            min(conjunctions / 2, 1.0) * 0.2 +
            min(analytical_complexity / 3, 1.0) * 0.3
        )
        
        return {
            'syntactic_complexity': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_sentence_length': avg_sentence_length
            },
            'semantic_complexity': {
                'question_words': question_words,
                'conjunctions': conjunctions
            },
            'analytical_complexity': analytical_complexity,
            'overall_complexity': complexity_score,
            'complexity_level': self._get_complexity_level(complexity_score)
        }
    
    def _get_complexity_level(self, score: float) -> str:
        """Convert complexity score to level"""
        if score < 0.3:
            return 'simple'
        elif score < 0.6:
            return 'moderate'
        elif score < 0.8:
            return 'complex'
        else:
            return 'very_complex'
    
    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific context"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        
        return {
            'query_history_count': profile.get('query_count', 0),
            'preferred_domains': profile.get('preferred_domains', []),
            'complexity_preference': profile.get('avg_complexity', 0.5),
            'common_intents': profile.get('common_intents', []),
            'last_interaction': profile.get('last_interaction'),
            'expertise_level': self._assess_user_expertise(profile)
        }
    
    def _assess_user_expertise(self, profile: Dict[str, Any]) -> str:
        """Assess user expertise level based on interaction patterns"""
        query_count = profile.get('query_count', 0)
        avg_complexity = profile.get('avg_complexity', 0.5)
        
        if query_count < 5:
            return 'beginner'
        elif query_count < 20 and avg_complexity < 0.6:
            return 'intermediate'
        elif avg_complexity > 0.7:
            return 'advanced'
        else:
            return 'intermediate'
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session-specific context"""
        if session_id not in self.session_contexts:
            return {}
        
        context = self.session_contexts[session_id]
        
        return {
            'session_duration': context.get('duration', 0),
            'query_count': context.get('query_count', 0),
            'dominant_intent': context.get('dominant_intent'),
            'context_continuity': context.get('continuity_score', 0.0),
            'last_query_time': context.get('last_query_time')
        }
    
    def _analyze_conversation_context(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation history for context"""
        if not history:
            return {}
        
        # Extract patterns from conversation
        intents = [h.get('intent', {}).get('primary_intent') for h in history if h.get('intent')]
        domains = [h.get('domain') for h in history if h.get('domain')]
        
        # Calculate context continuity
        continuity_score = self._calculate_continuity_score(history)
        
        # Identify conversation themes
        themes = self._extract_conversation_themes(history)
        
        return {
            'conversation_length': len(history),
            'dominant_intents': Counter(intents).most_common(3),
            'dominant_domains': Counter(domains).most_common(3),
            'continuity_score': continuity_score,
            'themes': themes,
            'context_evolution': self._analyze_context_evolution(history)
        }
    
    def _calculate_continuity_score(self, history: List[Dict]) -> float:
        """Calculate how continuous the conversation context is"""
        if len(history) < 2:
            return 0.0
        
        continuity_scores = []
        
        for i in range(1, len(history)):
            prev_query = history[i-1].get('query', '')
            curr_query = history[i].get('query', '')
            
            # Create context vectors
            prev_vector = ContextVector(prev_query)
            curr_vector = ContextVector(curr_query)
            
            # Calculate similarity
            similarity = prev_vector.similarity(curr_vector)
            continuity_scores.append(similarity)
        
        return sum(continuity_scores) / len(continuity_scores)
    
    def _extract_conversation_themes(self, history: List[Dict]) -> List[str]:
        """Extract main themes from conversation history"""
        all_queries = ' '.join([h.get('query', '') for h in history])
        
        # Simple theme extraction based on frequent terms
        words = re.findall(r'\w+', all_queries.lower())
        word_freq = Counter(words)
        
        # Filter for meaningful terms
        meaningful_terms = [
            word for word, freq in word_freq.most_common(10)
            if len(word) > 3 and word not in ['what', 'how', 'when', 'where', 'why', 'which', 'show', 'give', 'tell']
        ]
        
        return meaningful_terms[:5]
    
    def _analyze_context_evolution(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze how context has evolved over the conversation"""
        if len(history) < 3:
            return {}
        
        # Track intent evolution
        intents = [h.get('intent', {}).get('primary_intent') for h in history if h.get('intent')]
        intent_changes = sum(1 for i in range(1, len(intents)) if intents[i] != intents[i-1])
        
        # Track complexity evolution
        complexities = [h.get('complexity', 0.5) for h in history]
        complexity_trend = 'increasing' if complexities[-1] > complexities[0] else 'decreasing'
        
        return {
            'intent_stability': 1.0 - (intent_changes / max(len(intents) - 1, 1)),
            'complexity_trend': complexity_trend,
            'context_depth': len(set(intents))
        }
    
    def _find_pattern_matches(self, query: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Find matching patterns from previous interactions"""
        matches = []
        
        # Create vector for current query
        query_vector = ContextVector(query)
        
        # Search through cached patterns
        for pattern_id, pattern in self.pattern_cache.items():
            if pattern.confidence > self.pattern_confidence_threshold:
                # Calculate similarity (simplified)
                pattern_query = pattern.pattern_data.get('representative_query', '')
                if pattern_query:
                    pattern_vector = ContextVector(pattern_query)
                    similarity = query_vector.similarity(pattern_vector)
                    
                    if similarity > self.similarity_threshold:
                        matches.append({
                            'pattern_type': pattern.pattern_type,
                            'similarity': similarity,
                            'confidence': pattern.confidence,
                            'usage_count': pattern.usage_count,
                            'recommendations': pattern.pattern_data.get('recommendations', [])
                        })
        
        # Sort by relevance (similarity * confidence)
        matches.sort(key=lambda x: x['similarity'] * x['confidence'], reverse=True)
        
        return matches[:3]  # Return top 3 matches
    
    def _generate_contextual_recommendations(self, context_analysis: Dict[str, Any], query: str) -> List[str]:
        """Generate intelligent contextual recommendations"""
        recommendations = []
        
        # Intent-based recommendations
        primary_intent = context_analysis['query_intent']['primary_intent']
        
        if primary_intent == 'sales_analysis':
            recommendations.extend([
                "Consider segmenting sales data by customer demographics for deeper insights",
                "Analyze seasonal patterns to optimize inventory and marketing timing",
                "Compare performance against industry benchmarks or historical data"
            ])
        elif primary_intent == 'trend_analysis':
            recommendations.extend([
                "Extend the analysis to include leading indicators for better predictions",
                "Consider external factors that might influence the trends",
                "Set up automated monitoring to track trend changes"
            ])
        elif primary_intent == 'forecasting':
            recommendations.extend([
                "Validate forecasts with multiple models for better accuracy",
                "Include confidence intervals to understand prediction uncertainty",
                "Consider scenario analysis for different business conditions"
            ])
        
        # Complexity-based recommendations
        complexity_level = context_analysis['complexity_analysis']['complexity_level']
        
        if complexity_level == 'very_complex':
            recommendations.append("Consider breaking this analysis into smaller, focused questions")
        elif complexity_level == 'simple':
            recommendations.append("You might want to explore additional dimensions or drill deeper into the data")
        
        # Domain-specific recommendations
        primary_domain = context_analysis['domain_context']['primary_domain']
        
        if primary_domain == 'sales':
            recommendations.append("Consider analyzing customer lifetime value and retention metrics")
        elif primary_domain == 'marketing':
            recommendations.append("Evaluate campaign ROI and attribution across different channels")
        elif primary_domain == 'finance':
            recommendations.append("Include variance analysis and budget vs. actual comparisons")
        
        # Pattern-based recommendations
        for pattern_match in context_analysis['pattern_matches']:
            if pattern_match['similarity'] > 0.8:
                recommendations.extend(pattern_match.get('recommendations', []))
        
        # User context recommendations
        user_context = context_analysis.get('user_context', {})
        expertise_level = user_context.get('expertise_level', 'intermediate')
        
        if expertise_level == 'beginner':
            recommendations.append("Start with basic summary statistics before moving to advanced analytics")
        elif expertise_level == 'advanced':
            recommendations.append("Consider advanced statistical methods or machine learning approaches")
        
        # Remove duplicates and limit
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:5]
    
    def _update_session_context(self, session_id: str, context_analysis: Dict[str, Any]):
        """Update session context with new analysis"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                'start_time': time.time(),
                'query_count': 0,
                'intents': [],
                'domains': []
            }
        
        session_context = self.session_contexts[session_id]
        session_context['query_count'] += 1
        session_context['last_query_time'] = time.time()
        session_context['duration'] = time.time() - session_context['start_time']
        
        # Track intents and domains
        primary_intent = context_analysis['query_intent']['primary_intent']
        primary_domain = context_analysis['domain_context']['primary_domain']
        
        session_context['intents'].append(primary_intent)
        session_context['domains'].append(primary_domain)
        
        # Calculate dominant patterns
        session_context['dominant_intent'] = Counter(session_context['intents']).most_common(1)[0][0]
        session_context['dominant_domain'] = Counter(session_context['domains']).most_common(1)[0][0]
    
    def _update_user_context(self, user_id: str, context_analysis: Dict[str, Any]):
        """Update user profile with new interaction data"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'query_count': 0,
                'intents': [],
                'domains': [],
                'complexities': [],
                'first_interaction': time.time()
            }
        
        profile = self.user_profiles[user_id]
        profile['query_count'] += 1
        profile['last_interaction'] = time.time()
        
        # Track patterns
        primary_intent = context_analysis['query_intent']['primary_intent']
        primary_domain = context_analysis['domain_context']['primary_domain']
        complexity = context_analysis['complexity_analysis']['overall_complexity']
        
        profile['intents'].append(primary_intent)
        profile['domains'].append(primary_domain)
        profile['complexities'].append(complexity)
        
        # Calculate preferences
        profile['preferred_domains'] = [item[0] for item in Counter(profile['domains']).most_common(3)]
        profile['common_intents'] = [item[0] for item in Counter(profile['intents']).most_common(3)]
        profile['avg_complexity'] = sum(profile['complexities']) / len(profile['complexities'])
    
    def _get_fallback_context(self, query: str) -> Dict[str, Any]:
        """Provide fallback context when analysis fails"""
        return {
            'query_intent': {'primary_intent': 'general_analysis', 'confidence': 0.5},
            'semantic_context': {'entities': {}, 'relationships': [], 'richness_score': 0.1},
            'temporal_context': {'time_patterns': {}, 'temporal_complexity': 0},
            'domain_context': {'primary_domain': 'general', 'domain_confidence': 0.1},
            'complexity_analysis': {'overall_complexity': 0.5, 'complexity_level': 'moderate'},
            'user_context': {},
            'session_context': {},
            'conversation_context': {},
            'pattern_matches': [],
            'contextual_recommendations': [
                "Try rephrasing your question with more specific terms",
                "Consider breaking complex queries into simpler parts"
            ]
        }
    
    def learn_from_interaction(self, query: str, response: Dict[str, Any], 
                             user_feedback: Dict[str, Any] = None, 
                             session_id: str = None, user_id: str = None):
        """Learn from user interactions to improve context understanding"""
        try:
            # Create pattern from successful interaction
            if response.get('success', False):
                pattern_data = {
                    'representative_query': query,
                    'response_type': response.get('type', 'analysis'),
                    'success_indicators': response.get('metrics', {}),
                    'recommendations': response.get('recommendations', [])
                }
                
                # Calculate pattern confidence based on success metrics
                confidence = 0.7  # Base confidence
                if user_feedback:
                    if user_feedback.get('helpful', False):
                        confidence += 0.2
                    if user_feedback.get('accurate', False):
                        confidence += 0.1
                
                # Create and store pattern
                pattern_id = hashlib.md5(query.encode()).hexdigest()[:8]
                pattern = ContextPattern('successful_query', pattern_data, confidence)
                self.pattern_cache[pattern_id] = pattern
                
                logger.info(f"Learned new pattern from successful interaction: {pattern_id}")
        
        except Exception as e:
            logger.error(f"Error learning from interaction: {str(e)}")
    
    def get_context_summary(self, session_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """Get a summary of current context state"""
        summary = {
            'total_patterns': len(self.pattern_cache),
            'active_sessions': len(self.session_contexts),
            'user_profiles': len(self.user_profiles)
        }
        
        if session_id and session_id in self.session_contexts:
            summary['session_info'] = self.session_contexts[session_id]
        
        if user_id and user_id in self.user_profiles:
            summary['user_info'] = self.user_profiles[user_id]
        
        return summary

# Global context engineering instance
_context_engine = None

def get_context_engine(memory_manager=None) -> ContextEngineering:
    """Get or create the global context engineering instance"""
    global _context_engine
    if _context_engine is None:
        _context_engine = ContextEngineering(memory_manager)
    return _context_engine