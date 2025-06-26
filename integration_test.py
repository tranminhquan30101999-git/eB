#!/usr/bin/env python3
"""
Integration Test Script for Nail Salon Knowledge Base System

This script tests the basic functionality of the integrated system:
1. Backend API endpoints
2. Knowledge base functionality
3. Database connectivity

Run this script after starting the backend server to verify integration.
"""

import requests
import json
import sys
from pathlib import Path

API_BASE_URL = "http://localhost:8080/api/v1"

def test_api_health():
    """Test if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API Health Check: PASSED")
            return True
        else:
            print(f"✗ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ API Health Check: FAILED (Error: {e})")
        return False

def test_services_endpoint():
    """Test the services endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/services", timeout=5)
        if response.status_code == 200:
            services = response.json()
            print(f"✓ Services Endpoint: PASSED ({len(services)} services found)")
            return True
        else:
            print(f"✗ Services Endpoint: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Services Endpoint: FAILED (Error: {e})")
        return False

def test_knowledge_base_endpoints():
    """Test knowledge base endpoints"""
    try:
        # Test getting documents
        response = requests.get(f"{API_BASE_URL}/knowledge/documents", timeout=5)
        if response.status_code == 200:
            documents = response.json()
            print(f"✓ Knowledge Documents Endpoint: PASSED ({len(documents)} documents found)")
            
            # Test search endpoint
            search_response = requests.get(f"{API_BASE_URL}/knowledge/search?query=test", timeout=5)
            if search_response.status_code == 200:
                print("✓ Knowledge Search Endpoint: PASSED")
                return True
            else:
                print(f"✗ Knowledge Search Endpoint: FAILED (Status: {search_response.status_code})")
                return False
        else:
            print(f"✗ Knowledge Documents Endpoint: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Knowledge Base Endpoints: FAILED (Error: {e})")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    try:
        chat_data = {
            "message": "Xin chào",
            "conversation_id": "test-conversation"
        }
        response = requests.post(
            f"{API_BASE_URL}/chat", 
            json=chat_data, 
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                print("✓ Chat Endpoint: PASSED")
                return True
            else:
                print("✗ Chat Endpoint: FAILED (No response field)")
                return False
        else:
            print(f"✗ Chat Endpoint: FAILED (Status: {response.status_code})")
            # Print response content for debugging
            try:
                error_detail = response.json()
                print(f"   Error detail: {error_detail}")
            except:
                print(f"   Error text: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Chat Endpoint: FAILED (Error: {e})")
        return False

def main():
    """Run all integration tests"""
    print("🧪 Running Integration Tests for Nail Salon Knowledge Base System")
    print("=" * 60)
    
    tests = [
        test_api_health,
        test_services_endpoint,
        test_knowledge_base_endpoints,
        test_chat_endpoint,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the backend server and configuration.")
        print("\nTroubleshooting:")
        print("1. Make sure the backend server is running on http://localhost:8080")
        print("2. Check that the database is initialized (run: python init_data.py)")
        print("3. Verify that OPENAI_API_KEY is set in .env file")
        print("4. Check server logs for any errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())