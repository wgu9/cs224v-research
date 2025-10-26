# Query 1: Create a new Python file to test LLM connection and print all key model information.

**User**
@test-litellm.ipynb  please write a new python file for testing connection and print out all key infomration about the model when connected.

---

**Assistant**
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
