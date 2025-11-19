#!/usr/bin/env python3

# This script checks the locally modified packages, and then compares the newly generated manifests against
# the ones that are already on the server. Then it posts this diff as a comment on the PR. It's called from the CI

import os
import sys
import json
import urllib.request
import urllib.error
import difflib

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')
PR_NUMBER = os.environ.get('PR_NUMBER')

def fetch_current_manifest(package: str, cdn_url: str):
    manifest_url = f"{cdn_url}/packages/{package}/manifest.install"
    try:
        req = urllib.request.Request(manifest_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            return [line.strip() for line in content.strip().split('\n') if line.strip()]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # no remote package
        raise
    except Exception as e:
        print(f"WARNING: Could not fetch manifest for {package}: {e}")
        return None

def read_local_manifest(package: str):
    manifest_path = f'packages/{package}/manifest.install'
    
    try:
        with open(manifest_path, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"WARNING: Could not find local manifest for {package} at {manifest_path}")
        return None

# reads the txt that spinarak produces for packages that were rebuilt
def get_updated_packages():
    try:
        with open('packages/updated_packages.txt', 'r') as f:
            updated_pkgs = f.read().strip().split(',')
            return [p.strip() for p in updated_pkgs if p.strip()]
    except FileNotFoundError:
        print("WARNING: No updated_packages.txt found")
        return []

def create_manifest_diff(package: str, old_manifest, new_manifest):
    if old_manifest is None:
        return f"### New Manifest: `{package}`\n\n```\n" + '\n'.join(new_manifest) + "\n```\n"
    
    if old_manifest == new_manifest:
        return f"### Manifest Check: `{package}`\n\n✅ File layout looks good: Manifest matches the previous version\n"
    
    # Create unified diff
    diff = list(difflib.unified_diff(
        old_manifest,
        new_manifest,
        lineterm=''
    ))
    
    if not diff:
        return f"### Manifest Check: `{package}`\n\n✅ File layout looks good: Manifest is unchanged from the previous version\n"
    
    diff_text = '\n'.join(diff[2:]) # skip first 2 lines which are just file headers
    
    return f"""### Manifest Diff: `{package}`

The following files would be added/removed on update:

```diff
{diff_text}
```
"""

def save_comment_to_file(comment_body: str):
    with open('comment.md', 'w') as f:
        f.write(comment_body)
    
    if PR_NUMBER:
        with open('pr_number.txt', 'w') as f:
            f.write(PR_NUMBER)
    print(f"Saved comment for PR #{PR_NUMBER} to comment.md and pr_number.txt")

def main():
    if len(sys.argv) < 2:
        print("Usage: python post_pr_comment.py <cdn_url>")
        sys.exit(1)
    
    cdn_url = sys.argv[1]
    print(f"Using CDN URL: {cdn_url}")
    
    package_names = get_updated_packages()
    
    if not package_names:
        print("No packages to process")
        return
    
    print(f"Found {len(package_names)} package(s) to report on: {package_names}")
    
    comment_parts = []
    
    for package in sorted(package_names):
        print(f"Processing {package}...")
        
        new_manifest = read_local_manifest(package)
        if new_manifest is None:
            print(f"Skipping {package} - no local manifest found")
            continue
        
        old_manifest = fetch_current_manifest(package, cdn_url)
        
        diff = create_manifest_diff(package, old_manifest, new_manifest)
        comment_parts.append(diff)
    
    comment_body = '\n\n'.join(comment_parts)
    
    # save to file for build artifacts
    save_comment_to_file(comment_body)

if __name__ == '__main__':
    main()
