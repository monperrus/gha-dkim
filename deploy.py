#!/usr/bin/python
# upload a file to a server
"""
GitHub Action for continuous deployment with DKIM authentication

Usage:
    python deploy.py --server <server_url> --file_to_deploy <file_path> --signing_address <email> [--pem_private_key_path <path>]

Environment variables:
    GITHUB_REPOSITORY: GitHub repository name (e.g., owner/repo)
    GITHUB_SHA: Current commit SHA
    GITHUB_REF: Current git reference (e.g., refs/heads/main)
"""
import requests
import os
import sys
import dkim
import argparse
import socket
import datetime

def get_fallback_repository():
    """Generate a fallback repository name if GITHUB_REPOSITORY is not set"""
    return f"unknown-{socket.gethostname()}"

def get_fallback_sha():
    """Generate a fallback SHA if GITHUB_SHA is not set"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"local-{timestamp}"

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Upload a file to a server with DKIM authentication')
    parser.add_argument('--server', required=True, help='The target server URL')
    parser.add_argument('--file_to_deploy', required=True, help='Path to the file to deploy')
    parser.add_argument('--signing_address', required=True, help='Email address used for signing (e.g., user@example.com)')
    parser.add_argument('--pem_private_key_path', default="gha.pem", 
                        help='Path to the PEM private key file for DKIM signing (default: gha.pem)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Extract domain and selector from signing address
    email_parts = args.signing_address.split('@')
    if len(email_parts) != 2:
        print(f"Error: Invalid signing address format: {args.signing_address}")
        sys.exit(1)
    
    domain = email_parts[1]
    selector = email_parts[0]
    
    # Check if private key file exists
    if not os.path.exists(args.pem_private_key_path):
        print(f"Error: Private key file not found: {args.pem_private_key_path}")
        sys.exit(1)
    
    # Check if file to deploy exists
    if not os.path.exists(args.file_to_deploy):
        print(f"Error: File not found: {args.file_to_deploy}")
        sys.exit(1)
    
    url = args.server
    file_path = args.file_to_deploy
    file_name = os.path.basename(file_path)

    # Get GitHub environment variables with fallbacks
    github_repo = os.environ.get('GITHUB_REPOSITORY')
    if not github_repo:
        github_repo = get_fallback_repository()
        print(f"Warning: GITHUB_REPOSITORY not set, using fallback: {github_repo}")
        
    github_sha = os.environ.get('GITHUB_SHA')
    if not github_sha:
        github_sha = get_fallback_sha()
        print(f"Warning: GITHUB_SHA not set, using fallback: {github_sha}")
        
    github_ref = os.environ.get('GITHUB_REF', 'unknown')

    with open(file_path, 'rb') as file:
        file_content = file.read()
        # Sign the message
        fromheader = args.signing_address
        data = f"From: {fromheader}\n\n".encode()+file_content
        
        try:
            signature = dkim.sign(
                message=data,
                selector=selector.encode(),
                domain=domain.encode(),
                privkey=open(args.pem_private_key_path).read().encode(),
                include_headers=['From'],
                canonicalize=(b'relaxed', b'relaxed')
            )
            
            headers = {
                'From': fromheader,
                'DKIM-Signature': signature.decode().split(":")[1].strip().replace("\r\n",""),
                'Content-Type': 'application/data',
                'Content-Disposition': f'attachment; filename="{file_name}"',
                'X-GitHub-Repository': github_repo,
                'X-GitHub-SHA': github_sha
            }
            
            # Add GitHub ref if available
            if github_ref != 'unknown':
                headers['X-GitHub-Ref'] = github_ref.replace('refs/heads/', '')
            
            print(f"Sending file with headers: {headers}")
            response = requests.post(url, data=file_content, headers=headers)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code >= 400:
                sys.exit(1)
                
        except Exception as e:
            print(f"Error during signing or upload: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
