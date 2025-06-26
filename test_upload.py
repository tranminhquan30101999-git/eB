#!/usr/bin/env python3
"""
Test file upload to verify the knowledge base endpoint is working
"""

import requests
import tempfile
import os

def test_upload_endpoint():
    """Test the upload endpoint with a simple text file"""
    API_BASE_URL = "http://localhost:8080/api/v1"
    
    # Create a simple test file
    test_content = "This is a test document for the nail salon knowledge base.\n\nThis document contains information about nail care procedures."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        print("Testing upload endpoint...")
        print(f"API URL: {API_BASE_URL}/knowledge/documents/upload")
        
        # Test file upload
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'title': 'Test Document', 'tags': 'test,demo'}
            
            response = requests.post(
                f"{API_BASE_URL}/knowledge/documents/upload",
                files=files,
                data=data,
                timeout=10
            )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Upload successful!")
            print(f"Result: {result}")
        else:
            print(f"✗ Upload failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed: Backend server is not running on localhost:8080")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Clean up temp file
        os.unlink(temp_file)

def test_health_endpoint():
    """Test the health endpoint"""
    API_BASE_URL = "http://localhost:8080/api/v1"
    
    try:
        print("Testing health endpoint...")
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✓ Health check passed!")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed: Backend server is not running")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Backend Upload Functionality")
    print("=" * 50)
    
    test_health_endpoint()
    print()
    test_upload_endpoint()