#!/usr/bin/env python3
"""
Test script for Structura.AI Backend API
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TEXT = '''
"Be the change you wish to see in the world." - Mahatma Gandhi
Albert Einstein once said, "Imagination is more important than knowledge."
> This is a block quote that should be extracted from the text
"Hello," said John. "How are you today?"
'''

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def test_quote_extraction():
    """Test quote extraction endpoint"""
    print("\n🔍 Testing quote extraction...")
    try:
        response = requests.post(
            f"{BASE_URL}/extract-quotes",
            json={"text": TEST_TEXT}
        )
        if response.status_code == 200:
            print("✅ Quote extraction passed")
            result = response.json()
            print(f"   Total quotes found: {result.get('total_quotes', 0)}")
            print(f"   Text length: {result.get('text_length', 0)}")
            
            # Display extracted quotes
            quotes = result.get('quotes', [])
            for i, quote in enumerate(quotes, 1):
                print(f"   Quote {i}: {quote.get('text', '')[:50]}...")
                if quote.get('author'):
                    print(f"      Author: {quote.get('author')}")
        else:
            print(f"❌ Quote extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Quote extraction error: {e}")

def test_api_info():
    """Test API information endpoint"""
    print("\n🔍 Testing API info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/info")
        if response.status_code == 200:
            print("✅ API info endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API info endpoint error: {e}")

def test_pdf_extraction():
    """Test PDF extraction endpoint"""
    print("\n🔍 Testing PDF extraction endpoint...")
    try:
        # Test with a sample PDF file if available
        test_pdf_path = "test_pdfs/PF1_Machine_Specifications.xlsx"
        if os.path.exists(test_pdf_path):
            with open(test_pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{BASE_URL}/extract-pdf", files=files)
                if response.status_code == 200:
                    print("✅ PDF extraction passed")
                    result = response.json()
                    print(f"   Filename: {result.get('filename', 'N/A')}")
                    print(f"   Technical fields: {result.get('technical_fields', 0)}")
                    print(f"   Commercial fields: {result.get('commercial_fields', 0)}")
                    print(f"   Basic fields: {result.get('basic_fields', 0)}")
                else:
                    print(f"❌ PDF extraction failed: {response.status_code}")
                    print(f"   Error: {response.text}")
        else:
            print("⚠️ No test PDF file found, skipping PDF extraction test")
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")

def test_invalid_request():
    """Test invalid request handling"""
    print("\n🔍 Testing invalid request handling...")
    try:
        response = requests.post(
            f"{BASE_URL}/extract-quotes",
            json={}  # Empty request
        )
        if response.status_code == 400:
            print("✅ Invalid request properly handled")
            print(f"   Error: {response.json()}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid request test error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Structura.AI Backend API Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    test_health_endpoint()
    test_root_endpoint()
    test_quote_extraction()
    test_api_info()
    test_pdf_extraction()
    test_invalid_request()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main() 