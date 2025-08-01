#!/usr/bin/env python3
"""
Debug script to check route registration
"""

from main import app

def debug_routes():
    print("🔍 Checking registered routes...")
    
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"Route: {route.path} - Methods: {getattr(route, 'methods', 'N/A')}")
        elif hasattr(route, 'routes'):
            print(f"Router: {getattr(route, 'prefix', 'No prefix')}")
            for sub_route in route.routes:
                if hasattr(sub_route, 'path'):
                    print(f"  Sub-route: {sub_route.path} - Methods: {getattr(sub_route, 'methods', 'N/A')}")

if __name__ == "__main__":
    debug_routes() 