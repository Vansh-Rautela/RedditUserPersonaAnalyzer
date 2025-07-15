#!/usr/bin/env python3
"""
Test script to verify the Reddit Persona Analyzer setup
"""

import sys
import os
from dotenv import load_dotenv


def test_imports():
    """Test if all required packages can be imported."""
    print("🔍 Testing package imports...")

    try:
        import praw
        print("✅ PRAW imported successfully")
    except ImportError as e:
        print(f"❌ PRAW import failed: {e}")
        return False

    try:
        from groq import Groq
        print("✅ Groq imported successfully")
    except ImportError as e:
        print(f"❌ Groq import failed: {e}")
        return False

    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False

    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False

    return True


def test_env_file():
    """Test if the environment file exists and has required variables."""
    print("\n🔧 Testing environment configuration...")

    if not os.path.exists('config.env'):
        print("❌ config.env file not found")
        return False

    load_dotenv('config.env')

    required_vars = [
        'CLIENT_ID',
        'CLIENT_SECRET',
        'USER_AGENT',
        'GROQ_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False

    print("✅ All environment variables found")
    return True


def test_api_connections():
    """Test API connections."""
    print("\n🌐 Testing API connections...")

    try:
        from reddit_persona_analyzer import RedditPersonaAnalyzer
        analyzer = RedditPersonaAnalyzer()
        print("✅ Reddit API connection successful")
    except Exception as e:
        print(f"❌ Reddit API connection failed: {e}")
        return False

    try:
        # Test Groq connection with a simple request
        from groq import Groq
        load_dotenv('config.env')
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Simple test request
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ Groq API connection successful")
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

    return True


def test_file_structure():
    """Test if all required files exist."""
    print("\n📁 Testing file structure...")

    required_files = [
        'reddit_persona_analyzer.py',
        'app.py',
        'requirements.txt',
        'config.env',
        'README.md'
    ]

    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False

    print("✅ All required files found")
    return True


def main():
    """Run all tests."""
    print("🚀 Reddit Persona Analyzer - Setup Test")
    print("=" * 50)

    tests = [
        test_imports,
        test_env_file,
        test_api_connections,
        test_file_structure
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python reddit_persona_analyzer.py https://www.reddit.com/user/username/")
        print("2. Or run: streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check your config.env file")
        print("3. Verify your API credentials")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
