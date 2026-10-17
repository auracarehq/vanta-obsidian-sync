#!/usr/bin/env python3
"""Test the task creation functionality"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from function_app import create_compliance_project, create_task_from_test, create_summary_report
import requests

# Credentials
VANTA_CLIENT_ID = "vci_0c07415a383df9d0b51c0632cfd9054707cab45b52c933d7"
VANTA_CLIENT_SECRET = "vcs_0f13cb_9cc81e1480ccf46bd9143d4c81e557e23008a0a915568b1c98b680c4dd89a666"
VAULT_NAME = "dkg"

print("🔐 Authenticating with Vanta...")
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
token_response.raise_for_status()
access_token = token_response.json()['access_token']
print("✅ Authenticated\n")

print("📊 Fetching tests...")
all_tests = []
cursor = None
page = 1

while True:
    url = 'https://api.vanta.com/v1/tests'
    if cursor:
        url += f'?after={cursor}'

    tests_response = requests.get(
        url,
        headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
    )
    tests_response.raise_for_status()
    response_json = tests_response.json()

    results = response_json.get('results', {})
    page_tests = results.get('data', [])
    page_info = results.get('pageInfo', {})

    all_tests.extend(page_tests)
    print(f"   Page {page}: {len(page_tests)} tests (hasNextPage: {page_info.get('hasNextPage')})")

    if not page_info.get('hasNextPage'):
        break

    cursor = page_info.get('endCursor')
    page += 1

tests = all_tests
print(f"✅ Total fetched: {len(tests)} tests\n")

# Create project
print("📁 Creating Compliance project...")
create_compliance_project(VAULT_NAME)
print("✅ Project created\n")

# Create tasks for failing tests (Vanta uses NEEDS_ATTENTION/FAIL, not FAILING/WARNING)
failing_tests = [t for t in tests if t.get('status') in ['FAIL', 'NEEDS_ATTENTION']]

print(f"📝 Creating {len(failing_tests)} tasks for tests needing attention...")
for test in failing_tests:
    priority = 'high' if test.get('status') == 'FAIL' else 'medium'
    create_task_from_test(VAULT_NAME, test, priority=priority)
    status_emoji = '❌' if test.get('status') == 'FAIL' else '⚠️'
    print(f"  {status_emoji} {test.get('name', 'Unknown')}")

# Create summary
print("\n📄 Creating summary report...")
create_summary_report(VAULT_NAME, tests)
print("✅ Summary created\n")

print("=" * 60)
print("✅ All done! Check Obsidian:")
print("  - Projects/Compliance.md")
print("  - Projects/Compliance_tasks/")
print("  - Compliance/Vanta/Vanta Security Tests.md")
print("=" * 60)
