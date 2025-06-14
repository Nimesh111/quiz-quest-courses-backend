#!/usr/bin/env python3
"""
Simple installation test for Quiz Quest Backend
This script verifies that all dependencies are properly installed
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: {e}")
        return False

def main():
    """Run installation tests"""
    print("🧪 Testing Quiz Quest Backend Installation")
    print("=" * 50)
    
    # Test core dependencies
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("passlib", "Passlib"),
        ("jose", "Python-JOSE"),
        ("multipart", "Python-multipart"),
        ("email_validator", "Email-validator"),
        ("dotenv", "Python-dotenv"),
        ("aiofiles", "AIOFiles"),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for module, package in dependencies:
        if test_import(module, package):
            success_count += 1
    
    print("-" * 50)
    print(f"📊 Results: {success_count}/{total_count} dependencies installed")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
        
        # Test basic app import
        try:
            print("\n🔧 Testing app import...")
            from app.main import app
            print("✅ FastAPI app import successful")
            
            # Test database module
            from app.database import JSONDatabase
            print("✅ Database service import successful")
            
            print("\n🚀 Installation test passed! Ready to start the server.")
            return True
            
        except Exception as e:
            print(f"❌ App import failed: {e}")
            return False
    else:
        print(f"⚠️  Missing {total_count - success_count} dependencies")
        print("💡 Try running: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 