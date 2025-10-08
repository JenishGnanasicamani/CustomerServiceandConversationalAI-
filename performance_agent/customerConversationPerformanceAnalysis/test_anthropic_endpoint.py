#!/usr/bin/env python3
"""
Test the Anthropic-specific endpoint with proper parameters
"""

import requests
import json
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.aicore_service import get_aicore_client

def test_anthropic_invoke_endpoint():
    """Test the Anthropic invoke endpoint with proper parameters"""
    
    print("=" * 70)
    print("ANTHROPIC ENDPOINT TEST")
    print("=" * 70)
    
    try:
        client = get_aicore_client()
        access_token = client.authenticator.get_access_token()
        base_url = client.ai_api_url
        deployment_id = client.config.get('deployment', {}).get('default_deployment_id')
        
        print(f"Testing Anthropic endpoint with deployment: {deployment_id}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'AI-Resource-Group': 'default'
        }
        
        # Anthropic-specific payload with required anthropic_version
        anthropic_payloads = [
            {
                "anthropic_version": "2023-06-01",
                "messages": [
                    {"role": "user", "content": "Hello, this is a test message for conversation analysis."}
                ],
                "max_tokens": 100,
                "temperature": 0.1
            },
            {
                "anthropic_version": "2024-01-01", 
                "messages": [
                    {"role": "user", "content": "Analyze this customer conversation for quality."}
                ],
                "max_tokens": 150,
                "temperature": 0.1
            },
            {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {"role": "user", "content": "Test message"}
                ],
                "max_tokens": 50
            }
        ]
        
        # Test the /v2/inference/deployments/{id}/invoke endpoint
        endpoint = f"{base_url}/v2/inference/deployments/{deployment_id}/invoke"
        
        for i, payload in enumerate(anthropic_payloads, 1):
            print(f"\n--- Test {i}: anthropic_version = {payload['anthropic_version']} ---")
            
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("🎉 SUCCESS! AI Core is working!")
                    
                    try:
                        result = response.json()
                        print(f"Response keys: {list(result.keys())}")
                        
                        # Handle different response formats
                        if 'content' in result:
                            if isinstance(result['content'], list) and result['content']:
                                content = result['content'][0].get('text', '')
                                print(f"Response content: {content[:200]}...")
                            else:
                                print(f"Content: {result['content']}")
                                
                        elif 'choices' in result and result['choices']:
                            content = result['choices'][0].get('message', {}).get('content', '')
                            print(f"Response content: {content[:200]}...")
                            
                        elif 'completion' in result:
                            print(f"Completion: {result['completion'][:200]}...")
                            
                        else:
                            print(f"Full response: {json.dumps(result, indent=2)[:500]}...")
                        
                        return True, payload['anthropic_version']
                        
                    except json.JSONDecodeError:
                        print(f"Response (non-JSON): {response.text[:300]}...")
                        return True, payload['anthropic_version']
                
                elif response.status_code == 400:
                    print(f"❌ Bad Request: {response.text[:150]}")
                    
                elif response.status_code == 403:
                    print(f"❌ Forbidden: {response.text[:150]}")
                    
                elif response.status_code == 422:
                    print(f"❌ Validation Error: {response.text[:150]}")
                    
                else:
                    print(f"❓ Status {response.status_code}: {response.text[:150]}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout after 30 seconds")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Request Error: {e}")
        
        return False, None
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, None

def main():
    success, working_version = test_anthropic_invoke_endpoint()
    
    print(f"\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)
    
    if success:
        print(f"🎉 AI CORE CONNECTION IS WORKING!")
        print(f"✅ Working endpoint: /v2/inference/deployments/{{id}}/invoke")
        print(f"✅ Working anthropic_version: {working_version}")
        print(f"✅ Authentication: SUCCESS")
        print(f"✅ Authorization: SUCCESS") 
        print(f"✅ Real AI responses: ENABLED")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Update the aicore_service.py to use this working endpoint")
        print(f"2. Add anthropic_version parameter to requests")
        print(f"3. Test with the conversation analysis system")
        
    else:
        print(f"❌ AI Core connection still has issues")
        print(f"The system will continue using fallback responses.")
        
        print(f"\n🔍 DIAGNOSTIC INFO:")
        print(f"- Authentication: Working (getting tokens)")
        print(f"- Some endpoints: RBAC denied (403)")
        print(f"- Anthropic endpoint: Accepts requests but needs proper format")
        print(f"- May need different payload structure or additional parameters")
    
    return success

if __name__ == "__main__":
    main()
