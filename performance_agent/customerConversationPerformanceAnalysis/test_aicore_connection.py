#!/usr/bin/env python3
"""
Test script to diagnose AI Core connection issues
"""

import json
import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.aicore_service import get_aicore_client, AICoreCredentialsLoader
import requests

def test_aicore_endpoints():
    """Test different AI Core endpoints to find the correct one"""
    
    print("=" * 80)
    print("AI CORE CONNECTION DIAGNOSTICS")
    print("=" * 80)
    
    try:
        # Load credentials
        loader = AICoreCredentialsLoader()
        credentials = loader.load_credentials()
        
        print(f"✓ Loaded credentials successfully")
        print(f"  AI API URL: {credentials['services']['ai_api_url']}")
        print(f"  Auth URL: {credentials['oauth']['url']}")
        print(f"  Client ID: {credentials['oauth']['clientid'][:20]}...")
        
        # Test authentication
        print("\n" + "=" * 50)
        print("TESTING AUTHENTICATION")
        print("=" * 50)
        
        client = get_aicore_client()
        access_token = client.authenticator.get_access_token()
        print(f"✓ Successfully obtained access token: {access_token[:50]}...")
        
        # Test different endpoints
        base_url = credentials['services']['ai_api_url']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"\n" + "=" * 50)
        print("TESTING API ENDPOINTS")
        print("=" * 50)
        
        # List of potential endpoints to test
        test_endpoints = [
            "/v1/models",
            "/v1/chat/completions", 
            "/v2/inference/deployments",
            "/v2/lm/deployments",
            "/inference/deployments",
            "/lm/deployments",
            "/deployments",
            "/health",
            "/v1/health",
            "/v2/health"
        ]
        
        successful_endpoints = []
        
        for endpoint in test_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"\nTesting: {endpoint}")
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"  ✓ SUCCESS (200): {endpoint}")
                    try:
                        data = response.json()
                        print(f"    Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        successful_endpoints.append((endpoint, data))
                    except:
                        print(f"    Response: {response.text[:200]}")
                elif response.status_code == 404:
                    print(f"  ✗ NOT FOUND (404): {endpoint}")
                elif response.status_code == 401:
                    print(f"  ✗ UNAUTHORIZED (401): {endpoint}")
                elif response.status_code == 403:
                    print(f"  ✗ FORBIDDEN (403): {endpoint}")
                else:
                    print(f"  ? RESPONSE ({response.status_code}): {endpoint}")
                    print(f"    {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ✗ ERROR: {endpoint} - {e}")
        
        print(f"\n" + "=" * 50)
        print("SUCCESSFUL ENDPOINTS")
        print("=" * 50)
        
        if successful_endpoints:
            for endpoint, data in successful_endpoints:
                print(f"✓ {endpoint}")
                if isinstance(data, dict):
                    # Show structure of successful responses
                    if 'data' in data and isinstance(data['data'], list):
                        print(f"  Contains {len(data['data'])} items")
                        if data['data']:
                            first_item = data['data'][0]
                            if isinstance(first_item, dict):
                                print(f"  First item keys: {list(first_item.keys())}")
                    elif 'deployments' in data:
                        print(f"  Contains deployments: {len(data['deployments'])}")
                    else:
                        print(f"  Keys: {list(data.keys())}")
        else:
            print("No successful endpoints found!")
        
        # Test a simple chat completion with different endpoints
        print(f"\n" + "=" * 50)
        print("TESTING CHAT COMPLETION ENDPOINTS")
        print("=" * 50)
        
        test_message = {
            "messages": [
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            "model": "gpt-3.5-turbo",  # Generic model name
            "temperature": 0.1,
            "max_tokens": 50
        }
        
        chat_endpoints = [
            "/v1/chat/completions",
            "/v2/inference/deployments/{deployment_id}/chat/completions",
            "/inference/chat/completions",
            "/chat/completions"
        ]
        
        for endpoint in chat_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"\nTesting chat: {endpoint}")
                
                response = requests.post(url, headers=headers, json=test_message, timeout=30)
                
                if response.status_code == 200:
                    print(f"  ✓ CHAT SUCCESS (200): {endpoint}")
                    try:
                        data = response.json()
                        print(f"    Response keys: {list(data.keys())}")
                    except:
                        print(f"    Response: {response.text[:200]}")
                else:
                    print(f"  ✗ CHAT FAILED ({response.status_code}): {endpoint}")
                    print(f"    {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ✗ CHAT ERROR: {endpoint} - {e}")
        
        return successful_endpoints
        
    except Exception as e:
        print(f"✗ Error during diagnostics: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_health_check():
    """Test the health check functionality"""
    try:
        print(f"\n" + "=" * 50)
        print("HEALTH CHECK TEST")
        print("=" * 50)
        
        client = get_aicore_client()
        health_status = client.health_check()
        
        print("Health Check Result:")
        print(json.dumps(health_status, indent=2, default=str))
        
        return health_status
        
    except Exception as e:
        print(f"Health check failed: {e}")
        return None

def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)
    
    # Test endpoints
    successful_endpoints = test_aicore_endpoints()
    
    # Test health check
    health_status = test_health_check()
    
    print(f"\n" + "=" * 50)
    print("RECOMMENDATIONS")
    print("=" * 50)
    
    if successful_endpoints:
        print("✓ Found working endpoints! Consider updating the AI Core service to use:")
        for endpoint, _ in successful_endpoints:
            print(f"  - {endpoint}")
    else:
        print("✗ No working endpoints found. Check:")
        print("  1. AI Core credentials are correct")
        print("  2. AI Core service is deployed and running")
        print("  3. Your tenant has the necessary permissions")
        print("  4. The AI API URL is correct for your region/environment")
    
    if health_status and health_status.get('status') == 'healthy':
        print("✓ Health check passed")
    else:
        print("✗ Health check failed - service may not be properly configured")

if __name__ == "__main__":
    main()
