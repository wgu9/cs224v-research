# Test connection and print model information
_Exported on 10/25/2025 at 21:01:12 PDT from Cursor (1.7.53)_

---

**User**

@test-litellm.ipynb  please write a new python file for testing connection and print out all key infomration about the model when connected.

---

**Cursor**

I'll create a new Python file for testing the LLM connection and printing out all key information about the model. Let me first examine the current notebook to understand the setup, then create a comprehensive test file.


Now I'll create a comprehensive Python test file that will test the LLM connection and print out all key information about the model:


```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
"""

import requests
import json
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
    
    print(f"\n🔧 Configuration:")
    print(f"   API Endpoint: {base_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    print(f"   Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📊 Test Results:")
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
    
    print(f"\n🧪 Individual Test Results:")
    for test_name, result in model_info.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result.get('success', False):
            if 'response_time' in result:
                print(f"      Response Time: {result['response_time']:.2f}s")
            if 'usage' in result:
                usage = result['usage']
                print(f"      Tokens: {usage.get('total_tokens', 'N/A')}")
    
    print(f"\n🔍 Model Capabilities:")
    if limits_info.get('max_tokens_test', {}).get('success', False):
        max_test = limits_info['max_tokens_test']
        print(f"   Max Tokens Tested: {max_test['max_tokens_requested']}")
        print(f"   Tokens Actually Used: {max_test['tokens_used']}")
        print(f"   Response Length: {max_test['response_length']} characters")
    
    print(f"\n💡 Recommendations:")
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
        success, basic_result = test_basic_connection(api_key, base_url)
        if not success:
            print("\n❌ Basic connection failed. Stopping tests.")
            return
        
        # Get comprehensive model info
        model_info = get_model_info(api_key, base_url)
        
        # Test model limits
        limits_info = test_model_limits(api_key, base_url)
        
        # Print summary
        print_summary(model_info, limits_info, api_key, base_url)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()
```

Now let me also create a simple `.env` template file to help with configuration:


Let me check for any linting issues with the Python file I created:


Let me fix these linting issues:


Let me fix the linting issues one by one with more specific context:


```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
    
    print(f"\n🔧 Configuration:")
    print(f"   API Endpoint: {base_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    print(f"   Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📊 Test Results:")
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
    
    print(f"\n🧪 Individual Test Results:")
    for test_name, result in model_info.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result.get('success', False):
            if 'response_time' in result:
                print(f"      Response Time: {result['response_time']:.2f}s")
            if 'usage' in result:
                usage = result['usage']
                print(f"      Tokens: {usage.get('total_tokens', 'N/A')}")
    
    print(f"\n🔍 Model Capabilities:")
    if limits_info.get('max_tokens_test', {}).get('success', False):
        max_test = limits_info['max_tokens_test']
        print(f"   Max Tokens Tested: {max_test['max_tokens_requested']}")
        print(f"   Tokens Actually Used: {max_test['tokens_used']}")
        print(f"   Response Length: {max_test['response_length']} characters")
    
    print(f"\n💡 Recommendations:")
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
        success, basic_result = test_basic_connection(api_key, base_url)
        if not success:
            print("\n❌ Basic connection failed. Stopping tests.")
            return
        
        # Get comprehensive model info
        model_info = get_model_info(api_key, base_url)
        
        # Test model limits
        limits_info = test_model_limits(api_key, base_url)
        
        # Print summary
        print_summary(model_info, limits_info, api_key, base_url)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
    
    print(f"\n🔧 Configuration:")
    print(f"   API Endpoint: {base_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    print(f"   Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📊 Test Results:")
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
    
    print(f"\n🧪 Individual Test Results:")
    for test_name, result in model_info.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result.get('success', False):
            if 'response_time' in result:
                print(f"      Response Time: {result['response_time']:.2f}s")
            if 'usage' in result:
                usage = result['usage']
                print(f"      Tokens: {usage.get('total_tokens', 'N/A')}")
    
    print(f"\n🔍 Model Capabilities:")
    if limits_info.get('max_tokens_test', {}).get('success', False):
        max_test = limits_info['max_tokens_test']
        print(f"   Max Tokens Tested: {max_test['max_tokens_requested']}")
        print(f"   Tokens Actually Used: {max_test['tokens_used']}")
        print(f"   Response Length: {max_test['response_length']} characters")
    
    print(f"\n💡 Recommendations:")
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
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
    
    print(f"\n📊 Test Results:")
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
    
    print(f"\n🧪 Individual Test Results:")
    for test_name, result in model_info.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result.get('success', False):
            if 'response_time' in result:
                print(f"      Response Time: {result['response_time']:.2f}s")
            if 'usage' in result:
                usage = result['usage']
                print(f"      Tokens: {usage.get('total_tokens', 'N/A')}")
    
    print(f"\n🔍 Model Capabilities:")
    if limits_info.get('max_tokens_test', {}).get('success', False):
        max_test = limits_info['max_tokens_test']
        print(f"   Max Tokens Tested: {max_test['max_tokens_requested']}")
        print(f"   Tokens Actually Used: {max_test['tokens_used']}")
        print(f"   Response Length: {max_test['response_length']} characters")
    
    print(f"\n💡 Recommendations:")
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
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
    
    print(f"\n🧪 Individual Test Results:")
    for test_name, result in model_info.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result.get('success', False):
            if 'response_time' in result:
                print(f"      Response Time: {result['response_time']:.2f}s")
            if 'usage' in result:
                usage = result['usage']
                print(f"      Tokens: {usage.get('total_tokens', 'N/A')}")
    
    print(f"\n🔍 Model Capabilities:")
    if limits_info.get('max_tokens_test', {}).get('success', False):
        max_test = limits_info['max_tokens_test']
        print(f"   Max Tokens Tested: {max_test['max_tokens_requested']}")
        print(f"   Tokens Actually Used: {max_test['tokens_used']}")
        print(f"   Response Length: {max_test['response_length']} characters")
    
    print(f"\n💡 Recommendations:")
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
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
    
    print(f"\n🔍 Model Capabilities:")
    if limits_info.get('max_tokens_test', {}).get('success', False):
        max_test = limits_info['max_tokens_test']
        print(f"   Max Tokens Tested: {max_test['max_tokens_requested']}")
        print(f"   Tokens Actually Used: {max_test['tokens_used']}")
        print(f"   Response Length: {max_test['response_length']} characters")
    
    print(f"\n💡 Recommendations:")
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
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
    
    print(f"\n💡 Recommendations:")
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
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
            print(f"   📊 Tokens used: {usage.get('total_tokens', 0)}")
        else:
            limits_info['max_tokens_test'] = {
                'success': False,
                'error': response.text
            }
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except Exception as e:
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
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

Now let me fix the exception handling issues:


```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
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
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure you have a .env file with LLM_API_KEY and LLM_API_ENDPOINT")

if __name__ == "__main__":
    main()

```

```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
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

```

Now let me check if there are any remaining linting issues:


I see there's a syntax error. Let me fix the indentation issue:


I see the issue - the indentation is wrong. Let me fix it:


```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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
            print(f"   ✅ Max tokens test successful")
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

```

Let me check the linting again:


Let me read more context around the problematic area:


I see the issue. The try block is missing its corresponding except block. Let me fix the entire function:


```python
#!/usr/bin/env python3
"""
LLM Connection Test Script

This script tests the connection to the LLM API and prints out comprehensive
information about the model, including capabilities, limits, and configuration.
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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

```

Now let me check the linting again:


Let me check what's on line 209:


The syntax looks correct. Let me check if there's a missing try statement by reading more context:


I see the issue - there's an extra indentation on line 208. Let me fix it:


```python
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
```

Let me check the exact indentation:


I see the issue - line 208 has extra whitespace. Let me fix it:


```python
            print(f"   ❌ Max tokens test failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
```

Let me try a different approach and rewrite the entire problematic section:


```python
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
```

Let me try to run the script to see if it works despite the linting error:


The script needs the `python-dotenv` package. Let me check if there's a requirements.txt file and install the dependencies:


Let me add the missing dependencies to requirements.txt:


```pip-requirements
jsonlines
pyyaml
requests
python-dotenv

```

Now let me install the dependencies:


Great! Now let me create a simple `.env` file for testing purposes:


The `.env` file is blocked by gitignore. Let me test the script with the placeholder values to show how it works:


Perfect! The script is working excellently. Let me also create a simple README file to explain how to use it:


```markdown
# LLM Connection Test Script

This script provides comprehensive testing of your LLM API connection and prints out detailed information about the model's capabilities, performance, and configuration.

## Features

- **Basic Connection Test**: Verifies API connectivity
- **Comprehensive Model Testing**: Tests various scenarios including:
  - Basic chat functionality
  - Long response generation
  - High temperature creativity
  - System message handling
- **Performance Metrics**: Measures response times and token usage
- **Model Limits Testing**: Tests maximum token limits
- **Detailed Reporting**: Provides comprehensive summary with recommendations

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create a `.env` file in the same directory with your API credentials:
   ```
   LLM_API_KEY=your_api_key_here
   LLM_API_ENDPOINT=your_api_endpoint_here
   ```

3. **Run the Test**:
   ```bash
   python test_llm_connection.py
   ```

## Output

The script provides detailed output including:

- ✅ Connection status and response times
- 📊 Token usage statistics
- 🧪 Individual test results
- 🔍 Model capabilities and limits
- 💡 Recommendations for production use

## Example Output

```
🚀 Starting LLM Connection Test
==================================================
✅ Environment loaded successfully
   Endpoint: https://your-api-endpoint.com
🔗 Testing basic connection...
✅ Basic connection successful!
   Response: Connection successful

📊 Gathering model information...
🧪 Testing: Basic Chat
   ✅ Success (Response time: 0.55s)
   📝 Response: 2 + 2 = **4**...
   📊 Tokens - Prompt: 14, Completion: 9, Total: 23

[... more detailed test results ...]

================================================================================
📋 COMPREHENSIVE MODEL TEST SUMMARY
================================================================================
🔧 Configuration:
   API Endpoint: https://your-api-endpoint.com
   API Key: sk-****...****
   Test Time: 2025-10-25 20:56:08

📊 Test Results:
   Successful Tests: 4/4
   Average Response Time: 0.97s
   Total Tokens Used: 273

💡 Recommendations:
   ✅ All tests passed! The model is working correctly.
   💡 Consider implementing retry logic for production use.
   💡 Monitor token usage to manage costs.
```

## Troubleshooting

- **ModuleNotFoundError**: Make sure you've installed the requirements: `pip install -r requirements.txt`
- **Environment variables not found**: Check that your `.env` file exists and contains the correct `LLM_API_KEY` and `LLM_API_ENDPOINT`
- **Connection errors**: Verify your API endpoint and key are correct
- **Timeout errors**: Check your network connection and API endpoint availability
```

## Summary

I've successfully created a comprehensive Python test script for testing LLM connections! Here's what I've delivered:

### 📁 **Files Created:**

1. **`test_llm_connection.py`** - A comprehensive test script that:
   - Tests basic API connectivity
   - Runs multiple test scenarios (basic chat, long responses, high temperature, system messages)
   - Measures performance metrics (response times, token usage)
   - Tests model limits and capabilities
   - Provides detailed reporting with recommendations

2. **`README_test_script.md`** - Documentation explaining how to use the test script

3. **Updated `requirements.txt`** - Added necessary dependencies (`requests`, `python-dotenv`)

### 🚀 **Key Features:**

- **Comprehensive Testing**: Tests various model capabilities and scenarios
- **Performance Metrics**: Measures response times and token usage for each test
- **Detailed Reporting**: Provides a complete summary with configuration, results, and recommendations
- **Error Handling**: Robust error handling with specific exception types
- **Environment Configuration**: Uses `.env` file for secure API key management
- **Professional Output**: Clean, emoji-enhanced output with clear status indicators

### 📊 **Test Results from Your Environment:**

The script successfully ran and showed:
- ✅ All 4 tests passed
- ⚡ Average response time: 0.97s
- 📊 Total tokens used: 273
- 🔍 Successfully tested up to 4,000 token limit
- 💡 Provided recommendations for production use

The script is ready to use and provides comprehensive information about your LLM model's capabilities, performance, and configuration. Just make sure you have a `.env` file with your `LLM_API_KEY` and `LLM_API_ENDPOINT` configured!

---

**User**

how to run this file? please also comment at the top to teach how to run

---

**Cursor**

I'll add comprehensive comments at the top of the file to teach how to run it, and then show you how to execute it.


```python
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
            print("✅ Basic connection successful!")
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
        {
            "name": "Long Response",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Count from 1 to 10"}],
                "max_tokens": 100,
                "temperature": 0.1
            }
        },
        {
            "name": "High Temperature",
            "config": {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Tell me a creative story about a robot"}],
                "max_tokens": 150,
                "temperature": 0.9
            }
        },
        {
            "name": "System Message",
            "config": {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always responds in JSON format."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        }
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

```

Now let me show you how to run the file. First, let me check if you have the `.env` file set up:


Great! You already have the `.env` file. Now let me show you how to run the script:


Perfect! Let me also show you alternative ways to run the script:


## How to Run the Script

I've added comprehensive instructions at the top of the file! Here are the different ways you can run the script:

### 🚀 **Method 1: Using `python`**
```bash
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
python test_llm_connection.py
```

### 🚀 **Method 2: Using `python3`**
```bash
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
python3 test_llm_connection.py
```

### 🚀 **Method 3: Make it executable and run directly**
```bash
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
chmod +x test_llm_connection.py
./test_llm_connection.py
```

### 📋 **What the Script Does:**

The script runs comprehensive tests and shows you:

1. **🔗 Basic Connection Test** - Verifies API connectivity
2. **📊 Model Information Tests** - Tests different scenarios:
   - Basic chat functionality
   - Long response generation  
   - High temperature creativity
   - System message handling
3. **🔍 Model Limits Testing** - Tests maximum token limits
4. **📋 Comprehensive Summary** - Shows:
   - Configuration details
   - Performance metrics (response times, token usage)
   - Individual test results
   - Model capabilities
   - Recommendations for production use

### ✅ **Current Status:**
Your script is working perfectly! As you can see from the test runs:
- ✅ All 4 tests passed
- ⚡ Average response time: ~1 second
- 📊 Token usage varies by test (23-165 tokens)
- 🔍 Successfully tested up to 4,000 token limit
- 💡 Ready for production use

The script is now fully documented and ready to use. Just run any of the commands above from the `agent-memory-lab-v3` directory!

```shellscript
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
python test_llm_connection.py
```

```shellscript
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
python3 test_llm_connection.py
```

```shellscript
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
chmod +x test_llm_connection.py
./test_llm_connection.py
```

---

**User**

just do one test. # of tests reduce to 1 (commenting the toher 3)

---

**Cursor**

I'll modify the script to run only one test by commenting out the other 3 tests. Let me update the `get_model_info` function:


```python
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
            print("✅ Basic connection successful!")
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

```

Now let's test the modified script to see it running with just one test:


Perfect! ✅ I've successfully modified the script to run only **1 test** instead of 4. Here's what changed:

## 🔧 **Changes Made:**

- **Commented out 3 tests**: "Long Response", "High Temperature", and "System Message"
- **Kept only 1 test**: "Basic Chat" - which asks "What is 2+2?"

## 📊 **Results:**

The script now runs much faster and shows:
- ✅ **1/1 tests passed** (instead of 4/4)
- ⚡ **Average response time: 0.50s** (much faster)
- 📊 **Total tokens used: 24** (much lower)
- 🔍 **Still tests model limits** (max tokens test)

## 🚀 **To run the modified script:**

```bash
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
python test_llm_connection.py
```

The script is now much more lightweight and runs quickly while still providing comprehensive information about your LLM connection and capabilities! If you want to re-enable the other tests later, just uncomment the lines in the `test_cases` array.

```shellscript
cd /Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3
python test_llm_connection.py
```

---

**User**

and show which model specificially

---

**Cursor**

I'll modify the script to show which specific model is being used. Let me update the output to display the model name more prominently:


Let me first check the current structure of the print_summary function:


Let me find the print_summary function:


Now let me add the model information to the configuration section:


```python
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
            print("✅ Basic connection successful!")
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

```

Now let me also add the model information to the basic connection test output. Let me find that function:


Let me also add model information to the basic connection test:


```python
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

```

Now let's test the updated script to see the model information displayed:


Let me run the test again:


It seems the command completed without output. Let me try running it with more verbose output:


Perfect! ✅ I've successfully updated the script to show the specific model being used. Here's what's now displayed:

## 🤖 **Model Information Added:**

### **1. In Basic Connection Test:**
```
✅ Basic connection successful!
   🤖 Model: gpt-4.1-2025-04-14
   Response: Connection successful
```

### **2. In Configuration Summary:**
```
🔧 Configuration:
   API Endpoint: https://cs224v-litellm.genie.stanford.edu
   API Key: sk-Dsdhgnd...F7Gw
   Test Time: 2025-10-25 20:58:54
   🤖 Model: gpt-4.1-2025-04-14
```

## 📊 **Key Information Now Shown:**

- **🤖 Model Name**: `gpt-4.1-2025-04-14` (specific version)
- **🔗 API Endpoint**: Your LiteLLM endpoint
- **📊 Performance**: Response times and token usage
- **✅ Test Results**: 1/1 tests passed
- **🔍 Capabilities**: Max tokens tested and used

The script now clearly shows that you're using **GPT-4.1 with version 2025-04-14** through your LiteLLM endpoint. This gives you complete visibility into which specific model is being tested and its performance characteristics!

```plaintext
✅ Basic connection successful!
   🤖 Model: gpt-4.1-2025-04-14
   Response: Connection successful
```

```plaintext
🔧 Configuration:
   API Endpoint: https://cs224v-litellm.genie.stanford.edu
   API Key: sk-Dsdhgnd...F7Gw
   Test Time: 2025-10-25 20:58:54
   🤖 Model: gpt-4.1-2025-04-14
```

