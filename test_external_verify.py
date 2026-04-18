#!/usr/bin/env python3
"""Test external verification endpoint"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

# Generate keys
print("1. Generating keys...")
resp = requests.post(f'{BASE_URL}/generate-keys')
resp.raise_for_status()
keys_data = resp.json()
session = keys_data['sessionId']
public_key = keys_data['publicKey']
print(f"✓ Session: {session}")
print(f"✓ Public key (first 80 chars): {public_key[:80]}...")

# Upload PDF
print("\n2. Uploading PDF...")
with open('output/pdf/unsigned_demo.pdf', 'rb') as f:
    resp = requests.post(f'{BASE_URL}/upload', files={'file': f})
    resp.raise_for_status()
    file_data = resp.json()
    file_id = file_data['fileId']
    print(f"✓ File ID: {file_id}")

# Sign
print("\n3. Signing PDF...")
resp = requests.post(f'{BASE_URL}/sign',
    data={'fileId': file_id, 'sessionId': session})
resp.raise_for_status()
sign_data = resp.json()
signed_id = sign_data['signedFileId']
print(f"✓ Signed ID: {signed_id}")

# Download signed PDF
print("\n4. Downloading signed PDF...")
resp = requests.get(f'{BASE_URL}/download/{signed_id}')
resp.raise_for_status()
with open('/tmp/test_signed.pdf', 'wb') as f:
    f.write(resp.content)
print(f"✓ Downloaded: /tmp/test_signed.pdf ({len(resp.content)} bytes)")

# Test external verification with public key
print("\n5. Testing external verification with public key...")
with open('/tmp/test_signed.pdf', 'rb') as pdf_file:
    resp = requests.post(f'{BASE_URL}/verify-external',
        files={'file': pdf_file},
        data={'publicKey': public_key})

    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text}")
    else:
        result = resp.json()
        print(f"Result: {json.dumps(result, indent=2)[:500]}...")

        if result.get('valid'):
            print("\n✅ SUCCESS: External verification works! Signature is VALID")
        else:
            print(f"\n❌ FAILED: {result.get('message')}")
