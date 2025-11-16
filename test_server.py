#!/usr/bin/env python3
"""
Simple test script to verify server is working
"""

import requests
import sys

BASE_URL = 'http://localhost:5000'

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/api/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"✅ GitHub configured: {data['github_configured']}")
            print(f"⚠️  Bot configured: {data['bot_configured']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure server is running: python server_v2.py")
        return False

def test_init():
    """Test storage initialization"""
    print("\n🔍 Testing storage initialization...")
    try:
        response = requests.post(f'{BASE_URL}/api/init')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Storage initialized successfully")
                return True
            else:
                print(f"❌ Init failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Init request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Init error: {e}")
        return False

def test_translations():
    """Test translations endpoint"""
    print("\n🔍 Testing translations...")
    try:
        for lang in ['ru', 'en']:
            response = requests.get(f'{BASE_URL}/api/translations/{lang}')
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {lang.upper()}: '{data.get('welcome')}'")
            else:
                print(f"❌ Translation failed for {lang}")
                return False
        return True
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return False

def test_shop_products():
    """Test shop products endpoint"""
    print("\n🔍 Testing shop products...")
    try:
        response = requests.get(f'{BASE_URL}/api/shop/products')
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products")
            if products:
                print(f"   Example: {products[0]['title']} - {products[0]['price']} M$")
            return True
        else:
            print(f"❌ Products request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Products error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 HomeOS Server Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Storage Init", test_init),
        ("Translations", test_translations),
        ("Shop Products", test_shop_products),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\n🎉 All tests passed! Server is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Get BOT_TOKEN from @BotFather")
        print("   2. Add it to .env file")
        print("   3. Restart server")
        print("   4. Test Telegram authentication")
        return 0
    else:
        print("\n❌ Some tests failed. Please check:")
        print("   - Server is running (python server_v2.py)")
        print("   - GitHub token is correct in .env")
        print("   - data/ folder exists in GitHub repo")
        return 1

if __name__ == '__main__':
    sys.exit(main())