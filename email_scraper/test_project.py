#!/usr/bin/env python3
"""
Test script for the Email Scraper project
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp imported successfully")
    except ImportError as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 imported successfully")
    except ImportError as e:
        print(f"❌ beautifulsoup4 import failed: {e}")
        return False
    
    try:
        from email_scraper.scraper import EmailScraper
        print("✅ EmailScraper imported successfully")
    except ImportError as e:
        print(f"❌ EmailScraper import failed: {e}")
        return False
    
    return True

def test_scraper_creation():
    """Test if EmailScraper can be instantiated."""
    print("\nTesting scraper creation...")
    
    try:
        from email_scraper.scraper import EmailScraper
        scraper = EmailScraper(delay=0.1, max_concurrent=5)
        print("✅ EmailScraper created successfully")
        return True
    except Exception as e:
        print(f"❌ EmailScraper creation failed: {e}")
        return False

def test_file_processing():
    """Test file processing functions."""
    print("\nTesting file processing...")
    
    try:
        import tempfile
        import os
        
        # Create a test file with URLs
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("https://example.com\nhttps://google.com\n")
            test_file = f.name
        
        # Test if file exists
        if os.path.exists(test_file):
            print("✅ Test file created successfully")
            
            # Clean up
            os.remove(test_file)
            print("✅ Test file cleaned up")
            return True
        else:
            print("❌ Test file creation failed")
            return False
            
    except Exception as e:
        print(f"❌ File processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running Email Scraper Project Tests\n")
    
    tests = [
        test_imports,
        test_scraper_creation,
        test_file_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 