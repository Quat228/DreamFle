import os
import re
from pathlib import Path
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def crm_app(request):
    """Serve CRM React app at /crm/"""
    # Same logic as miniapp but for CRM
    static_root = Path(settings.STATIC_ROOT)
    dist_index_path = static_root / "frontend" / "index.html"
    
    if not dist_index_path.exists() and settings.STATICFILES_DIRS:
        static_dirs = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None
        if static_dirs:
            dist_index_path = Path(static_dirs) / "frontend" / "index.html"
    
    js_path = "frontend/assets/index-fc86472f.js"
    css_path = "frontend/assets/index-ca84d5cb.css"
    
    if dist_index_path.exists():
        try:
            with open(dist_index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                script_match = re.search(r'<script[^>]+src=["\']([^"\']+)["\']', content)
                if script_match:
                    js_path_raw = script_match.group(1)
                    if js_path_raw.startswith('/assets/'):
                        js_path = "frontend" + js_path_raw
                    elif js_path_raw.startswith('/'):
                        js_path = "frontend" + js_path_raw
                    else:
                        js_path = "frontend/" + js_path_raw
                
                css_match = re.search(r'<link[^>]+href=["\']([^"\']+\.css)["\']', content)
                if css_match:
                    css_path_raw = css_match.group(1)
                    if css_path_raw.startswith('/assets/'):
                        css_path = "frontend" + css_path_raw
                    elif css_path_raw.startswith('/'):
                        css_path = "frontend" + css_path_raw
                    else:
                        css_path = "frontend/" + css_path_raw
        except Exception as e:
            print(f"Error reading index.html: {e}")
    
    context = {
        'js_path': js_path,
        'css_path': css_path,
    }
    
    return render(request, "frontend/index.html", context)

@xframe_options_exempt
def miniapp(request):
    # Try to read the built index.html from static files directory
    # First try STATIC_ROOT (collected static files)
    static_root = Path(settings.STATIC_ROOT)
    dist_index_path = static_root / "frontend" / "index.html"
    
    # Fallback to STATICFILES_DIRS (source static files)
    if not dist_index_path.exists() and settings.STATICFILES_DIRS:
        static_dirs = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None
        if static_dirs:
            dist_index_path = Path(static_dirs) / "frontend" / "index.html"
    
    # Default fallback paths
    js_path = "frontend/assets/index-fc86472f.js"
    css_path = "frontend/assets/index-ca84d5cb.css"
    
    if dist_index_path.exists():
        try:
            with open(dist_index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract script src
                script_match = re.search(r'<script[^>]+src=["\']([^"\']+)["\']', content)
                if script_match:
                    js_path_raw = script_match.group(1)
                    # Convert /assets/... to frontend/assets/... for Django static
                    if js_path_raw.startswith('/assets/'):
                        js_path = "frontend" + js_path_raw
                    elif js_path_raw.startswith('/'):
                        js_path = "frontend" + js_path_raw
                    else:
                        js_path = "frontend/" + js_path_raw
                
                # Extract CSS link if present
                css_match = re.search(r'<link[^>]+href=["\']([^"\']+\.css)["\']', content)
                if css_match:
                    css_path_raw = css_match.group(1)
                    # Convert /assets/... to frontend/assets/... for Django static
                    if css_path_raw.startswith('/assets/'):
                        css_path = "frontend" + css_path_raw
                    elif css_path_raw.startswith('/'):
                        css_path = "frontend" + css_path_raw
                    else:
                        css_path = "frontend/" + css_path_raw
        except Exception as e:
            print(f"Error reading index.html: {e}")
    
    context = {
        'js_path': js_path,
        'css_path': css_path,
    }
    
    return render(request, "frontend/index.html", context)
