#!/usr/bin/env python3
"""
Local test script for Vanta → Obsidian sync
Run this to test the integration before deploying to Azure
"""

import requests
import json
import subprocess
from datetime import datetime
import os

# Configuration - update these if needed
VANTA_CLIENT_ID = "vci_0c07415a383df9d0b51c0632cfd9054707cab45b52c933d7"
VANTA_CLIENT_SECRET = "vcs_0f13cb_9cc81e1480ccf46bd9143d4c81e557e23008a0a915568b1c98b680c4dd89a666"
OBSIDIAN_VAULT_PATH = "Compliance/Vanta"

def test_vanta_api():
    """Test connection to Vanta API and fetch data"""
    print("🔐 Testing Vanta OAuth...")

    try:
        # Get OAuth access token using JSON body (Vanta's documented method)
        print("Authenticating with Vanta OAuth...")

        token_response = requests.post(
            'https://api.vanta.com/oauth/token',
            headers={'Content-Type': 'application/json'},
            json={
                'client_id': VANTA_CLIENT_ID,
                'client_secret': VANTA_CLIENT_SECRET,
                'scope': 'vanta-api.all:read',
                'grant_type': 'client_credentials'
            }
        )

        print(f"Response status: {token_response.status_code}")
        if token_response.status_code != 200:
            print(f"Response body: {token_response.text}")

        token_response.raise_for_status()
        access_token = token_response.json()['access_token']
        print("✅ Successfully authenticated with Vanta")

        # Fetch tests
        print("\n📊 Fetching security tests...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        tests_response = requests.get(
            'https://api.vanta.com/v1/tests',
            headers=headers
        )
        tests_response.raise_for_status()
        response_json = tests_response.json()

        # Vanta API returns {results: {data: [...], pageInfo: {...}}}
        results = response_json.get('results', {})
        tests = results.get('data', [])

        tests_data = {'results': tests}  # Normalize for downstream processing

        passing = sum(1 for t in tests if isinstance(t, dict) and t.get('status') == 'PASSING')
        failing = sum(1 for t in tests if t.get('status') == 'FAILING')
        warning = sum(1 for t in tests if t.get('status') == 'WARNING')

        print(f"✅ Fetched {len(tests)} tests:")
        print(f"   - Passing: {passing}")
        print(f"   - Failing: {failing}")
        print(f"   - Warnings: {warning}")

        return tests_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Vanta API error: {str(e)}")
        return None

def generate_markdown(tests_data):
    """Generate markdown from Vanta data"""
    print("\n📝 Generating markdown...")

    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    tests = tests_data.get('results', [])

    md = f"""---
title: Vanta Security Tests
updated: {now}
tags: [compliance, vanta, security]
---

# Vanta Security Tests & Checks

> Last synced: {now}

## Summary

"""

    passing = sum(1 for t in tests if t.get('status') == 'PASSING')
    failing = sum(1 for t in tests if t.get('status') == 'FAILING')
    warning = sum(1 for t in tests if t.get('status') == 'WARNING')
    total = len(tests)

    md += f"""- **Total Tests**: {total}
- **Passing**: ✅ {passing}
- **Failing**: ❌ {failing}
- **Warnings**: ⚠️ {warning}

---

## Failing Tests

"""

    failing_tests = [t for t in tests if t.get('status') == 'FAILING']
    if failing_tests:
        for test in failing_tests:
            md += f"""### ❌ {test.get('displayName', 'Unknown Test')}

**ID**: `{test.get('id', 'N/A')}`
**Status**: {test.get('status', 'UNKNOWN')}
**Description**: {test.get('description', 'No description available')}

"""
            if test.get('remediation'):
                md += f"**Remediation**: {test['remediation']}\n\n"
            md += "---\n\n"
    else:
        md += "No failing tests! 🎉\n\n"

    print(f"✅ Generated {len(md)} characters of markdown")
    return md

def test_obsidian_cli(content):
    """Test writing to Obsidian vault using CLI"""
    print("\n📓 Testing Obsidian CLI...")

    # Check if obsidian CLI is available
    try:
        result = subprocess.run(
            ['obsidian', '--help'],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Obsidian CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("❌ Obsidian CLI not found. Please install it first.")
        print("   Install: npm install -g obsidian-cli")
        return False

    # Write test file
    timestamp = datetime.utcnow().strftime('%Y-%m-%d')
    test_path = f"{OBSIDIAN_VAULT_PATH}/Vanta Security Tests - {timestamp}"

    try:
        print(f"   Writing to: {test_path}")

        cmd = [
            'obsidian',
            'create',
            f'path={test_path}',
            f'content={content}',
            'overwrite'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print(f"✅ Successfully wrote to Obsidian vault!")
        print(f"   File: {test_path}.md")

        # Also write the "latest" version
        cmd_latest = [
            'obsidian',
            'create',
            f'path={OBSIDIAN_VAULT_PATH}/Vanta Security Tests',
            f'content={content}',
            'overwrite'
        ]

        subprocess.run(cmd_latest, capture_output=True, text=True, check=True)
        print(f"✅ Updated latest version")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Obsidian CLI failed: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("Vanta → Obsidian Sync - Local Test")
    print("=" * 60)

    # Test 1: Vanta API
    tests_data = test_vanta_api()
    if not tests_data:
        print("\n❌ Vanta API test failed. Check your credentials.")
        return

    # Test 2: Generate markdown
    markdown = generate_markdown(tests_data)

    # Test 3: Obsidian CLI
    success = test_obsidian_cli(markdown)

    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Ready to deploy to Azure.")
        print("\nNext steps:")
        print("  1. Run: ./deploy.sh")
        print("  2. Check logs: az functionapp log tail --name vanta-obsidian-sync --resource-group auracare-rg")
        print(f"  3. View results in: /Users/akn/projects/auracare/dkg/{OBSIDIAN_VAULT_PATH}/")
    else:
        print("❌ Some tests failed. Fix issues before deploying.")
    print("=" * 60)

if __name__ == "__main__":
    main()
