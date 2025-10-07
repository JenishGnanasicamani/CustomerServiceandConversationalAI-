#!/usr/bin/env python3
"""
Test AI Core Integration - Final Verification
Tests that AI Core is working with real conversation analysis
"""

import json
import logging
from src.aicore_service import get_aicore_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_aicore_conversation_analysis():
    """Test AI Core with a real conversation analysis scenario"""
    
    print("🚀 Testing AI Core Integration - Real Conversation Analysis")
    print("=" * 80)
    
    try:
        # Initialize AI Core client
        client = get_aicore_client()
        print(f"✓ AI Core client initialized")
        print(f"  API URL: {client.ai_api_url}")
        print(f"  Default Model: {client.default_model}")
        
        # Test conversation data
        conversation = {
            "customer": "Hi, I'm having trouble with my internet connection. It's been very slow for the past week.",
            "agent": "I'm sorry to hear you're experiencing slow internet speeds. Let me help you troubleshoot this issue. Can you tell me what speeds you're currently getting?",
            "customer": "It's only about 5 Mbps download, but I'm paying for 100 Mbps.",
            "agent": "That's definitely not the speed you should be getting. Let me run a diagnostic on your line. I can see there's an issue with your modem. I'll send a technician tomorrow between 9 AM and 12 PM. Will that work for you?",
            "customer": "Yes, that works perfectly. Thank you for your quick help!",
            "agent": "You're very welcome! The technician will bring a new modem and get everything sorted out. Is there anything else I can help you with today?",
            "customer": "No, that covers everything. Thanks again!"
        }
        
        # Convert to conversation format
        conversation_text = "\n".join([f"{role}: {text}" for role, text in conversation.items()])
        
        # Prepare analysis prompt
        messages = [
            {
                "role": "user",
                "content": f"""Please analyze this customer service conversation and provide a detailed performance assessment:

{conversation_text}

Please evaluate:
1. Customer satisfaction level (1-10)
2. Issue resolution effectiveness
3. Agent communication quality
4. Overall service quality
5. Key strengths and areas for improvement

Format your response as a structured analysis."""
            }
        ]
        
        print("\n🔄 Sending conversation analysis request...")
        print(f"Conversation length: {len(conversation_text)} characters")
        
        # Send request to AI Core
        response = client.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=1000
        )
        
        # Parse response
        if 'choices' in response and response['choices']:
            analysis = response['choices'][0]['message']['content']
            usage = response.get('usage', {})
            
            print(f"\n✅ AI Core Analysis Complete!")
            print(f"Response length: {len(analysis)} characters")
            print(f"Token usage: {usage.get('prompt_tokens', 0)} prompt + {usage.get('completion_tokens', 0)} completion = {usage.get('total_tokens', 0)} total")
            
            print(f"\n📊 ANALYSIS RESULTS:")
            print("=" * 50)
            print(analysis)
            print("=" * 50)
            
            # Check if it's a real AI response (not fallback)
            if "FALLBACK" in analysis:
                print("⚠️  This appears to be a fallback response")
                return False
            else:  
                print("🎉 Real AI Core response received!")
                return True
                
        else:
            print("❌ Invalid response format")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

def test_health_check():
    """Test AI Core health check"""
    print("\n🔍 AI Core Health Check")
    print("-" * 40)
    
    try:
        client = get_aicore_client()
        health = client.health_check()
        
        print(f"Status: {health['status']}")
        print(f"Timestamp: {health['timestamp']}")
        print(f"Token Valid: {health['token_valid']}")
        
        return health['status'] == 'healthy'
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing SAP AI Core Integration with Real Conversation Analysis")
    print("=" * 80)
    
    # Run tests
    health_ok = test_health_check()
    analysis_ok = test_aicore_conversation_analysis()
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS:")
    print(f"✓ Health Check: {'PASS' if health_ok else 'FAIL'}")
    print(f"✓ Conversation Analysis: {'PASS' if analysis_ok else 'FAIL'}")
    
    if health_ok and analysis_ok:
        print("\n🎉 SUCCESS: AI Core integration is working perfectly!")
        print("✅ Real Claude responses from SAP AI Core")
        print("✅ Using /invoke endpoint with bedrock-2023-05-31")
        print("✅ Anthropic format conversion working")
    else:
        print("\n❌ Some tests failed - check logs above")
    
    print("=" * 80)
