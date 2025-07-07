#!/usr/bin/env python3
"""
Setup script for Google Maps Email Scraper
Installs all required dependencies and Playwright browsers.
"""

import subprocess
import sys
import os

def install_packages():
    """Install required Python packages."""
    print("📦 Installing required packages...")
    
    packages = [
        "pandas>=2.2.0",
        "openpyxl==3.1.2", 
        "python-docx==1.0.1",
        "playwright>=1.40.0",
        "tqdm==4.66.1"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error installing {package}: {str(e)}")
            return False
    
    return True

def install_playwright_browsers():
    """Install Playwright browsers."""
    print("\n🔧 Installing Playwright browsers...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully!")
        else:
            print("❌ Failed to install Playwright browsers:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing Playwright browsers: {str(e)}")
        return False
    
    return True

def check_dependencies():
    """Check if all dependencies are properly installed."""
    print("\n🔍 Checking dependencies...")
    
    dependencies = [
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"), 
        ("python-docx", "docx"),
        ("playwright", "playwright"),
        ("tqdm", "tqdm")
    ]
    
    all_good = True
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            print(f"❌ {package_name} is not installed")
            all_good = False
    
    return all_good

def create_sample_files():
    """Create sample files for testing."""
    print("\n📄 Creating sample files...")
    
    # Create sample CSV
    sample_csv_content = '''Title,Phone,Address,href,Website
"Joe's Pizza","(555) 123-4567","123 Main St, City, State","https://maps.google.com/maps?cid=123456789","https://joespizza.com"
"ABC Company","(555) 987-6543","456 Oak Ave, City, State","https://www.google.com/maps/place/ABC+Company","https://abccompany.com"
"XYZ Services","(555) 456-7890","789 Pine Rd, City, State","https://maps.google.com/maps?q=XYZ+Services","https://xyzservices.net"'''
    
    try:
        with open('sample_google_maps.csv', 'w') as f:
            f.write(sample_csv_content)
        print("✅ Created sample_google_maps.csv")
    except Exception as e:
        print(f"❌ Error creating sample CSV: {str(e)}")

def main():
    """Main setup function."""
    print("🚀 Google Maps Email Scraper Setup")
    print("=" * 50)
    
    # Install packages
    if not install_packages():
        print("\n❌ Package installation failed. Please check the errors above.")
        return
    
    # Install Playwright browsers
    if not install_playwright_browsers():
        print("\n❌ Playwright browser installation failed. Please check the errors above.")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Some dependencies are missing. Please reinstall them.")
        return
    
    # Create sample files
    create_sample_files()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Prepare your input file (.xlsx, .csv, or .docx) with Google Maps URLs")
    print("2. Run the scraper: python gmaps_email_scraper.py")
    print("3. Enter the path to your input file when prompted")
    print("4. Results will be saved to results.xlsx and results.csv")
    print("\n💡 Tip: Use sample_google_maps.csv for testing")

if __name__ == "__main__":
    main() 