#!/usr/bin/env python3
"""
Test UI Access and Functionality
"""

import time
import sys

def main():
    print("🌐 Testing UI Access")
    print("=" * 50)
    
    ui_url = "http://localhost:3007"
    
    print(f"Opening UI at: {ui_url}")
    print("\nManual Test Steps:")
    print("1. ✅ Login with: admin@datalegos.com / password")
    print("2. ✅ Verify you see the dashboard")
    print("3. 🔍 Go to Programs page")
    print("4. 🔍 Click 'New Program' button")
    print("5. 🔍 Look for 'Assign Owners' section at the bottom")
    print("6. 🔍 Go to Projects page")
    print("7. 🔍 Select a client and program")
    print("8. 🔍 Click 'New Project' button")
    print("9. 🔍 Look for 'Assign Owners' section at the bottom")
    print("\n📋 What to Check:")
    print("- Is the 'Assign Owners' section visible?")
    print("- Are there any console errors in browser dev tools (F12)?")
    print("- Does the OwnerSelector component render?")
    print("\n🐛 If Owner Assignment is NOT visible:")
    print("- Open browser dev tools (F12)")
    print("- Check Console tab for JavaScript errors")
    print("- Check Elements tab and search for 'OwnerSelector' or 'Assign Owners'")
    print("- Look for console.log messages starting with 'ProgramModal:' or 'ProjectModal:'")
    
    print(f"\n🌐 APPLICATION AVAILABLE AT: {ui_url}")
    print("ℹ️  Browser NOT opened - you can test manually in your existing session")
    
    print("\n" + "=" * 50)
    print("🎯 Focus: Check if Owner Assignment UI is visible in modal forms")

if __name__ == "__main__":
    main()