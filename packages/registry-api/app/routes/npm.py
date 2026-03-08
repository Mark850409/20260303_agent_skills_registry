from flask import Blueprint, jsonify, request
import requests
import base64
import os
import re
from app.models import NpmPackage
from app import db
import concurrent.futures

npm_bp = Blueprint('npm', __name__)

# Registry URL inside the docker network
VERDACCIO_URL = os.getenv('VERDACCIO_INTERNAL_URL', 'http://verdaccio:4873')
# Registry URL for external access (for hints in UI)
NPM_EXTERNAL_URL = os.getenv('NPM_EXTERNAL_URL', 'localhost:5005/npm')

# Basic Auth for verdaccio internal API calls
REGISTRY_USER = 'admin'
REGISTRY_PASS = 'admin'
auth_header = {'Authorization': 'Basic ' + base64.b64encode(f"{REGISTRY_USER}:{REGISTRY_PASS}".encode()).decode()}

@npm_bp.route('/catalog', methods=['GET'])
def get_catalog():
    try:
        # Get from our DB first
        db_pkgs = NpmPackage.query.all()
        db_pkg_names = {r.name for r in db_pkgs}
        
        # Merge with actual verdaccio catalog if any exist
        try:
            response = requests.get(f"{VERDACCIO_URL}/-/all", headers=auth_header, timeout=5)
            if response.status_code == 200:
                data = response.json()
                registry_pkgs = [k for k in data.keys() if k != "_updated" and k != "npm"]
                
                # Auto-register new packages in background/lazy-mode
                for pkg_name in registry_pkgs:
                    if pkg_name not in db_pkg_names:
                        try:
                            new_pkg = NpmPackage(name=pkg_name, description="Auto-registered from registry")
                            db.session.add(new_pkg)
                            db_pkg_names.add(pkg_name)
                        except Exception:
                            db.session.rollback()
                
                if registry_pkgs:
                    db.session.commit()
                    
                db_pkg_names.update(registry_pkgs)
        except Exception as e:
            print(f"Verdaccio connection error: {e}") # Ignore registry connection errors here, show db repos at least
            
        return jsonify({
            "packages": sorted(list(db_pkg_names))
        })
    except Exception as e:
        print(f"NPM Catalog Error: {str(e)}")
        return jsonify({"packages": [], "error": str(e)}), 500

@npm_bp.route('/<path:pkg_name>/info', methods=['GET'])
def get_package_info(pkg_name):
    # Retrieve package info from Verdaccio API directly
    try:
        pkg = NpmPackage.query.filter_by(name=pkg_name).first()
        db_desc = pkg.description if pkg else None

        response = requests.get(f"{VERDACCIO_URL}/{pkg_name}", headers=auth_header, timeout=5)
        
        if response.status_code == 404:
            return jsonify({
                "name": pkg_name,
                "description": db_desc or "No description",
                "dist-tags": {},
                "versions": [],
                "readme": "No readme found"
            })
            
        response.raise_for_status()
        data = response.json()
        
        versions = data.get('versions', {})
        version_list = []
        for v, info in versions.items():
            author = info.get("author")
            author_str = author.get("name") if isinstance(author, dict) else str(author) if author else "Unknown"
            
            version_list.append({
                "version": v,
                "description": info.get("description", ""),
                "author": author_str,
                "time": data.get("time", {}).get(v)
            })
            
        return jsonify({
            "name": data.get("name", pkg_name),
            "description": data.get("description") or db_desc,
            "dist-tags": data.get("dist-tags", {}),
            "versions": sorted(version_list, key=lambda x: x['version'], reverse=True),
            "readme": data.get("readme", "")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@npm_bp.route('/info', methods=['GET'])
def get_info():
    url = NPM_EXTERNAL_URL
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    return jsonify({
        "external_url": url,
        "username": REGISTRY_USER
    })

