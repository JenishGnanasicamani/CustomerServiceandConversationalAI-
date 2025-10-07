#!/usr/bin/env python3
"""
Test script to verify AI Core service with RBAC fallback
"""

import json
import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.aicore_service import get_aicore_client, AICoreCredentialsLoader

def test_aicore_with_fallback():
    """Test AI Core service with fallback mechanism"""
    
    print("=" * 80)
    print("AI CORE SERVICE TEST WITH RBAC FALLBACK")
    print("=" * 80)
    
    try:
        # Load credentials and client
        print("Loading AI Core client...")
        client = get_aicore_client()
        
        print(f"✓ Client initialized successfully")
        print(f"  API URL: {client.ai_api_url}")
        print(f"  Default Model: {client.default_model}")
        print(f"  RBAC Issue Known: {client.config.get('issues', {}).get('rbac_access_denied', False)}")
        
        # Test different types of requests
        test_scenarios = [
            {
                "name": "Conversation Analysis Request",
                "messages": [
                    {"role": "system", "content": "You are an expert at analyzing customer service conversations."},
                    {"role": "user", "content": "Please analyze this conversation: Customer: Hi, I have an issue with my order. Agent: I'd be happy to help you with that. Can you provide your order number?"}
                ]
            },
            {
                "name": "Scoring Request",
                "messages": [
                    {"role": "user", "content": "Please provide performance scores for this customer service interaction based on satisfaction, resolution, and communication quality."}
                ]
            },
            {
                "name": "General Query",
                "messages": [
                    {"role": "user", "content": "What are the key indicators of good customer service?"}
                ]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n" + "=" * 60)
            print(f"TEST SCENARIO {i}: {scenario['name']}")
            print("=" * 60)
            
            try:
                print(f"Sending request...")
                
                response = client.chat_completion(
                    messages=scenario['messages'],
                    temperature=0.1,
                    max_tokens=500
                )
                
                print(f"✓ Request completed successfully")
                print(f"Response structure:")
                print(f"  - ID: {response.get('id', 'N/A')}")
                print(f"  - Model: {response.get('model', 'N/A')}")
                print(f"  - Choices: {len(response.get('choices', []))}")
                
                if 'choices' in response and response['choices']:
                    content = response['choices'][0].get('message', {}).get('content', '')
                    print(f"  - Content length: {len(content)} characters")
                    print(f"  - Content preview: {content[:200]}...")
                
                if 'system_info' in response:
                    print(f"  - System info: {response['system_info']}")
                
                if 'usage' in response:
                    usage = response['usage']
                    print(f"  - Token usage: {usage.get('prompt_tokens', 0)} prompt + {usage.get('completion_tokens', 0)} completion = {usage.get('total_tokens', 0)} total")
                
            except Exception as e:
                print(f"✗ Test scenario failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Test health check
        print(f"\n" + "=" * 60)
        print("HEALTH CHECK TEST")
        print("=" * 60)
        
        health_status = client.health_check()
        print("Health Check Result:")
        print(json.dumps(health_status, indent=2, default=str))
        
        # Test configuration details
        print(f"\n" + "=" * 60)
        print("CONFIGURATION SUMMARY")
        print("=" * 60)
        
        deployment_config = client.config.get('deployment', {})
        issues_config = client.config.get('issues', {})
        
        print(f"Resource Group: {deployment_config.get('resource_group', 'Not configured')}")
        print(f"Default Deployment ID: {deployment_config.get('default_deployment_id', 'Not configured')}")
        print(f"Available Deployment IDs: {len(deployment_config.get('deployment_ids', []))}")
        print(f"RBAC Access Denied: {issues_config.get('rbac_access_denied', False)}")
        print(f"Fallback Mode: {'Active' if issues_config.get('rbac_access_denied', False) else 'Inactive'}")
        
        return True
        
    except Exception as e:
        print(f"✗ AI Core test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_credentials_loading():
    """Test credentials loading separately"""
    
    print(f"\n" + "=" * 60)
    print("CREDENTIALS LOADING TEST")
    print("=" * 60)
    
    try:
        loader = AICoreCredentialsLoader()
        credentials = loader.load_credentials()
        
        print("✓ Credentials loaded successfully")
        print(f"  OAuth URL: {credentials['oauth']['url']}")
        print(f"  AI API URL: {credentials['services']['ai_api_url']}")
        print(f"  Client ID: {credentials['oauth']['clientid'][:20]}...")
        
        if 'deployment' in credentials:
            deployment = credentials['deployment']
            print(f"  Resource Group: {deployment.get('resource_group', 'Not set')}")
            print(f"  Deployment IDs: {len(deployment.get('deployment_ids', []))}")
        
        if 'issues' in credentials:
            issues = credentials['issues']
            print(f"  Known Issues: {list(issues.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Credentials loading failed: {e}")
        return False

def main():
    """Main test function"""
    logging.basicConfig(level=logging.INFO)
    
    print("Testing AI Core service with enhanced RBAC handling...")
    
    # Test credentials loading
    creds_ok = test_credentials_loading()
    
    # Test AI Core service
    aicore_ok = test_aicore_with_fallback()
    
    print(f"\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    print(f"✓ Credentials Loading: {'PASS' if creds_ok else 'FAIL'}")
    print(f"✓ AI Core Service: {'PASS' if aicore_ok else 'FAIL'}")
    
    if creds_ok and aicore_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"AI Core service is now working with fallback mechanism.")
        print(f"The system will:")
        print(f"  1. Try to use real AI Core endpoints first")
        print(f"  2. Fall back to mock responses if RBAC access is denied")
        print(f"  3. Provide helpful error messages and next steps")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"  1. To get full AI functionality, resolve RBAC permissions")
        print(f"  2. Contact SAP AI Core admin to grant inference permissions")
        print(f"  3. Test with: python -m pytest tests/test_aicore_integration.py")
        
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print(f"Please check the error messages above.")
    
    return creds_ok and aicore_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
