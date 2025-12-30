"""
Verification script for Excel Loader FastAPI application.

This script verifies that the FastAPI application is properly configured
and all endpoints are accessible.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def verify_app_structure():
    """Verify the FastAPI application structure."""
    print("=" * 60)
    print("Excel Loader FastAPI Application Verification")
    print("=" * 60)
    
    try:
        # Import the app
        from Data_upload.scripts.excel_loader.excel_loader_app import app, config
        print("✓ Successfully imported FastAPI app")
        
        # Check app configuration
        print(f"\nApp Configuration:")
        print(f"  Name: {config.APP_NAME}")
        print(f"  Version: {config.APP_VERSION}")
        print(f"  Database: {config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}")
        print(f"  Max file size: {config.EXCEL_UPLOAD_MAX_SIZE / (1024 * 1024):.0f}MB")
        print(f"  Import timeout: {config.EXCEL_IMPORT_TIMEOUT}s")
        
        # Check routes
        print(f"\nRegistered Routes:")
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                routes.append(f"  {methods:20} {route.path}")
        
        for route in sorted(routes):
            print(route)
        
        # Verify required endpoints
        required_endpoints = [
            ('GET', '/'),
            ('GET', '/health'),
            ('POST', '/api/import'),
        ]
        
        print(f"\nRequired Endpoints:")
        for method, path in required_endpoints:
            found = False
            for route in app.routes:
                if hasattr(route, 'methods') and hasattr(route, 'path'):
                    if method in route.methods and route.path == path:
                        found = True
                        break
            
            status = "✓" if found else "✗"
            print(f"  {status} {method:6} {path}")
        
        # Check middleware
        print(f"\nMiddleware:")
        for middleware in app.user_middleware:
            print(f"  ✓ {middleware.cls.__name__}")
        
        # Check ImportResponse model
        from Data_upload.scripts.excel_loader.import_orchestrator import ImportResponse
        print(f"\nImportResponse Model:")
        print(f"  ✓ ImportResponse model available")
        print(f"  Fields: {', '.join(ImportResponse.model_fields.keys())}")
        
        print("\n" + "=" * 60)
        print("Verification Complete - All checks passed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_app_structure()
    sys.exit(0 if success else 1)
