#!/usr/bin/env python3

import requests
import json
import sys
import argparse
from requests.auth import HTTPBasicAuth

# Configuration
API_BASE = "http://localhost:8000"  # Change to your production URL
USERNAME = "john"
PASSWORD = "doe"

def import_data(filename, api_base=API_BASE, username=USERNAME, password=PASSWORD):
    """
    Import health data from JSON export file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}")
        return

    print(f"Found {len(entries)} entries in {filename}")
    print(f"Using API: {api_base}")

    success_count = 0
    error_count = 0

    for i, entry in enumerate(entries, 1):
        try:
            response = requests.post(
                f"{api_base}/entries/",
                json=entry,
                auth=HTTPBasicAuth(username, password),
                timeout=30  # 30 second timeout
            )

            if response.status_code in [200, 201]:
                operation = response.headers.get('X-Operation', 'unknown')
                print(f"✅ [{i}/{len(entries)}] {entry['date']} - {operation}")
                success_count += 1
            else:
                print(f"❌ [{i}/{len(entries)}] {entry['date']} - HTTP {response.status_code}: {response.text}")
                error_count += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ [{i}/{len(entries)}] {entry['date']} - Network error: {e}")
            error_count += 1
        except KeyError:
            print(f"❌ [{i}/{len(entries)}] Entry missing 'date' field")
            error_count += 1

    print(f"\n📊 Import Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {error_count}")
    print(f"   📋 Total: {len(entries)}")

def main():
    parser = argparse.ArgumentParser(description='Import health data from JSON export')
    parser.add_argument('filename', help='JSON file to import')
    parser.add_argument('--api-base', default=API_BASE,
                       help=f'API base URL (default: {API_BASE})')
    parser.add_argument('--username', default=USERNAME,
                       help=f'Basic Auth username (default: {USERNAME})')
    parser.add_argument('--password', default=PASSWORD,
                       help=f'Basic Auth password (default: {PASSWORD})')

    args = parser.parse_args()

    import_data(
        filename=args.filename,
        api_base=args.api_base,
        username=args.username,
        password=args.password
    )

if __name__ == "__main__":
    main()