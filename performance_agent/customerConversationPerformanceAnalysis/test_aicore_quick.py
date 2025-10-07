#!/usr/bin/env python3
"""
Quick AI Core connection test with alternative endpoints
"""

import requests
import json
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.aicore_service import get_aicore_client

def test_alternative_endpoints():
    """Test alternative AI Core endpoints"""
    
    print("=" * 60)
    print("QUICK AI CORE CONNECTION TEST")
    print("=" * 60)
    
    try:
        client = get_aicore_client()
        access_token = client.authenticator.get_access_token()
        base_url = client.ai_api_url
        deployment_id = client.config.get('deployment', {}).get('default_deployment_id')
        
        print(f"Testing with deployment: {deployment_id}")
        print(f"Model: {client.default_model}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'AI-Resource-Group': 'default'
        }
        
        # Test message
        test_payload = {
            "messages": [
                {"role": "user", "content": "Hello, test message"}
            ],
            "temperature": 0.1,
            "max_tokens": 100
        }
        
        # Alternative endpoints to try
        endpoints_to_test = [
            # Standard endpoints
            f"/v2/lm/deployments/{deployment_id}/chat/completions",
            f"/v2/inference/deployments/{deployment_id}/chat/completions",
            f"/v2/lm/deployments/{deployment_id}/completions",
            
            # Alternative patterns
            f"/v2/lm/deployments/{deployment_id}/invoke",
            f"/v2/inference/deployments/{deployment_id}/invoke",
            f"/v2/deployments/{deployment_id}/chat/completions",
            f"/v2/deployments/{deployment_id}/completions",
            f"/v2/deployments/{deployment_id}/invoke",
            
            # Simple patterns
            f"/lm/deployments/{deployment_id}/chat/completions",
            f"/inference/deployments/{deployment_id}/chat/completions",
            f"/deployments/{deployment_id}/chat/completions",
            f"/deployments/{deployment_id}/invoke",
            
            # Direct model access (if supported)
            f"/v2/models/{client.default_model}/chat/completions",
            f"/v2/models/chat/completions",
            f"/models/{client.default_model}/chat/completions",
            f"/models/chat/completions",
        ]
        
        working_endpoints = []
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            
            try:
                print(f"\nTesting: {endpoint}")
                
                response = requests.post(
                    url,
                    headers=headers,
                    json=test_payload,
                    timeout=10
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS!")
                    try:
                        result = response.json()
                        print(f"  Response keys: {list(result.keys())}")
                        if 'choices' in result and result['choices']:
                            content = result['choices'][0].get('message', {}).get('content', '')
                            print(f"  Content: {content[:100]}...")
                        working_endpoints.append(endpoint)
                        return True  # Found a working endpoint!
                    except:
                        print(f"  Response: {response.text[:150]}")
                        
                elif response.status_code == 400:
                    print(f"  ❌ Bad Request: {response.text[:100]}")
                elif response.status_code == 401:
                    print(f"  ❌ Unauthorized: {response.text[:100]}")
                elif response.status_code == 403:
                    print(f"  ❌ Forbidden: {response.text[:100]}")
                elif response.status_code == 404:
                    print(f"  ❌ Not Found")
                elif response.status_code == 422:
                    print(f"  ❌ Validation Error: {response.text[:100]}")
                else:
                    print(f"  ❓ Status {response.status_code}: {response.text[:100]}")
                    
            except requests.exceptions.Timeout:
                print(f"  ⏰ Timeout")
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Request Error: {e}")
        
        if working_endpoints:
            print(f"\n🎉 Found {len(working_endpoints)} working endpoints!")
            for ep in working_endpoints:
                print(f"  ✅ {ep}")
            return True
        else:
            print(f"\n❌ No working endpoints found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    success = test_alternative_endpoints()
    
    if success:
        print(f"\n🎉 AI Core connection is working!")
        print(f"The service should now use real AI responses instead of fallbacks.")
    else:
        print(f"\n❌ AI Core connection still has issues")
        print(f"The system will continue using fallback responses.")
        print(f"\nThis could be due to:")
        print(f"  1. RBAC permissions still not granted") 
        print(f"  2. Model deployment not properly configured")
        print(f"  3. Different API endpoint pattern required")
        print(f"  4. Additional headers or authentication needed")
    
    return success

if __name__ == "__main__":
    main()
