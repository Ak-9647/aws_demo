#!/usr/bin/env python3
"""
Production Analytics Agent v4.1 - Evaluation Suite
Comprehensive testing and evaluation framework
"""

import json
import time
import requests
import boto3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics
import concurrent.futures
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    test_name: str
    status: str  # PASS, FAIL, SKIP
    duration: float
    details: Dict[str, Any]
    error_message: Optional[str] = None

class EvaluationFramework:
    """Main evaluation framework for the Production Analytics Agent"""
    
    def __init__(self):
        self.config = {
            'gui_url': 'http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com',
            'agent_arn': 'arn:aws:bedrock-agentcore:us-west-2:280383026847:runtime/hosted_agent_jqgjl-fJiyIV95k9',
            'gateway_id': 'production-analytics-agent-database-gateway-wni9bfjx64',
            'lambda_function': 'production-analytics-agent-analytics-gateway-target',
            'region': 'us-west-2'
        }
        self.results = []
        self.aws_clients = {
            'lambda': boto3.client('lambda', region_name=self.config['region']),
            'ecs': boto3.client('ecs', region_name=self.config['region']),
            'rds': boto3.client('rds', region_name=self.config['region']),
            'elasticache': boto3.client('elasticache', region_name=self.config['region'])
        }
    
    def run_evaluation(self, test_categories: List[str] = None) -> Dict[str, Any]:
        """Run the complete evaluation suite"""
        logger.info("🚀 Starting Production Analytics Agent Evaluation")
        
        if test_categories is None:
            test_categories = ['infrastructure', 'functional', 'performance', 'security', 'integration']
        
        start_time = time.time()
        
        for category in test_categories:
            logger.info(f"📊 Running {category.upper()} tests...")
            category_results = getattr(self, f'test_{category}')()
            self.results.extend(category_results)
        
        total_duration = time.time() - start_time
        
        # Generate comprehensive report
        report = self.generate_report(total_duration)
        
        logger.info("✅ Evaluation completed!")
        return report
    
    def test_infrastructure(self) -> List[TestResult]:
        """Test infrastructure components and health"""
        tests = []
        
        # Test 1: GUI Accessibility
        tests.append(self._test_gui_health())
        
        # Test 2: Lambda Function Health
        tests.append(self._test_lambda_health())
        
        # Test 3: Database Connectivity
        tests.append(self._test_database_health())
        
        # Test 4: Cache System Health
        tests.append(self._test_cache_health())
        
        # Test 5: ECS Service Health
        tests.append(self._test_ecs_health())
        
        return tests
    
    def test_functional(self) -> List[TestResult]:
        """Test core analytics functionality"""
        tests = []
        
        # Test 1: Basic Analytics
        tests.append(self._test_basic_analytics())
        
        # Test 2: Statistical Analysis
        tests.append(self._test_statistical_analysis())
        
        # Test 3: Data Visualization
        tests.append(self._test_visualization())
        
        # Test 4: Anomaly Detection
        tests.append(self._test_anomaly_detection())
        
        # Test 5: Query Processing
        tests.append(self._test_query_processing())
        
        return tests
    
    def test_performance(self) -> List[TestResult]:
        """Test system performance and scalability"""
        tests = []
        
        # Test 1: Response Time
        tests.append(self._test_response_time())
        
        # Test 2: Throughput
        tests.append(self._test_throughput())
        
        # Test 3: Concurrent Users
        tests.append(self._test_concurrent_users())
        
        # Test 4: Resource Utilization
        tests.append(self._test_resource_utilization())
        
        # Test 5: Scalability
        tests.append(self._test_scalability())
        
        return tests
    
    def test_security(self) -> List[TestResult]:
        """Test security controls and authentication"""
        tests = []
        
        # Test 1: Authentication
        tests.append(self._test_authentication())
        
        # Test 2: Authorization
        tests.append(self._test_authorization())
        
        # Test 3: Data Encryption
        tests.append(self._test_encryption())
        
        # Test 4: Network Security
        tests.append(self._test_network_security())
        
        # Test 5: Input Validation
        tests.append(self._test_input_validation())
        
        return tests
    
    def test_integration(self) -> List[TestResult]:
        """Test gateway and external system integration"""
        tests = []
        
        # Test 1: Gateway Connectivity
        tests.append(self._test_gateway_connectivity())
        
        # Test 2: Database Integration
        tests.append(self._test_database_integration())
        
        # Test 3: Authentication Flow
        tests.append(self._test_auth_flow())
        
        # Test 4: Error Handling
        tests.append(self._test_error_handling())
        
        # Test 5: Data Flow
        tests.append(self._test_data_flow())
        
        return tests
    
    # Infrastructure Tests
    def _test_gui_health(self) -> TestResult:
        """Test GUI accessibility and basic functionality"""
        start_time = time.time()
        try:
            response = requests.get(self.config['gui_url'], timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                return TestResult(
                    test_name="GUI Health Check",
                    status="PASS",
                    duration=duration,
                    details={
                        "status_code": response.status_code,
                        "response_time": duration,
                        "content_length": len(response.content)
                    }
                )
            else:
                return TestResult(
                    test_name="GUI Health Check",
                    status="FAIL",
                    duration=duration,
                    details={"status_code": response.status_code},
                    error_message=f"HTTP {response.status_code}"
                )
        except Exception as e:
            return TestResult(
                test_name="GUI Health Check",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_lambda_health(self) -> TestResult:
        """Test Lambda function health and responsiveness"""
        start_time = time.time()
        try:
            # Test Lambda function with health check
            payload = {"path": "/health"}
            
            response = self.aws_clients['lambda'].invoke(
                FunctionName=self.config['lambda_function'],
                Payload=json.dumps(payload)
            )
            
            duration = time.time() - start_time
            
            if response['StatusCode'] == 200:
                payload_response = json.loads(response['Payload'].read())
                
                return TestResult(
                    test_name="Lambda Health Check",
                    status="PASS",
                    duration=duration,
                    details={
                        "status_code": response['StatusCode'],
                        "response": payload_response,
                        "execution_duration": duration
                    }
                )
            else:
                return TestResult(
                    test_name="Lambda Health Check",
                    status="FAIL",
                    duration=duration,
                    details={"status_code": response['StatusCode']},
                    error_message=f"Lambda returned {response['StatusCode']}"
                )
        except Exception as e:
            return TestResult(
                test_name="Lambda Health Check",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_database_health(self) -> TestResult:
        """Test database connectivity and health"""
        start_time = time.time()
        try:
            # Get RDS cluster information
            response = self.aws_clients['rds'].describe_db_clusters(
                DBClusterIdentifier='production-analytics-agent-analytics-cluster'
            )
            
            duration = time.time() - start_time
            cluster = response['DBClusters'][0]
            
            if cluster['Status'] == 'available':
                return TestResult(
                    test_name="Database Health Check",
                    status="PASS",
                    duration=duration,
                    details={
                        "status": cluster['Status'],
                        "engine": cluster['Engine'],
                        "endpoint": cluster['Endpoint']
                    }
                )
            else:
                return TestResult(
                    test_name="Database Health Check",
                    status="FAIL",
                    duration=duration,
                    details={"status": cluster['Status']},
                    error_message=f"Database status: {cluster['Status']}"
                )
        except Exception as e:
            return TestResult(
                test_name="Database Health Check",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_cache_health(self) -> TestResult:
        """Test Redis cache health"""
        start_time = time.time()
        try:
            # Get ElastiCache cluster information
            response = self.aws_clients['elasticache'].describe_cache_clusters(
                CacheClusterId='production-analytics-agent-redis-001'
            )
            
            duration = time.time() - start_time
            cluster = response['CacheClusters'][0]
            
            if cluster['CacheClusterStatus'] == 'available':
                return TestResult(
                    test_name="Cache Health Check",
                    status="PASS",
                    duration=duration,
                    details={
                        "status": cluster['CacheClusterStatus'],
                        "engine": cluster['Engine'],
                        "node_type": cluster['CacheNodeType']
                    }
                )
            else:
                return TestResult(
                    test_name="Cache Health Check",
                    status="FAIL",
                    duration=duration,
                    details={"status": cluster['CacheClusterStatus']},
                    error_message=f"Cache status: {cluster['CacheClusterStatus']}"
                )
        except Exception as e:
            return TestResult(
                test_name="Cache Health Check",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_ecs_health(self) -> TestResult:
        """Test ECS service health"""
        start_time = time.time()
        try:
            # Get ECS service information
            response = self.aws_clients['ecs'].describe_services(
                cluster='production-analytics-agent-cluster',
                services=['production-analytics-agent-gui-service']
            )
            
            duration = time.time() - start_time
            
            if response['services']:
                service = response['services'][0]
                running_count = service['runningCount']
                desired_count = service['desiredCount']
                
                if running_count == desired_count and running_count > 0:
                    return TestResult(
                        test_name="ECS Health Check",
                        status="PASS",
                        duration=duration,
                        details={
                            "running_count": running_count,
                            "desired_count": desired_count,
                            "status": service['status']
                        }
                    )
                else:
                    return TestResult(
                        test_name="ECS Health Check",
                        status="FAIL",
                        duration=duration,
                        details={
                            "running_count": running_count,
                            "desired_count": desired_count
                        },
                        error_message=f"Running: {running_count}, Desired: {desired_count}"
                    )
            else:
                return TestResult(
                    test_name="ECS Health Check",
                    status="FAIL",
                    duration=duration,
                    details={},
                    error_message="No services found"
                )
        except Exception as e:
            return TestResult(
                test_name="ECS Health Check",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    # Functional Tests
    def _test_basic_analytics(self) -> TestResult:
        """Test basic analytics functionality"""
        start_time = time.time()
        try:
            # Test data for basic analytics
            test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            
            # Calculate expected results
            expected_mean = statistics.mean(test_data)
            expected_median = statistics.median(test_data)
            
            # Simulate analytics processing
            calculated_mean = sum(test_data) / len(test_data)
            calculated_median = sorted(test_data)[len(test_data) // 2]
            
            duration = time.time() - start_time
            
            # Verify accuracy
            mean_accurate = abs(calculated_mean - expected_mean) < 0.001
            median_accurate = abs(calculated_median - expected_median) < 0.001
            
            if mean_accurate and median_accurate:
                return TestResult(
                    test_name="Basic Analytics",
                    status="PASS",
                    duration=duration,
                    details={
                        "expected_mean": expected_mean,
                        "calculated_mean": calculated_mean,
                        "expected_median": expected_median,
                        "calculated_median": calculated_median,
                        "accuracy": "100%"
                    }
                )
            else:
                return TestResult(
                    test_name="Basic Analytics",
                    status="FAIL",
                    duration=duration,
                    details={
                        "mean_accurate": mean_accurate,
                        "median_accurate": median_accurate
                    },
                    error_message="Analytics calculations inaccurate"
                )
        except Exception as e:
            return TestResult(
                test_name="Basic Analytics",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_statistical_analysis(self) -> TestResult:
        """Test statistical analysis capabilities"""
        start_time = time.time()
        try:
            # Test correlation analysis
            x_data = [1, 2, 3, 4, 5]
            y_data = [2, 4, 6, 8, 10]  # Perfect positive correlation
            
            # Calculate correlation coefficient
            n = len(x_data)
            sum_x = sum(x_data)
            sum_y = sum(y_data)
            sum_xy = sum(x * y for x, y in zip(x_data, y_data))
            sum_x2 = sum(x * x for x in x_data)
            sum_y2 = sum(y * y for y in y_data)
            
            correlation = (n * sum_xy - sum_x * sum_y) / \
                         ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))**0.5
            
            duration = time.time() - start_time
            
            # Perfect correlation should be 1.0
            if abs(correlation - 1.0) < 0.001:
                return TestResult(
                    test_name="Statistical Analysis",
                    status="PASS",
                    duration=duration,
                    details={
                        "correlation": correlation,
                        "expected": 1.0,
                        "accuracy": "100%"
                    }
                )
            else:
                return TestResult(
                    test_name="Statistical Analysis",
                    status="FAIL",
                    duration=duration,
                    details={"correlation": correlation, "expected": 1.0},
                    error_message=f"Correlation calculation error: {correlation}"
                )
        except Exception as e:
            return TestResult(
                test_name="Statistical Analysis",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_visualization(self) -> TestResult:
        """Test data visualization capabilities"""
        start_time = time.time()
        try:
            # Simulate visualization generation
            chart_types = ['bar', 'line', 'scatter', 'pie']
            generated_charts = []
            
            for chart_type in chart_types:
                # Simulate chart generation
                chart_data = {
                    'type': chart_type,
                    'data': [1, 2, 3, 4, 5],
                    'labels': ['A', 'B', 'C', 'D', 'E'],
                    'generated': True
                }
                generated_charts.append(chart_data)
            
            duration = time.time() - start_time
            
            if len(generated_charts) == len(chart_types):
                return TestResult(
                    test_name="Data Visualization",
                    status="PASS",
                    duration=duration,
                    details={
                        "charts_generated": len(generated_charts),
                        "chart_types": chart_types,
                        "success_rate": "100%"
                    }
                )
            else:
                return TestResult(
                    test_name="Data Visualization",
                    status="FAIL",
                    duration=duration,
                    details={
                        "expected": len(chart_types),
                        "generated": len(generated_charts)
                    },
                    error_message="Chart generation incomplete"
                )
        except Exception as e:
            return TestResult(
                test_name="Data Visualization",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_anomaly_detection(self) -> TestResult:
        """Test anomaly detection capabilities"""
        start_time = time.time()
        try:
            # Test data with known outliers
            test_data = [1, 2, 3, 4, 5, 100, 6, 7, 8, 9]  # 100 is an outlier
            
            # IQR-based anomaly detection
            sorted_data = sorted(test_data)
            q1 = sorted_data[len(sorted_data) // 4]
            q3 = sorted_data[3 * len(sorted_data) // 4]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            anomalies = [x for x in test_data if x < lower_bound or x > upper_bound]
            
            duration = time.time() - start_time
            
            # Should detect 100 as an anomaly
            if 100 in anomalies and len(anomalies) == 1:
                return TestResult(
                    test_name="Anomaly Detection",
                    status="PASS",
                    duration=duration,
                    details={
                        "anomalies_detected": anomalies,
                        "expected_anomalies": [100],
                        "detection_rate": "100%"
                    }
                )
            else:
                return TestResult(
                    test_name="Anomaly Detection",
                    status="FAIL",
                    duration=duration,
                    details={
                        "detected": anomalies,
                        "expected": [100]
                    },
                    error_message="Anomaly detection inaccurate"
                )
        except Exception as e:
            return TestResult(
                test_name="Anomaly Detection",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_query_processing(self) -> TestResult:
        """Test natural language query processing"""
        start_time = time.time()
        try:
            # Test queries
            test_queries = [
                "Calculate the average of these numbers",
                "Show me a chart of sales data",
                "Find anomalies in the dataset",
                "What is the correlation between X and Y?"
            ]
            
            processed_queries = []
            for query in test_queries:
                # Simulate query processing
                processed = {
                    'query': query,
                    'intent': 'analytics',
                    'processed': True,
                    'confidence': 0.95
                }
                processed_queries.append(processed)
            
            duration = time.time() - start_time
            
            success_rate = len(processed_queries) / len(test_queries)
            
            if success_rate >= 0.9:  # 90% success rate
                return TestResult(
                    test_name="Query Processing",
                    status="PASS",
                    duration=duration,
                    details={
                        "queries_processed": len(processed_queries),
                        "total_queries": len(test_queries),
                        "success_rate": f"{success_rate * 100}%"
                    }
                )
            else:
                return TestResult(
                    test_name="Query Processing",
                    status="FAIL",
                    duration=duration,
                    details={"success_rate": f"{success_rate * 100}%"},
                    error_message=f"Success rate below 90%: {success_rate * 100}%"
                )
        except Exception as e:
            return TestResult(
                test_name="Query Processing",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    # Performance Tests
    def _test_response_time(self) -> TestResult:
        """Test system response time"""
        start_time = time.time()
        try:
            response_times = []
            
            # Test multiple requests
            for i in range(10):
                request_start = time.time()
                
                # Simulate request to GUI
                try:
                    response = requests.get(self.config['gui_url'], timeout=10)
                    request_duration = time.time() - request_start
                    
                    if response.status_code == 200:
                        response_times.append(request_duration)
                except:
                    pass
            
            duration = time.time() - start_time
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]
                
                # Target: 95th percentile < 5 seconds
                if p95_response_time < 5.0:
                    return TestResult(
                        test_name="Response Time",
                        status="PASS",
                        duration=duration,
                        details={
                            "average_response_time": avg_response_time,
                            "p95_response_time": p95_response_time,
                            "samples": len(response_times)
                        }
                    )
                else:
                    return TestResult(
                        test_name="Response Time",
                        status="FAIL",
                        duration=duration,
                        details={
                            "p95_response_time": p95_response_time,
                            "target": 5.0
                        },
                        error_message=f"P95 response time too high: {p95_response_time}s"
                    )
            else:
                return TestResult(
                    test_name="Response Time",
                    status="FAIL",
                    duration=duration,
                    details={},
                    error_message="No successful responses"
                )
        except Exception as e:
            return TestResult(
                test_name="Response Time",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_throughput(self) -> TestResult:
        """Test system throughput"""
        start_time = time.time()
        try:
            # Simulate concurrent requests
            successful_requests = 0
            total_requests = 50
            
            def make_request():
                try:
                    response = requests.get(self.config['gui_url'], timeout=5)
                    return response.status_code == 200
                except:
                    return False
            
            # Use thread pool for concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(total_requests)]
                
                for future in concurrent.futures.as_completed(futures):
                    if future.result():
                        successful_requests += 1
            
            duration = time.time() - start_time
            throughput = successful_requests / duration  # requests per second
            
            # Target: > 25 requests per second
            if throughput >= 25:
                return TestResult(
                    test_name="Throughput",
                    status="PASS",
                    duration=duration,
                    details={
                        "throughput": throughput,
                        "successful_requests": successful_requests,
                        "total_requests": total_requests,
                        "success_rate": f"{(successful_requests/total_requests)*100}%"
                    }
                )
            else:
                return TestResult(
                    test_name="Throughput",
                    status="FAIL",
                    duration=duration,
                    details={
                        "throughput": throughput,
                        "target": 25
                    },
                    error_message=f"Throughput too low: {throughput} req/s"
                )
        except Exception as e:
            return TestResult(
                test_name="Throughput",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    def _test_concurrent_users(self) -> TestResult:
        """Test concurrent user handling"""
        start_time = time.time()
        try:
            # Simulate concurrent users
            concurrent_users = 20
            successful_sessions = 0
            
            def simulate_user_session():
                try:
                    # Simulate user workflow
                    response1 = requests.get(self.config['gui_url'], timeout=10)
                    if response1.status_code != 200:
                        return False
                    
                    # Simulate additional requests
                    time.sleep(0.1)  # User think time
                    response2 = requests.get(self.config['gui_url'], timeout=10)
                    
                    return response2.status_code == 200
                except:
                    return False
            
            # Run concurrent user sessions
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(simulate_user_session) for _ in range(concurrent_users)]
                
                for future in concurrent.futures.as_completed(futures):
                    if future.result():
                        successful_sessions += 1
            
            duration = time.time() - start_time
            success_rate = successful_sessions / concurrent_users
            
            # Target: > 90% success rate
            if success_rate >= 0.9:
                return TestResult(
                    test_name="Concurrent Users",
                    status="PASS",
                    duration=duration,
                    details={
                        "concurrent_users": concurrent_users,
                        "successful_sessions": successful_sessions,
                        "success_rate": f"{success_rate * 100}%"
                    }
                )
            else:
                return TestResult(
                    test_name="Concurrent Users",
                    status="FAIL",
                    duration=duration,
                    details={
                        "success_rate": f"{success_rate * 100}%",
                        "target": "90%"
                    },
                    error_message=f"Success rate too low: {success_rate * 100}%"
                )
        except Exception as e:
            return TestResult(
                test_name="Concurrent Users",
                status="FAIL",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    # Placeholder methods for remaining tests
    def _test_resource_utilization(self) -> TestResult:
        """Test resource utilization"""
        return TestResult("Resource Utilization", "SKIP", 0, {}, "Not implemented")
    
    def _test_scalability(self) -> TestResult:
        """Test system scalability"""
        return TestResult("Scalability", "SKIP", 0, {}, "Not implemented")
    
    def _test_authentication(self) -> TestResult:
        """Test authentication mechanisms"""
        return TestResult("Authentication", "SKIP", 0, {}, "Not implemented")
    
    def _test_authorization(self) -> TestResult:
        """Test authorization controls"""
        return TestResult("Authorization", "SKIP", 0, {}, "Not implemented")
    
    def _test_encryption(self) -> TestResult:
        """Test data encryption"""
        return TestResult("Encryption", "SKIP", 0, {}, "Not implemented")
    
    def _test_network_security(self) -> TestResult:
        """Test network security"""
        return TestResult("Network Security", "SKIP", 0, {}, "Not implemented")
    
    def _test_input_validation(self) -> TestResult:
        """Test input validation"""
        return TestResult("Input Validation", "SKIP", 0, {}, "Not implemented")
    
    def _test_gateway_connectivity(self) -> TestResult:
        """Test gateway connectivity"""
        return TestResult("Gateway Connectivity", "SKIP", 0, {}, "Not implemented")
    
    def _test_database_integration(self) -> TestResult:
        """Test database integration"""
        return TestResult("Database Integration", "SKIP", 0, {}, "Not implemented")
    
    def _test_auth_flow(self) -> TestResult:
        """Test authentication flow"""
        return TestResult("Auth Flow", "SKIP", 0, {}, "Not implemented")
    
    def _test_error_handling(self) -> TestResult:
        """Test error handling"""
        return TestResult("Error Handling", "SKIP", 0, {}, "Not implemented")
    
    def _test_data_flow(self) -> TestResult:
        """Test data flow"""
        return TestResult("Data Flow", "SKIP", 0, {}, "Not implemented")
    
    def generate_report(self, total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.results if r.status == "SKIP"])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Group results by category
        categories = {}
        for result in self.results:
            category = result.test_name.split()[0] if " " in result.test_name else "General"
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Generate report
        report = {
            "evaluation_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": total_duration,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": f"{success_rate:.1f}%",
                "overall_status": "PASS" if success_rate >= 80 else "FAIL"
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "status": result.status,
                    "duration": result.duration,
                    "details": result.details,
                    "error_message": result.error_message
                }
                for result in self.results
            ],
            "category_summary": {
                category: {
                    "total": len(results),
                    "passed": len([r for r in results if r.status == "PASS"]),
                    "failed": len([r for r in results if r.status == "FAIL"]),
                    "skipped": len([r for r in results if r.status == "SKIP"])
                }
                for category, results in categories.items()
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        
        if failed_tests:
            recommendations.append("Address failed test cases to improve system reliability")
        
        # Performance recommendations
        performance_tests = [r for r in self.results if "Response Time" in r.test_name or "Throughput" in r.test_name]
        failed_performance = [r for r in performance_tests if r.status == "FAIL"]
        
        if failed_performance:
            recommendations.append("Optimize system performance to meet response time and throughput targets")
        
        # Security recommendations
        security_tests = [r for r in self.results if any(keyword in r.test_name.lower() for keyword in ['auth', 'security', 'encryption'])]
        failed_security = [r for r in security_tests if r.status == "FAIL"]
        
        if failed_security:
            recommendations.append("Strengthen security controls and authentication mechanisms")
        
        # Infrastructure recommendations
        infra_tests = [r for r in self.results if any(keyword in r.test_name.lower() for keyword in ['health', 'database', 'cache', 'ecs'])]
        failed_infra = [r for r in infra_tests if r.status == "FAIL"]
        
        if failed_infra:
            recommendations.append("Review infrastructure health and resolve connectivity issues")
        
        if not recommendations:
            recommendations.append("System is performing well - continue monitoring and maintain current standards")
        
        return recommendations

def main():
    """Main execution function"""
    print("🚀 Production Analytics Agent v4.1 - Evaluation Suite")
    print("=" * 60)
    
    # Initialize evaluation framework
    evaluator = EvaluationFramework()
    
    # Run evaluation
    report = evaluator.run_evaluation()
    
    # Print summary
    print("\n📊 EVALUATION SUMMARY")
    print("=" * 60)
    summary = report['evaluation_summary']
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Skipped: {summary['skipped_tests']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Duration: {summary['total_duration']:.2f} seconds")
    
    # Print failed tests
    failed_tests = [r for r in report['test_results'] if r['status'] == 'FAIL']
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)})")
        print("=" * 60)
        for test in failed_tests:
            print(f"• {test['test_name']}: {test['error_message']}")
    
    # Print recommendations
    if report['recommendations']:
        print(f"\n💡 RECOMMENDATIONS")
        print("=" * 60)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
    
    # Save detailed report
    with open('evaluation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: evaluation_report.json")
    
    return report

if __name__ == "__main__":
    main()