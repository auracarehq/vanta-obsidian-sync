#!/usr/bin/env python3
"""Test the task creation functionality"""

import sys
sys.path.insert(0, '/Users/akn/projects/auracare/vanta-sync-function')

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
tests_response = requests.get(
    'https://api.vanta.com/v1/tests',
    headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
)
tests_response.raise_for_status()
response_json = tests_response.json()
results = response_json.get('results', {})
tests = results.get('data', [])
print(f"✅ Fetched {len(tests)} tests\n")

# Create project
print("📁 Creating Compliance project...")
create_compliance_project(VAULT_NAME)
print("✅ Project created\n")

# Create tasks for failing/warning tests
failing_tests = [t for t in tests if t.get('status') == 'FAILING']
warning_tests = [t for t in tests if t.get('status') == 'WARNING']

print(f"📝 Creating {len(failing_tests)} failing test tasks...")
for test in failing_tests:
    create_task_from_test(VAULT_NAME, test, priority='high')
    print(f"  ✅ {test.get('name', 'Unknown')}")

print(f"\n📝 Creating {len(warning_tests)} warning test tasks...")
for test in warning_tests:
    create_task_from_test(VAULT_NAME, test, priority='medium')
    print(f"  ✅ {test.get('name', 'Unknown')}")

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
