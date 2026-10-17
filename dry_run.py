#!/usr/bin/env python3
"""Dry run with mock failing tests to show what gets created"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from function_app import create_compliance_project, create_task_from_test, create_summary_report

VAULT_NAME = "dkg"

# Mock failing tests
mock_tests = [
    {
        "id": "soc2-mfa-enforcement",
        "name": "Multi-factor authentication enforced for all users",
        "status": "FAILING",
        "description": "All users must have MFA enabled to access company systems. Currently 3 users do not have MFA configured.",
        "remediation": "1. Contact users: john@auracare.com, sarah@auracare.com, mike@auracare.com\n2. Guide them to Security Settings > MFA Setup\n3. Verify MFA is enabled and working\n4. Disable access for any users who refuse to enable MFA"
    },
    {
        "id": "soc2-password-policy",
        "name": "Password policy meets SOC 2 requirements",
        "status": "FAILING",
        "description": "Password policy must require: minimum 12 characters, uppercase, lowercase, numbers, and special characters. Current policy only requires 8 characters.",
        "remediation": "1. Go to Settings > Security > Password Policy\n2. Update minimum length to 12 characters\n3. Enable complexity requirements (uppercase, lowercase, number, special char)\n4. Set password expiration to 90 days\n5. Prevent reuse of last 5 passwords"
    },
    {
        "id": "soc2-access-review",
        "name": "Quarterly access reviews completed",
        "status": "WARNING",
        "description": "Access reviews should be completed quarterly. Last review was completed 95 days ago.",
        "remediation": "1. Schedule access review meeting with security team\n2. Export current user access list from identity provider\n3. Review each user's permissions with their manager\n4. Remove unnecessary access\n5. Document review in compliance folder"
    },
    {
        "id": "soc2-encryption-at-rest",
        "name": "Data encrypted at rest in production database",
        "status": "PASSING",
        "description": "Production databases use AES-256 encryption at rest",
        "remediation": None
    },
    {
        "id": "soc2-audit-logging",
        "name": "Audit logs retained for 1 year",
        "status": "PASSING",
        "description": "All system audit logs are stored in AWS CloudWatch with 365-day retention",
        "remediation": None
    }
]

print("=" * 60)
print("DRY RUN - Vanta Task Sync")
print("=" * 60)
print()

# Show what will be created
failing_tests = [t for t in mock_tests if t.get('status') == 'FAILING']
warning_tests = [t for t in mock_tests if t.get('status') == 'WARNING']

print(f"📊 Mock Vanta Data:")
print(f"   Total tests: {len(mock_tests)}")
print(f"   Failing: {len(failing_tests)}")
print(f"   Warning: {len(warning_tests)}")
print(f"   Passing: {len([t for t in mock_tests if t.get('status') == 'PASSING'])}")
print()

print("=" * 60)
print("Creating Compliance Project")
print("=" * 60)
print()
create_compliance_project(VAULT_NAME)
print("✅ Created: Projects/Compliance.md")
print()

print("=" * 60)
print("Creating Tasks for Failing Tests")
print("=" * 60)
print()
for test in failing_tests:
    print(f"📝 Creating task: {test['name']}")
    print(f"   ID: {test['id']}")
    print(f"   Priority: HIGH")
    print(f"   Status: TODO")
    print()
    create_task_from_test(VAULT_NAME, test, priority='high')
    print(f"✅ Created: Projects/Compliance_tasks/{test['id'].replace('soc2-', '')}")
    print()

print("=" * 60)
print("Creating Tasks for Warning Tests")
print("=" * 60)
print()
for test in warning_tests:
    print(f"⚠️  Creating task: {test['name']}")
    print(f"   ID: {test['id']}")
    print(f"   Priority: MEDIUM")
    print(f"   Status: TODO")
    print()
    create_task_from_test(VAULT_NAME, test, priority='medium')
    print(f"✅ Created: Projects/Compliance_tasks/{test['id'].replace('soc2-', '')}")
    print()

print("=" * 60)
print("Creating Summary Report")
print("=" * 60)
print()
create_summary_report(VAULT_NAME, mock_tests)
print("✅ Created: Compliance/Vanta/Vanta Security Tests.md")
print()

print("=" * 60)
print("✅ DRY RUN COMPLETE")
print("=" * 60)
print()
print("Check Obsidian vault:")
print("  1. Projects/Compliance.md - Main project")
print("  2. Projects/Compliance_tasks/ - 3 task files created")
print("  3. Compliance/Vanta/Vanta Security Tests.md - Summary")
print()
print("Task files created:")
print("  - mfa-enforcement.md (HIGH priority)")
print("  - password-policy.md (HIGH priority)")
print("  - access-review.md (MEDIUM priority)")
print()
