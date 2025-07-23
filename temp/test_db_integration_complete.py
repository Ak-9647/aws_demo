#!/usr/bin/env python3
"""
Complete test script for database integration
Tests functionality with graceful handling of missing dependencies
"""

import sys
import os
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_integration_complete():
    """Complete test of database integration with dependency handling"""
    print("🚀 Complete Database Integration Test Suite")
    print("=" * 60)
    
    test_results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_details': []
    }
    
    def add_test_result(test_name: str, success: bool, message: str):
        test_results['total_tests'] += 1
        if success:
            test_results['passed_tests'] += 1
            print(f"✅ {test_name}: {message}")
        else:
            test_results['failed_tests'] += 1
            print(f"❌ {test_name}: {message}")
        
        test_results['test_details'].append({
            'test_name': test_name,
            'success': success,
            'message': message
        })
    
    try:
        # Add agent directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))
        
        # Test 1: Import database integration
        print("\n📋 Test 1: Module Import")
        try:
            from database_integration import DatabaseIntegration, get_database_integration
            add_test_result("Module Import", True, "Successfully imported database integration module")
        except ImportError as e:
            add_test_result("Module Import", False, f"Import failed: {str(e)}")
            return test_results
        
        # Test 2: Initialize database integration
        print("\n📋 Test 2: Initialization")
        try:
            db = DatabaseIntegration()
            add_test_result("Initialization", True, "Database integration initialized successfully")
            
            # Check attributes
            required_attrs = ['connection_string', 'schema_cache', 'query_cache']
            for attr in required_attrs:
                if hasattr(db, attr):
                    add_test_result(f"Attribute {attr}", True, f"{attr} attribute exists")
                else:
                    add_test_result(f"Attribute {attr}", False, f"{attr} attribute missing")
                    
        except Exception as e:
            add_test_result("Initialization", False, f"Initialization failed: {str(e)}")
            return test_results
        
        # Test 3: Singleton pattern
        print("\n📋 Test 3: Singleton Pattern")
        try:
            db1 = get_database_integration()
            db2 = get_database_integration()
            if db1 is db2:
                add_test_result("Singleton Pattern", True, "Singleton pattern working correctly")
            else:
                add_test_result("Singleton Pattern", False, "Singleton pattern failed - different instances returned")
        except Exception as e:
            add_test_result("Singleton Pattern", False, f"Singleton test failed: {str(e)}")
        
        # Test 4: Connection string generation
        print("\n📋 Test 4: Connection String Generation")
        try:
            conn_str = db.get_connection_string()
            if conn_str and isinstance(conn_str, str) and len(conn_str) > 0:
                if conn_str.startswith('postgresql://'):
                    add_test_result("Connection String Format", True, "Valid PostgreSQL connection string format")
                else:
                    add_test_result("Connection String Format", False, "Invalid connection string format")
                
                # Test masking function if it exists
                if hasattr(db, '_mask_connection_string'):
                    masked = db._mask_connection_string(conn_str)
                    if '***' in masked:
                        add_test_result("Connection String Masking", True, "Password masking working")
                    else:
                        add_test_result("Connection String Masking", False, "Password masking not working")
            else:
                add_test_result("Connection String Generation", False, "Connection string is empty or invalid")
        except Exception as e:
            add_test_result("Connection String Generation", False, f"Connection string generation failed: {str(e)}")
        
        # Test 5: Database connection test
        print("\n📋 Test 5: Database Connection Test")
        try:
            result = db.test_connection()
            if isinstance(result, dict) and 'success' in result:
                if result['success']:
                    add_test_result("Connection Test", True, f"Connection test passed: {result.get('message', 'No message')}")
                    
                    # Check response time
                    if 'response_time_ms' in result and result['response_time_ms'] > 0:
                        add_test_result("Response Time", True, f"Response time: {result['response_time_ms']}ms")
                    
                    # Check connection method
                    if 'connection_method' in result:
                        method = result['connection_method']
                        add_test_result("Connection Method", True, f"Using {method} connection method")
                else:
                    add_test_result("Connection Test", False, f"Connection test failed: {result.get('message', 'Unknown error')}")
            else:
                add_test_result("Connection Test", False, "Invalid connection test result format")
        except Exception as e:
            add_test_result("Connection Test", False, f"Connection test error: {str(e)}")
        
        # Test 6: Schema discovery
        print("\n📋 Test 6: Schema Discovery")
        try:
            schema = db.discover_schema()
            if isinstance(schema, dict):
                # Check for required fields
                required_fields = ['schemas', 'tables', 'total_tables', 'total_columns']
                all_fields_present = all(field in schema for field in required_fields)
                
                if all_fields_present:
                    add_test_result("Schema Structure", True, "Schema has all required fields")
                    
                    total_tables = schema.get('total_tables', 0)
                    total_columns = schema.get('total_columns', 0)
                    
                    if total_tables > 0:
                        add_test_result("Schema Content", True, f"Found {total_tables} tables with {total_columns} columns")
                    else:
                        add_test_result("Schema Content", False, "No tables found in schema")
                    
                    # Test schema caching
                    if hasattr(db, 'schema_cache') and db.schema_cache:
                        add_test_result("Schema Caching", True, "Schema cached successfully")
                    else:
                        add_test_result("Schema Caching", False, "Schema not cached")
                else:
                    missing_fields = [field for field in required_fields if field not in schema]
                    add_test_result("Schema Structure", False, f"Missing fields: {missing_fields}")
            else:
                add_test_result("Schema Discovery", False, "Schema discovery returned invalid format")
        except Exception as e:
            add_test_result("Schema Discovery", False, f"Schema discovery failed: {str(e)}")
        
        # Test 7: SQL generation from natural language
        print("\n📋 Test 7: SQL Generation")
        test_queries = [
            "Show me sales by region",
            "What are the top selling products?",
            "Analyze customer segments",
            "Give me a general overview"
        ]
        
        successful_generations = 0
        for i, query in enumerate(test_queries, 1):
            try:
                result = db.generate_sql_from_natural_language(query)
                if isinstance(result, dict) and result.get('success'):
                    successful_generations += 1
                    sql_query = result.get('sql_query', '')
                    if sql_query and 'select' in sql_query.lower():
                        add_test_result(f"SQL Gen Query {i}", True, f"Generated valid SQL for '{query[:30]}...'")
                    else:
                        add_test_result(f"SQL Gen Query {i}", False, f"Generated invalid SQL for '{query[:30]}...'")
                else:
                    add_test_result(f"SQL Gen Query {i}", False, f"Failed to generate SQL for '{query[:30]}...'")
            except Exception as e:
                add_test_result(f"SQL Gen Query {i}", False, f"SQL generation error: {str(e)}")
        
        success_rate = successful_generations / len(test_queries)
        add_test_result("SQL Generation Overall", success_rate >= 0.5, f"Success rate: {success_rate:.1%}")
        
        # Test 8: Query execution
        print("\n📋 Test 8: Query Execution")
        test_sql_queries = [
            "SELECT 1 as test_value",
            "SELECT 'hello' as greeting, 42 as number"
        ]
        
        successful_executions = 0
        for i, sql_query in enumerate(test_sql_queries, 1):
            try:
                result = db.execute_query(sql_query)
                if isinstance(result, dict) and result.get('success'):
                    successful_executions += 1
                    row_count = result.get('row_count', 0)
                    exec_time = result.get('execution_time_ms', 0)
                    add_test_result(f"Query Exec {i}", True, f"Executed successfully: {row_count} rows in {exec_time}ms")
                else:
                    add_test_result(f"Query Exec {i}", False, f"Execution failed: {result.get('message', 'Unknown error')}")
            except Exception as e:
                add_test_result(f"Query Exec {i}", False, f"Query execution error: {str(e)}")
        
        exec_success_rate = successful_executions / len(test_sql_queries)
        add_test_result("Query Execution Overall", exec_success_rate >= 0.5, f"Success rate: {exec_success_rate:.1%}")
        
        # Test 9: Error handling
        print("\n📋 Test 9: Error Handling")
        try:
            # Test with invalid SQL
            result = db.execute_query("INVALID SQL SYNTAX")
            if isinstance(result, dict):
                if not result.get('success'):
                    add_test_result("Error Handling", True, "Correctly handled invalid SQL")
                else:
                    add_test_result("Error Handling", False, "Invalid SQL should not succeed")
            else:
                add_test_result("Error Handling", False, "Invalid error handling response format")
        except Exception as e:
            add_test_result("Error Handling", True, "Correctly raised exception for invalid SQL")
        
        # Test 10: Performance and utility methods
        print("\n📋 Test 10: Utility Methods")
        try:
            # Test table extraction if method exists
            if hasattr(db, '_extract_tables_from_query'):
                tables = db._extract_tables_from_query("SELECT * FROM sales.transactions JOIN public.customers")
                if isinstance(tables, list) and len(tables) > 0:
                    add_test_result("Table Extraction", True, f"Extracted {len(tables)} tables from query")
                else:
                    add_test_result("Table Extraction", False, "Table extraction returned empty result")
            
            # Test complexity assessment if method exists
            if hasattr(db, '_assess_query_complexity'):
                complexity = db._assess_query_complexity("SELECT * FROM table")
                valid_complexities = ['simple', 'moderate', 'complex', 'very_complex']
                if complexity in valid_complexities:
                    add_test_result("Complexity Assessment", True, f"Assessed complexity as '{complexity}'")
                else:
                    add_test_result("Complexity Assessment", False, f"Invalid complexity assessment: {complexity}")
            
        except Exception as e:
            add_test_result("Utility Methods", False, f"Utility methods test failed: {str(e)}")
        
        # Generate final summary
        print("\n" + "=" * 60)
        print("📊 COMPLETE TEST SUMMARY")
        print("=" * 60)
        
        total = test_results['total_tests']
        passed = test_results['passed_tests']
        failed = test_results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Determine overall result
        if success_rate >= 80:
            print(f"\n🎯 OVERALL RESULT: ✅ EXCELLENT")
            print("Database integration is working excellently!")
        elif success_rate >= 60:
            print(f"\n🎯 OVERALL RESULT: ✅ GOOD")
            print("Database integration is working well with minor issues.")
        elif success_rate >= 40:
            print(f"\n🎯 OVERALL RESULT: ⚠️ FAIR")
            print("Database integration has some issues that should be addressed.")
        else:
            print(f"\n🎯 OVERALL RESULT: ❌ NEEDS WORK")
            print("Database integration needs significant improvements.")
        
        # Save detailed results
        results_file = 'database_integration_test_results.json'
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        return test_results
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return test_results

if __name__ == "__main__":
    results = test_database_integration_complete()
    success_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    sys.exit(0 if success_rate >= 60 else 1)