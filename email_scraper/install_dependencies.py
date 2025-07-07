#!/usr/bin/env python3
"""
Installation script for Email Scraper Project
Installs all required dependencies and sets up the environment.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package."""
    try:
        print(f"Installing {package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing {package}: {str(e)}")
        return False

def install_all_dependencies():
    """Install all required dependencies."""
    print("📦 Installing all required packages...")
    
    packages = [
        "pandas>=2.2.0",
        "tqdm==4.66.1", 
        "python-dotenv==1.0.0",
        "streamlit>=1.35.0",
        "openpyxl==3.1.2",
        "python-docx==1.0.1",
        "xlrd==2.0.1",
        "playwright>=1.40.0"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary: {success_count}/{len(packages)} packages installed successfully")
    return success_count == len(packages)

def install_playwright_browsers():
    """Install Playwright browsers."""
    print("\n🔧 Installing Playwright browsers...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully!")
            return True
        else:
            print("❌ Failed to install Playwright browsers:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing Playwright browsers: {str(e)}")
        return False

def test_imports():
    """Test if all packages can be imported."""
    print("\n🧪 Testing imports...")
    
    imports_to_test = [
        ("pandas", "pandas"),
        ("streamlit", "streamlit"),
        ("playwright", "playwright"),
        ("openpyxl", "openpyxl"),
        ("docx", "docx"),
        ("tqdm", "tqdm")
    ]
    
    success_count = 0
    for package_name, import_name in imports_to_test:
        try:
            __import__(import_name)
            print(f"✅ {package_name} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ {package_name} import failed: {str(e)}")
    
    print(f"\n📊 Import Test Summary: {success_count}/{len(imports_to_test)} imports successful")
    return success_count == len(imports_to_test)

def create_init_files():
    """Create __init__.py files if they don't exist."""
    print("\n📁 Creating __init__.py files...")
    
    init_locations = [
        "email_scraper",
        "email_scraper/email_scraper"
    ]
    
    for location in init_locations:
        init_file = os.path.join(location, "__init__.py")
        if not os.path.exists(init_file):
            try:
                os.makedirs(location, exist_ok=True)
                with open(init_file, 'w') as f:
                    f.write("# Email Scraper Package\n")
                print(f"✅ Created {init_file}")
            except Exception as e:
                print(f"❌ Error creating {init_file}: {str(e)}")
        else:
            print(f"✅ {init_file} already exists")

def main():
    """Main installation function."""
    print("🚀 Email Scraper Project - Dependency Installation")
    print("=" * 60)
    
    # Install packages
    if not install_all_dependencies():
        print("\n❌ Some packages failed to install. Please check the errors above.")
        return False
    
    # Install Playwright browsers
    if not install_playwright_browsers():
        print("\n❌ Playwright browser installation failed.")
        return False
    
    # Create __init__.py files
    create_init_files()
    
    # Test imports
    if not test_imports():
        print("\n❌ Some imports failed. Please check the errors above.")
        return False
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the web app: streamlit run app.py")
    print("2. Run the Playwright scraper: python playwright_email_scraper.py")
    print("3. Run the Google Maps scraper: python gmaps_email_scraper.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 