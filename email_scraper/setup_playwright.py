#!/usr/bin/env python3
"""
Setup script for Playwright Email Scraper
Installs Playwright browsers for the email scraper.
"""

import subprocess
import sys
import os

def install_playwright_browsers():
    """Install Playwright browsers."""
    print("🔧 Setting up Playwright browsers...")
    
    try:
        # Install Playwright browsers
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully!")
            print("You can now run the email scraper.")
        else:
            print("❌ Failed to install Playwright browsers:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing Playwright browsers: {str(e)}")
        return False
    
    return True

def check_playwright_installation():
    """Check if Playwright is properly installed."""
    try:
        import playwright  # type: ignore
        print("✅ Playwright Python package is installed")
        return True
    except ImportError:
        print("❌ Playwright Python package is not installed")
        print("Please run: pip install playwright")
        return False

def main():
    """Main setup function."""
    print("🚀 Playwright Email Scraper Setup")
    print("=" * 40)
    
    # Check if Playwright is installed
    if not check_playwright_installation():
        return
    
    # Install browsers
    if install_playwright_browsers():
        print("\n🎉 Setup completed successfully!")
        print("\nYou can now run the email scraper with:")
        print("  python playwright_email_scraper.py")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 