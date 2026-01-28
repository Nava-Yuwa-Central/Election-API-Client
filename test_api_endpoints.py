#!/usr/bin/env python3
"""
Test script to verify API endpoints are working
"""

import requests
import json
import time

BASE_URL = "http://localhost:8195"

def test_endpoint(endpoint, description):
    """Test a single endpoint"""
    try:
        print(f"Testing {description}...")
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"  ✅ Success: {len(data)} items returned")
            elif isinstance(data, dict):
                print(f"  ✅ Success: Response received")
                if 'total' in data:
                    print(f"     Total items: {data.get('total', 'N/A')}")
            else:
                print(f"  ✅ Success: {type(data)} response")
        else:
            print(f"  ❌ Error: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connection Error: {e}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    print("🇳🇵 Nepal Entity Service - API Test")
    print("=" * 50)
    
    # Test health endpoint first
    test_endpoint("/health", "Health Check")
    
    # Test API endpoints
    test_endpoint("/api/v1/entities/", "All Entities")
    test_endpoint("/api/v1/entities/?entity_type=person", "Person Entities (Leaders)")
    test_endpoint("/api/v1/entities/?entity_type=political_party", "Political Party Entities")
    
    # Test frontend
    try:
        print("\nTesting Frontend...")
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("  ✅ Frontend accessible")
        else:
            print(f"  ❌ Frontend error: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Frontend error: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print(f"\n🌐 Access your application:")
    print(f"   Main App: {BASE_URL}")
    print(f"   API Docs: {BASE_URL}/docs")
    print(f"   Leaders: {BASE_URL}/leaders.html")
    print(f"   Parties: {BASE_URL}/parties.html")

if __name__ == "__main__":
    main()