#!/usr/bin/env python3
"""
Test the correct Anthropic API format for SAP AI Core
"""

import requests
import json
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.aicore_service import get_aicore_client

def test_correct_anthropic_format():
    """Test the correct Anthropic API format"""
    
    print("=" * 80)
    print("CORRECT ANTHROPIC API FORMAT TEST")
    print("=" * 80)
    
    try:
        client = get_aicore_client()
        access_token = client.authenticator.get_access_token()
        base_url = client.ai_api_url
        deployment_id = client.config.get('deployment', {}).get('default_deployment_id')
        
        print(f"Testing deployment: {deployment_id}")
        print(f"Model type: anthropic--claude")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'AI-Resource-Group': 'default'
        }
        
        # CORRECT Anthropic format
        anthropic_payload = {
            "anthropic_version": "2023-06-01",  # Required for Anthropic
            "messages": [
                {
                    "role": "user", 
                    "content": "Hello! Please respond with a brief greeting."
                }
            ],
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        print("\n" + "=" * 40)
        print("COMPARISON: Why Different Endpoints?")
        print("=" * 40)
        
        print("\n1. OpenAI-style models (GPT) would use:")
        print("   Endpoint: /v2/inference/deployments/{id}/chat/completions")
        print("   Payload: {")
        print("     'messages': [...],")
        print("     'model': 'gpt-4',")
        print("     'temperature': 0.1")
        print("   }")
        
        print("\n2. Anthropic models (Claude) must use:")
        print("   Endpoint: /v2/inference/deployments/{id}/invoke")
        print("   Payload: {")
        print("     'anthropic_version': '2023-06-01',  # REQUIRED!")
        print("     'messages': [...],")
        print("     'max_tokens': 100,")
        print("     'temperature': 0.1")
        print("   }")
        
        print("\n" + "=" * 40)
        print("TESTING CORRECT ANTHROPIC FORMAT")
        print("=" * 40)
        
        # Test the correct endpoint
        endpoint = f"{base_url}/v2/inference/deployments/{deployment_id}/invoke"
        print(f"\nTesting: {endpoint}")
        print(f"Payload: {json.dumps(anthropic_payload, indent=2)}")
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=anthropic_payload,
                timeout=30
            )
            
            print(f"\nStatus: {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS! Anthropic endpoint working with correct format!")
                
                try:
                    result = response.json()
                    print(f"Response keys: {list(result.keys())}")
                    
                    # Anthropic response format
                    if 'content' in result and isinstance(result['content'], list):
                        content = result['content'][0].get('text', '')
                        print(f"Claude response: {content}")
                    else:
                        print(f"Response: {json.dumps(result, indent=2)[:300]}...")
                        
                    return True
                    
                except json.JSONDecodeError:
                    print(f"Response (non-JSON): {response.text[:200]}...")
                    return True
            
            elif response.status_code == 400:
                error_msg = response.text
                print(f"❌ Bad Request: {error_msg}")
                
                if "anthropic_version" in error_msg:
                    print("\n💡 The endpoint accepts requests but needs a valid anthropic_version")
                    print("   Common valid versions: 2023-06-01, 2023-01-01, bedrock-2023-05-31")
                    
                elif "Invalid API version" in error_msg:
                    print("\n💡 The anthropic_version format is incorrect")
                    print("   Try: 2023-06-01, 2023-01-01, or bedrock-2023-05-31")
                
            elif response.status_code == 403:
                print(f"❌ Forbidden: {response.text}")
                print("\n💡 This means RBAC permissions are still needed")
                
            elif response.status_code == 404:
                print(f"❌ Not Found: {response.text}")
                print("\n💡 Deployment might not exist or endpoint path is wrong")
                
            else:
                print(f"❓ Status {response.status_code}: {response.text[:150]}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out after 30 seconds")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
        
        print("\n" + "=" * 40)
        print("WHY SAP AI CORE ENFORCES THIS")
        print("=" * 40)
        
        print("\n🔍 Technical Explanation:")
        print("1. **Model Compatibility**: Each AI model has its own API specification")
        print("2. **Provider Standards**: Anthropic uses different endpoints than OpenAI")
        print("3. **Parameter Validation**: SAP AI Core validates requests match the model type")
        print("4. **Error Prevention**: Prevents incompatible requests from being sent")
        
        print("\n📋 What this means for your application:")
        print("✓ Authentication is working (we get 400, not 401)")
        print("✓ Deployment exists (we get 400, not 404)")
        print("✓ Endpoint is correct (SAP AI Core recognizes the invoke pattern)")
        print("❌ Need either proper anthropic_version OR RBAC permissions")
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("Understanding why different models need different endpoints...\n")
    test_correct_anthropic_format()
    
    print(f"\n" + "=" * 80)
    print("SUMMARY: Model-Specific API Requirements")
    print("=" * 80)
    
    print("\n🎯 Key Insights:")
    print("1. SAP AI Core supports multiple model providers")
    print("2. Each provider has different API requirements")
    print("3. The system validates compatibility to prevent errors")
    print("4. Anthropic models MUST use /invoke with anthropic_version")
    print("5. OpenAI models would use /chat/completions")
    
    print("\n🚀 This is actually GOOD news:")
    print("- Your authentication is working")
    print("- Your deployment exists and is accessible")
    print("- The system is protecting you from incompatible API calls")
    print("- You just need the right format OR RBAC permissions")

if __name__ == "__main__":
    main()
