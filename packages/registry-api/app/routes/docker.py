from flask import Blueprint, jsonify, request
import requests
import base64
import os
import re
from app.models import DockerRepository
import concurrent.futures

docker_bp = Blueprint('docker', __name__)

# Registry URL inside the docker network
REGISTRY_URL = os.getenv('REGISTRY_INTERNAL_URL', 'http://registry:5000')
# Registry URL for external access (for hints in UI)
REGISTRY_EXTERNAL_URL = os.getenv('REGISTRY_EXTERNAL_URL', 'localhost:5005')

# Basic Auth for the registry
REGISTRY_USER = 'admin'
REGISTRY_PASS = 'admin'
auth_header = {'Authorization': 'Basic ' + base64.b64encode(f"{REGISTRY_USER}:{REGISTRY_PASS}".encode()).decode()}

@docker_bp.route('/auth_check', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
def auth_check():
    original_method = request.headers.get('X-Original-Method', request.method)
    original_uri = request.headers.get('X-Original-URI', request.path)
    
    # Allow read requests
    if original_method in ['GET', 'HEAD', 'OPTIONS']:
        return "OK", 200
        
    # Match /v2/<repo_name>/(blobs|manifests|tags)/...
    match = re.match(r'^/v2/(.*?)/(blobs|manifests|tags)($|/)', original_uri)
    if not match:
        return "OK", 200
        
    repo_name = match.group(1)
    
    # Verify if repo exists in our database
    repo = DockerRepository.query.filter_by(name=repo_name).first()
    if not repo:
        return jsonify({"error": f"Repository '{repo_name}' not found. Please create it in the Admin panel first."}), 403
        
    return "OK", 200

@docker_bp.route('/catalog', methods=['GET'])
def get_catalog():
    try:
        # Get from our DB first
        db_repos = DockerRepository.query.all()
        db_repo_names = {r.name for r in db_repos}
        
        # Merge with actual registry catalog if any exist
        try:
            response = requests.get(f"{REGISTRY_URL}/v2/_catalog", headers=auth_header, timeout=5)
            if response.status_code == 200:
                registry_repos = response.json().get('repositories', [])
                db_repo_names.update(registry_repos)
        except Exception:
            pass # Ignore registry connection errors here, show db repos at least
            
        return jsonify({
            "repositories": sorted(list(db_repo_names))
        })
    except Exception as e:
        print(f"Docker Catalog Error: {str(e)}")
        return jsonify({"repositories": [], "error": str(e)}), 500

@docker_bp.route('/<path:repo>/tags', methods=['GET'])
def get_tags(repo):
    try:
        response = requests.get(f"{REGISTRY_URL}/v2/{repo}/tags/list", headers=auth_header)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@docker_bp.route('/<path:repo>/tags/details', methods=['GET'])
def get_tags_details(repo):
    try:
        response = requests.get(f"{REGISTRY_URL}/v2/{repo}/tags/list", headers=auth_header)
        if response.status_code == 404:
            return jsonify({"tags": []})
        response.raise_for_status()
        tags = response.json().get('tags', [])
        
        if not tags:
            return jsonify({"tags": []})
            
        def fetch_tag_detail(tag):
            try:
                accepts = [
                    'application/vnd.docker.distribution.manifest.v2+json',
                    'application/vnd.docker.distribution.manifest.list.v2+json',
                    'application/vnd.oci.image.manifest.v1+json',
                    'application/vnd.oci.image.index.v1+json'
                ]
                headers = {**auth_header, 'Accept': ', '.join(accepts)}
                m_res = requests.get(f"{REGISTRY_URL}/v2/{repo}/manifests/{tag}", headers=headers)
                if m_res.status_code != 200:
                    return {"tag": tag, "error": f"manifest not found: {m_res.status_code}"}
                
                digest = m_res.headers.get('Docker-Content-Digest')
                manifest = m_res.json()
                
                # Check for manifest list / OCI index
                media_type = manifest.get('mediaType', '')
                if 'list.v2+json' in media_type or 'index.v1+json' in media_type:
                    manifests = manifest.get('manifests', [])
                    if manifests:
                        # Fetch the first manifest in the list (usually linux/amd64 or the only available one) to get the config blob info
                        sub_digest = manifests[0].get('digest')
                        m_res2 = requests.get(f"{REGISTRY_URL}/v2/{repo}/manifests/{sub_digest}", headers=headers)
                        if m_res2.status_code == 200:
                            manifest = m_res2.json()

                # At this point, manifest should be a concrete image manifest
                # Size calculation: config size + all layer sizes
                size = manifest.get('config', {}).get('size', 0)
                for layer in manifest.get('layers', []):
                    size += layer.get('size', 0)
                    
                config_digest = manifest.get('config', {}).get('digest')
                created_at = None
                
                if config_digest:
                    c_res = requests.get(f"{REGISTRY_URL}/v2/{repo}/blobs/{config_digest}", headers=auth_header, timeout=3)
                    if c_res.status_code == 200:
                        created_at = c_res.json().get('created')
                        
                return {
                    "tag": tag,
                    "digest": digest,
                    "size": size,
                    "created_at": created_at
                }
            except Exception as e:
                return {"tag": tag, "error": str(e)}

        details = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for result in executor.map(fetch_tag_detail, tags):
                details.append(result)
                
        def get_time(item):
            return item.get("created_at") or ""
            
        details.sort(key=get_time, reverse=True)
        
        return jsonify({"tags": details})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@docker_bp.route('/<path:repo>/manifest/<tag>', methods=['GET'])
def get_manifest(repo, tag):
    try:
        # We need the digest for deletion, so we request the manifest with the required accept header
        headers = {**auth_header, 'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
        response = requests.get(f"{REGISTRY_URL}/v2/{repo}/manifests/{tag}", headers=headers)
        response.raise_for_status()
        
        digest = response.headers.get('Docker-Content-Digest')
        manifest = response.json()
        
        return jsonify({
            "repo": repo,
            "tag": tag,
            "digest": digest,
            "manifest": manifest
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@docker_bp.route('/<path:repo>/manifest/<digest>', methods=['DELETE'])
def delete_artifact(repo, digest):
    try:
        response = requests.delete(f"{REGISTRY_URL}/v2/{repo}/manifests/{digest}", headers=auth_header)
        response.raise_for_status()
        return jsonify({"message": "Deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@docker_bp.route('/info', methods=['GET'])
def get_info():
    return jsonify({
        "external_url": REGISTRY_EXTERNAL_URL,
        "username": REGISTRY_USER
    })
