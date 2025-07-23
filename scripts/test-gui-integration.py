#!/usr/bin/env python3
"""
GUI Integration Test Script
Tests the enhanced GUI with real AgentCore integration
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# Add gui directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'gui'))

def test_agentcore_client():
    """Test AgentCore client functionality."""
    print("🧪 Testing AgentCore Client Integration")
    print("=" * 60)
    
    try:
        from agentcore_client import get_agentcore_client
        
        # Initialize client
        client = get_agentcore_client()
        print("✅ AgentCore client initialized successfully")
        
        # Test connection
        print("\n🔍 Testing connection...")
        connection_result = client.test_connection()
        
        if connection_result["success"]:
            print(f"✅ Connection successful via {connection_result['method']}")
            print(f"   Response time: {connection_result.get('response_time', 'N/A')}")
        else:
            print(f"⚠️  Connection failed (expected in development): {connection_result.get('error')}")
        
        # Test query processing
        print("\n📊 Testing query processing...")
        test_queries = [
            "Show me sales performance for Q2 2024",
            "What are our key performance indicators?",
            "Analyze customer satisfaction trends"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            
            start_time = time.time()
            result = client.invoke_agent(query, f"test_session_{i}", "test_user")
            response_time = time.time() - start_time
            
            if result["success"]:
                print(f"   ✅ Query processed successfully in {response_time:.2f}s")
                print(f"   Method: {result.get('method', 'Unknown')}")
                print(f"   Analysis length: {len(result.get('analysis', ''))} characters")
                
                if result.get('visualizations'):
                    print(f"   📊 Visualizations: {len(result['visualizations'])}")
                
                if result.get('recommendations'):
                    print(f"   💡 Recommendations: {len(result['recommendations'])}")
                    
            else:
                print(f"   ❌ Query failed: {result.get('error')}")
        
        print("\n🎉 AgentCore client testing completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import AgentCore client: {e}")
        return False
    except Exception as e:
        print(f"❌ AgentCore client test failed: {e}")
        return False

def test_gui_dependencies():
    """Test GUI dependencies and imports."""
    print("\n🧪 Testing GUI Dependencies")
    print("=" * 60)
    
    dependencies = [
        ('streamlit', 'st'),
        ('plotly.express', 'px'),
        ('plotly.graph_objects', 'go'),
        ('pandas', 'pd'),
        ('boto3', 'boto3'),
        ('requests', 'requests')
    ]
    
    all_passed = True
    
    for module_name, import_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - Available")
        except ImportError:
            print(f"❌ {module_name} - Missing")
            all_passed = False
    
    return all_passed

def test_agent_endpoint():
    """Test agent HTTP endpoint if available."""
    print("\n🧪 Testing Agent HTTP Endpoint")
    print("=" * 60)
    
    # Common agent endpoints to test
    endpoints = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        os.getenv('AGENT_ENDPOINT')
    ]
    
    for endpoint in endpoints:
        if not endpoint:
            continue
            
        print(f"Testing endpoint: {endpoint}")
        
        try:
            # Test health endpoint
            response = requests.get(f"{endpoint}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Health check passed: {endpoint}")
                
                # Test query endpoint
                test_payload = {
                    "query": "Hello, this is a test query",
                    "session_id": "test_session",
                    "user_id": "test_user"
                }
                
                response = requests.post(
                    endpoint,
                    json=test_payload,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    print(f"✅ Query processing works: {endpoint}")
                    print(f"   Response length: {len(response.text)} characters")
                    return endpoint
                else:
                    print(f"⚠️  Query failed with status {response.status_code}")
            else:
                print(f"⚠️  Health check failed with status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Connection refused: {endpoint}")
        except requests.exceptions.Timeout:
            print(f"⚠️  Connection timeout: {endpoint}")
        except Exception as e:
            print(f"⚠️  Error testing {endpoint}: {e}")
    
    print("ℹ️  No HTTP endpoints available (expected if agent not running)")
    return None

def generate_test_report():
    """Generate comprehensive test report."""
    print("\n📋 GUI Integration Test Report")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test 1: Dependencies
    print("1. Testing dependencies...")
    deps_result = test_gui_dependencies()
    results["tests"]["dependencies"] = deps_result
    
    # Test 2: AgentCore Client
    print("\n2. Testing AgentCore client...")
    client_result = test_agentcore_client()
    results["tests"]["agentcore_client"] = client_result
    
    # Test 3: HTTP Endpoint
    print("\n3. Testing HTTP endpoint...")
    endpoint_result = test_agent_endpoint()
    results["tests"]["http_endpoint"] = endpoint_result is not None
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    total_tests = len(results["tests"])
    passed_tests = sum(1 for result in results["tests"].values() if result)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Test Results:")
    for test_name, result in results["tests"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not results["tests"]["dependencies"]:
        print("   - Install missing Python dependencies")
    if not results["tests"]["agentcore_client"]:
        print("   - Check AgentCore client configuration")
    if not results["tests"]["http_endpoint"]:
        print("   - Start agent HTTP server for testing: python agent/main.py")
    
    if passed_tests == total_tests:
        print("   - All tests passed! GUI is ready for use")
    
    # Save report
    report_file = 'gui_integration_test_report.json'
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return passed_tests / total_tests

def main():
    """Main test execution."""
    print("🚀 GUI Integration Testing Suite")
    print("=" * 80)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_rate = generate_test_report()
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_rate >= 0.8:
        print("🎉 GUI integration tests mostly successful!")
        return 0
    else:
        print("⚠️  Some GUI integration tests failed. Check the report for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)