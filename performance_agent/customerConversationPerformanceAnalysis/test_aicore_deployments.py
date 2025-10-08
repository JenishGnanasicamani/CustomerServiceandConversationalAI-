#!/usr/bin/env python3
"""
Enhanced AI Core deployment discovery script
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

def find_deployments_and_resource_groups():
    """Find available deployments and resource groups"""
    
    print("=" * 80)
    print("AI CORE DEPLOYMENT DISCOVERY")
    print("=" * 80)
    
    try:
        # Load credentials and get client
        client = get_aicore_client()
        access_token = client.authenticator.get_access_token()
        base_url = client.ai_api_url
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"Base URL: {base_url}")
        print(f"Access token obtained: {access_token[:50]}...")
        
        # Try to find resource groups first
        print(f"\n" + "=" * 50)
        print("DISCOVERING RESOURCE GROUPS")
        print("=" * 50)
        
        resource_group_endpoints = [
            "/v2/lm/resourceGroups",
            "/v2/resourceGroups", 
            "/lm/resourceGroups",
            "/resourceGroups"
        ]
        
        resource_groups = []
        
        for endpoint in resource_group_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"Testing: {endpoint}")
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✓ SUCCESS: Found resource groups endpoint")
                    print(f"    Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if isinstance(data, dict):
                        if 'resources' in data:
                            resource_groups = [rg.get('id', rg.get('name', str(rg))) for rg in data['resources']]
                        elif 'data' in data:
                            resource_groups = [rg.get('id', rg.get('name', str(rg))) for rg in data['data']]
                        else:
                            resource_groups = list(data.keys())
                    
                    print(f"    Found resource groups: {resource_groups}")
                    break
                    
                elif response.status_code == 400:
                    print(f"  ? BAD REQUEST (400): {response.text[:200]}")
                elif response.status_code == 404:
                    print(f"  ✗ NOT FOUND (404)")
                else:
                    print(f"  ? STATUS ({response.status_code}): {response.text[:200]}")
                    
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
        
        # If no resource groups found, try common ones
        if not resource_groups:
            print("No resource groups discovered. Trying common defaults...")
            resource_groups = ["default", "rg-1", "main", "production", "test"]
        
        # Try to find deployments for each resource group
        print(f"\n" + "=" * 50)
        print("DISCOVERING DEPLOYMENTS")
        print("=" * 50)
        
        all_deployments = []
        
        for rg in resource_groups:
            print(f"\nTesting resource group: {rg}")
            
            # Try different deployment endpoints
            deployment_endpoints = [
                f"/v2/lm/deployments",
                f"/v2/inference/deployments", 
                f"/deployments"
            ]
            
            for endpoint in deployment_endpoints:
                try:
                    url = f"{base_url}{endpoint}"
                    test_headers = headers.copy()
                    test_headers['AI-Resource-Group'] = rg
                    
                    print(f"  Testing: {endpoint} with RG: {rg}")
                    
                    response = requests.get(url, headers=test_headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✓ SUCCESS: Found deployments")
                        
                        deployments = []
                        if isinstance(data, dict):
                            if 'resources' in data:
                                deployments = data['resources']
                            elif 'data' in data:
                                deployments = data['data']
                            elif 'deployments' in data:
                                deployments = data['deployments']
                        elif isinstance(data, list):
                            deployments = data
                        
                        print(f"    Found {len(deployments)} deployments")
                        
                        for i, deployment in enumerate(deployments[:3]):  # Show first 3
                            if isinstance(deployment, dict):
                                dep_id = deployment.get('id', deployment.get('deploymentId', f'deployment_{i}'))
                                dep_status = deployment.get('status', 'unknown')
                                dep_config = deployment.get('configurationId', 'unknown')
                                print(f"      - ID: {dep_id}, Status: {dep_status}, Config: {dep_config}")
                                
                                all_deployments.append({
                                    'id': dep_id,
                                    'resource_group': rg,
                                    'status': dep_status,
                                    'endpoint': endpoint,
                                    'full_data': deployment
                                })
                        
                        if len(deployments) > 3:
                            print(f"      ... and {len(deployments) - 3} more")
                        
                        break  # Found working endpoint for this RG
                        
                    elif response.status_code == 400:
                        print(f"    ? BAD REQUEST (400): {response.text[:100]}")
                    elif response.status_code == 404:
                        print(f"    ✗ NOT FOUND (404)")
                    else:
                        print(f"    ? STATUS ({response.status_code}): {response.text[:100]}")
                        
                except Exception as e:
                    print(f"    ✗ ERROR: {e}")
        
        # Test chat completions with found deployments
        if all_deployments:
            print(f"\n" + "=" * 50)
            print("TESTING CHAT COMPLETIONS")
            print("=" * 50)
            
            test_message = {
                "messages": [
                    {"role": "user", "content": "Hello, this is a test."}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            }
            
            for deployment in all_deployments[:3]:  # Test first 3 deployments
                dep_id = deployment['id']
                rg = deployment['resource_group']
                
                print(f"\nTesting deployment: {dep_id} in RG: {rg}")
                
                chat_endpoints = [
                    f"/v2/lm/deployments/{dep_id}/chat/completions",
                    f"/v2/inference/deployments/{dep_id}/chat/completions",
                    f"/v2/lm/deployments/{dep_id}/completions",
                    f"/v2/inference/deployments/{dep_id}/completions"
                ]
                
                for chat_endpoint in chat_endpoints:
                    try:
                        url = f"{base_url}{chat_endpoint}"
                        test_headers = headers.copy()
                        test_headers['AI-Resource-Group'] = rg
                        
                        print(f"  Testing: {chat_endpoint}")
                        
                        response = requests.post(url, headers=test_headers, json=test_message, timeout=30)
                        
                        if response.status_code == 200:
                            print(f"    ✓ CHAT SUCCESS!")
                            try:
                                result = response.json()
                                print(f"    Response keys: {list(result.keys())}")
                                if 'choices' in result and result['choices']:
                                    content = result['choices'][0].get('message', {}).get('content', '')
                                    print(f"    Content preview: {content[:100]}")
                            except:
                                print(f"    Response: {response.text[:200]}")
                            
                            return {
                                'resource_group': rg,
                                'deployment_id': dep_id,
                                'endpoint': chat_endpoint,
                                'base_url': base_url
                            }
                            
                        elif response.status_code == 400:
                            print(f"    ? BAD REQUEST (400): {response.text[:100]}")
                        elif response.status_code == 404:
                            print(f"    ✗ NOT FOUND (404)")
                        else:
                            print(f"    ? STATUS ({response.status_code}): {response.text[:100]}")
                            
                    except Exception as e:
                        print(f"    ✗ ERROR: {e}")
        
        return {
            'resource_groups': resource_groups,
            'deployments': all_deployments,
            'working_config': None
        }
        
    except Exception as e:
        print(f"✗ Error during deployment discovery: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)
    
    result = find_deployments_and_resource_groups()
    
    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if result:
        if result.get('working_config'):
            config = result['working_config']
            print("✓ FOUND WORKING CONFIGURATION!")
            print(f"  Resource Group: {config['resource_group']}")
            print(f"  Deployment ID: {config['deployment_id']}")
            print(f"  Endpoint: {config['endpoint']}")
            print(f"  Base URL: {config['base_url']}")
            
            print(f"\n" + "=" * 50)
            print("CONFIGURATION TO UPDATE")
            print("=" * 50)
            print("Update your AI Core configuration with these values:")
            print(f"ai_resource_group: '{config['resource_group']}'")
            print(f"deployment_id: '{config['deployment_id']}'")
            print(f"chat_endpoint: '{config['endpoint']}'")
            
        else:
            print("✗ No working chat completion endpoint found")
            if result.get('deployments'):
                print(f"Found {len(result['deployments'])} deployments but none support chat completions")
            else:
                print("No deployments found")
                
        print(f"\nResource groups discovered: {result.get('resource_groups', [])}")
        print(f"Total deployments found: {len(result.get('deployments', []))}")
    else:
        print("✗ Discovery failed")

if __name__ == "__main__":
    main()
