import azure.functions as func
import logging
import requests
import json
from datetime import datetime, UTC
import os
import subprocess
import re

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 */6 * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False)
def vanta_sync_timer(myTimer: func.TimerRequest) -> None:
    """
    Azure Function that syncs Vanta security tests to Obsidian vault as tasks every 6 hours.
    Creates tasks in Projects/Compliance_tasks/ for each failing test.
    """
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Vanta sync function started at %s', datetime.now(UTC))

    # Get credentials from environment variables
    vanta_client_id = os.environ.get('VANTA_CLIENT_ID')
    vanta_client_secret = os.environ.get('VANTA_CLIENT_SECRET')
    vault_name = os.environ.get('OBSIDIAN_VAULT_NAME', 'dkg')

    if not vanta_client_id or not vanta_client_secret:
        logging.error('Missing Vanta OAuth credentials in environment variables')
        return

    try:
        # Step 1: Get OAuth access token from Vanta
        token_response = requests.post(
            'https://api.vanta.com/oauth/token',
            headers={'Content-Type': 'application/json'},
            json={
                'client_id': vanta_client_id,
                'client_secret': vanta_client_secret,
                'scope': 'vanta-api.all:read',
                'grant_type': 'client_credentials'
            }
        )
        token_response.raise_for_status()
        access_token = token_response.json()['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        # Step 2: Fetch security tests from Vanta API
        logging.info('Fetching security tests from Vanta API')
        tests_response = requests.get(
            'https://api.vanta.com/v1/tests',
            headers=headers
        )
        tests_response.raise_for_status()
        response_json = tests_response.json()

        # Vanta API returns {results: {data: [...], pageInfo: {...}}}
        results = response_json.get('results', {})
        tests = results.get('data', [])

        # Step 3: Create Compliance project if needed
        create_compliance_project(vault_name)

        # Step 4: Create tasks for failing tests
        failing_tests = [t for t in tests if t.get('status') == 'FAILING']
        warning_tests = [t for t in tests if t.get('status') == 'WARNING']

        logging.info(f'Found {len(failing_tests)} failing tests and {len(warning_tests)} warnings')

        for test in failing_tests:
            create_task_from_test(vault_name, test, priority='high')

        for test in warning_tests:
            create_task_from_test(vault_name, test, priority='medium')

        # Step 5: Also create summary report
        create_summary_report(vault_name, tests)

        logging.info('Vanta sync completed successfully at %s', datetime.now(UTC))

    except requests.exceptions.RequestException as e:
        logging.error(f'API request failed: {str(e)}')
        raise
    except Exception as e:
        logging.error(f'Vanta sync failed: {str(e)}')
        raise


def create_compliance_project(vault_name):
    """Create or update the Compliance project file."""
    now = datetime.now(UTC).strftime('%Y-%m-%d')

    project_content = f"""---
type: pm-project
tags: [project/compliance, vanta]
icon: ""
status: active
---

# Compliance

Automated compliance tracking from Vanta security tests.

**Auto-synced:** Every 6 hours from Vanta API

## Overview

This project tracks security compliance issues identified by Vanta. Tasks are automatically created for:
- ❌ Failing tests (high priority)
- ⚠️ Warning tests (medium priority)

## Links

- [[Compliance/Vanta/Vanta Security Tests]] - Latest test summary
- [Vanta Dashboard](https://app.vanta.com) - Full interface

---

*Last updated: {now}*
"""

    cmd = [
        'obsidian',
        'create',
        f'vault={vault_name}',
        'path=Projects/Compliance',
        f'content={project_content}',
        'overwrite'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    logging.info('Created/updated Compliance project')


def create_task_from_test(vault_name, test, priority='medium'):
    """Create a task file for a failing Vanta test."""
    test_id = test.get('id', 'unknown')
    test_name = test.get('name', 'Unknown Test')
    test_status = test.get('status', 'UNKNOWN')
    description = test.get('description', 'No description available')
    remediation = test.get('remediation', 'No remediation steps provided')

    # Sanitize test_id for filename
    safe_id = re.sub(r'[^a-z0-9-]', '-', test_id.lower())

    now = datetime.now(UTC)
    created = now.strftime('%Y-%m-%d')
    due_date = now.replace(day=now.day + 7).strftime('%Y-%m-%d')  # 7 days from now

    status_emoji = '❌' if test_status == 'FAILING' else '⚠️'

    task_content = f"""---
type: task
tags: [compliance, vanta, {test_status.lower()}]
icon: ""
status: todo
priority: {priority}
created: {created}
due: {due_date}
---

# {status_emoji} {test_name}

**Vanta Test ID:** `{test_id}`
**Status:** {test_status}
**Priority:** {priority.capitalize()}

## Description

{description}

## Remediation Steps

{remediation}

## Links

- [View in Vanta](https://app.vanta.com/tests/{test_id})
- [[Compliance/Vanta/Vanta Security Tests]] - Full test report

---

*Auto-created from Vanta sync*
"""

    task_path = f"Projects/Compliance_tasks/{safe_id}"

    cmd = [
        'obsidian',
        'create',
        f'vault={vault_name}',
        f'path={task_path}',
        f'content={task_content}',
        'overwrite'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    logging.info(f'Created task: {task_path}')


def create_summary_report(vault_name, tests):
    """Create summary report in Compliance/Vanta folder."""
    now = datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')
    timestamp = datetime.now(UTC).strftime('%Y-%m-%d')

    passing = sum(1 for t in tests if t.get('status') == 'PASSING')
    failing = sum(1 for t in tests if t.get('status') == 'FAILING')
    warning = sum(1 for t in tests if t.get('status') == 'WARNING')
    total = len(tests)

    summary_content = f"""---
title: Vanta Security Tests Summary
updated: {now}
tags: [compliance, vanta, security]
---

# Vanta Security Tests Summary

> Last synced: {now}

## Statistics

- **Total Tests**: {total}
- **Passing**: ✅ {passing}
- **Failing**: ❌ {failing}
- **Warnings**: ⚠️ {warning}

## Tasks Created

Failing and warning tests are automatically created as tasks in:
- [[Projects/Compliance]] - Compliance project
- `Projects/Compliance_tasks/` - Individual task files

## All Tests

"""

    # Group by status
    for status in ['FAILING', 'WARNING', 'PASSING']:
        status_tests = [t for t in tests if t.get('status') == status]
        if not status_tests:
            continue

        emoji = {'FAILING': '❌', 'WARNING': '⚠️', 'PASSING': '✅'}[status]
        summary_content += f"\n### {emoji} {status.capitalize()} ({len(status_tests)})\n\n"

        for test in status_tests:
            name = test.get('name', 'Unknown')
            test_id = test.get('id', 'N/A')
            summary_content += f"- {name} (`{test_id}`)\n"

    summary_content += "\n---\n\n*Automatically generated by Vanta sync function*\n"

    # Write to Compliance/Vanta folder
    cmd = [
        'obsidian',
        'create',
        f'vault={vault_name}',
        'path=Compliance/Vanta/Vanta Security Tests',
        f'content={summary_content}',
        'overwrite'
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    logging.info('Created summary report')
