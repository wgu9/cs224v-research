#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.

HOW TO RUN THIS SCRIPT:
=======================

1. INSTALL DEPENDENCIES:
   First, make sure you have the required packages installed:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install them individually:
   ```bash
   pip install requests python-dotenv
   ```

2. SET UP ENVIRONMENT VARIABLES:
   Create a file named `.env` in the same directory as this script with your API credentials:
   ```
   LLM_API_KEY=your_actual_api_key_here
   LLM_API_ENDPOINT=https://your-api-endpoint.com
   ```
   
   Example:
   ```
   LLM_API_KEY=sk-1234567890abcdef...
   LLM_API_ENDPOINT=https://api.openai.com/v1
   ```

3. RUN THE SCRIPT:
   From the command line, navigate to the directory containing this script and run:
   ```bash
   python test_llm_connection.py
   ```
   
   Or if you're using Python 3 specifically:
   ```bash
   python3 test_llm_connection.py
   ```
   
   Or make it executable and run directly:
   ```bash
   chmod +x test_llm_connection.py
   ./test_llm_connection.py
   ```

4. EXPECTED OUTPUT:
   The script will run several tests and display:
   - ✅ Connection status
   - 📊 Performance metrics (response times, token usage)
   - 🧪 Test results for different scenarios
   - 🔍 Model capabilities and limits
   - 💡 Recommendations for production use

TROUBLESHOOTING:
===============
- "ModuleNotFoundError": Run `pip install requests python-dotenv`
- "Environment variables not found": Check your `.env` file exists and has correct variable names
- "Connection failed": Verify your API endpoint and key are correct
- "Permission denied": Try `python3 test_llm_connection.py` instead

For more detailed information, see the README_test_script.md file.
"""

import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv(".env")
    
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_ENDPOINT")
    
    if not api_key:
        raise ValueError("LLM_API_KEY not found in environment variables")
    if not base_url:
        raise ValueError("LLM_API_ENDPOINT not found in environment variables")
    
    return api_key, base_url

def test_basic_connection(api_key, base_url):
    """Test basic connection with a simple request"""
    print("🔗 Testing basic connection...")
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4.1",
                "messages": [
                    {"role": "user", "content": "Hello! Please respond with 'Connection successful' and nothing else."}
                ],
                "max_tokens": 10,
                "temperature": 0.1
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            model_name = result.get('model', 'Unknown')
            print("✅ Basic connection successful!")
            print(f"   🤖 Model: {model_name}")
            print(f"   Response: {result['choices'][0]['message']['content']}")
            return True, result
        else:
            print(f"❌ Connection failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False, None

def get_model_info(api_key, base_url):
    """Get comprehensive model information"""
    print("\n📊 Gathering model information...")
    
    model_info = {}
    
    # Test different model parameters
    test_cases = [
        {
            "name": "Basic Chat",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "max_tokens": 50,
                "temperature": 0.1
            }
        },
        # {
        #     "name": "Long Response",
        #     "config": {
        #         "model": "gpt-4.1",
        #         "messages": [{"role": "user", "content": "Count from 1 to 10"}],
        #         "max_tokens": 100,
        #         "temperature": 0.1
        #     }
        # },
        # {
        #     "name": "High Temperature",
        #     "config": {
        #         "model": "gpt-4.1",
        #         "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
        #         "max_tokens": 150,
        #         "temperature": 0.9
        #     }
        # },
        # {
        #     "name": "System Message",
        #     "config": {
        #         "model": "gpt-4.1",
        #         "messages": [
        #             {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
        #             {"role": "user", "content": "What is the capital of France?"}
        #         ],
        #         "max_tokens": 50,
        #         "temperature": 0.1
        #     }
        # }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=test_case['config'],
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                response_time = end_time - start_time
                
                print(f"   ✅ Success (Response time: {response_time:.2f}s)")
                print(f"   📝 Response: {result['choices'][0]['message']['content'][:100]}...")
                
                # Extract usage information
                usage = result.get('usage', {})
                print(f"   📊 Tokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                      f"Completion: {usage.get('completion_tokens', 'N/A')}, "
                      f"Total: {usage.get('total_tokens', 'N/A')}")
                
                # Store model info
                model_info[test_case['name']] = {
                    'success': True,
                    'response_time': response_time,
                    'usage': usage,
                    'response_length': len(result['choices'][0]['message']['content']),
                    'model': result.get('model', 'Unknown')
                }
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                model_info[test_case['name']] = {
                    'success': False,
                    'error': response.text
                }
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
            model_info[test_case['name']] = {
                'success': False,
                'error': str(e)
            }
    
    return model_info

def test_model_limits(api_key, base_url):
    """Test model limits and capabilities"""
    print("\n🔍 Testing model limits...")
    
    limits_info = {}
    
    # Test maximum token limit
    print("\n📏 Testing maximum token limit...")
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Write a very long story"}],
                "max_tokens": 4000,  # Test high token limit
                "temperature": 0.1
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            usage = result.get('usage', {})
            limits_info['max_tokens_test'] = {
                'success': True,
                'max_tokens_requested': 4000,
                'tokens_used': usage.get('total_tokens', 0),
                'response_length': len(result['choices'][0]['message']['content'])
            }
            print("   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        limits_info['max_tokens_test'] = {
            'success': False,
            'error': str(e)
        }
        print(f"   ❌ Max tokens test error: {e}")
    
    return limits_info

def print_summary(model_info, limits_info, api_key, base_url):
    """Print comprehensive summary of all test results"""
    print("\n" + "="*80)
    print("📋 COMPREHENSIVE MODEL TEST SUMMARY")
    print("="*80)
    
    print("\n🔧 Configuration:")
    print(f"   API Endpoint: {base_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    print(f"   Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get model name from first successful test
    model_name = "Unknown"
    for test_result in model_info.values():
        if test_result.get('success', False) and 'model' in test_result:
            model_name = test_result['model']
            break
    print(f"   🤖 Model: {model_name}")
    
    print("\n📊 Test Results:")
    successful_tests = sum(1 for test in model_info.values() if test.get('success', False))
    total_tests = len(model_info)
    print(f"   Successful Tests: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        avg_response_time = sum(
            test['response_time'] for test in model_info.values() 
            if test.get('success', False) and 'response_time' in test
        ) / successful_tests
        print(f"   Average Response Time: {avg_response_time:.2f}s")
        
        total_tokens = sum(
            test['usage'].get('total_tokens', 0) for test in model_info.values() 
            if test.get('success', False) and 'usage' in test
        )
        print(f"   Total Tokens Used: {total_tokens}")
    
    print("\n🧪 Individual Test Results:")
    for test_name, result in model_info.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result.get('success', False):
            if 'response_time' in result:
                print(f"      Response Time: {result['response_time']:.2f}s")
            if 'usage' in result:
                usage = result['usage']
                print(f"      Tokens: {usage.get('total_tokens', 'N/A')}")
    
    print("\n🔍 Model Capabilities:")
    if limits_info.get('max_tokens_test', {}).get('success', False):
        max_test = limits_info['max_tokens_test']
        print(f"   Max Tokens Tested: {max_test['max_tokens_requested']}")
        print(f"   Tokens Actually Used: {max_test['tokens_used']}")
        print(f"   Response Length: {max_test['response_length']} characters")
    
    print("\n💡 Recommendations:")
    if successful_tests == total_tests:
        print("   ✅ All tests passed! The model is working correctly.")
        print("   💡 Consider implementing retry logic for production use.")
        print("   💡 Monitor token usage to manage costs.")
    else:
        print("   ⚠️  Some tests failed. Check your API configuration.")
        print("   💡 Verify your API key and endpoint are correct.")
        print("   💡 Check if you have sufficient API credits/quota.")

def main():
    """Main function to run all tests"""
    print("🚀 Starting LLM Connection Test")
    print("="*50)
    
    try:
        # Load environment
        api_key, base_url = load_environment()
        print(f"✅ Environment loaded successfully")
        print(f"   Endpoint: {base_url}")
        
        # Test basic connection
        success, _ = test_basic_connection(api_key, base_url)
        if not success:
            print("\n❌ Basic connection failed. Stopping tests.")
            return
        
        # Get comprehensive model info
        model_info = get_model_info(api_key, base_url)
        
        # Test model limits
        limits_info = test_model_limits(api_key, base_url)
        
        # Print summary
        print_summary(model_info, limits_info, api_key, base_url)
        
    except (ValueError, requests.exceptions.RequestException) as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()
