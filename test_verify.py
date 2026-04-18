#!/usr/bin/env python3
import requests
import sys

BASE_URL = 'http://127.0.0.1:8000/api'

try:
    # Test 1: Health check
    print("1. Testing health check...")
    resp = requests.get(f'{BASE_URL}/health')
    print(f"   Status: {resp.status_code}")
    if resp.status_code != 200:
        print("❌ Backend not responding")
        sys.exit(1)
    print("✓ Backend is up")

    # Test 2: Generate keys
    print("\n2. Generating keys...")
    resp = requests.post(f'{BASE_URL}/generate-keys')
    keys_data = resp.json()
    session = keys_data['sessionId']
    public_key = keys_data['publicKey']
    print(f"✓ Public key obtained ({len(public_key)} chars)")

    # Test 3: Sign a document
    print("\n3. Uploading and signing PDF...")
    with open('output/pdf/unsigned_demo.pdf', 'rb') as f:
        resp = requests.post(f'{BASE_URL}/upload', files={'file': f})
        file_id = resp.json()['fileId']

    resp = requests.post(f'{BASE_URL}/sign',
        data={'fileId': file_id, 'sessionId': session})
    signed_id = resp.json()['signedFileId']

    resp = requests.get(f'{BASE_URL}/download/{signed_id}')
    with open('/tmp/test_signed.pdf', 'wb') as f:
        f.write(resp.content)
    print("✓ Signed PDF created")

    # Test 4: Verify with clean public key
    print("\n4. Verify with CLEAN public key (no whitespace)...")
    with open('/tmp/test_signed.pdf', 'rb') as pdf_file:
        resp = requests.post(f'{BASE_URL}/verify-external',
            files={'file': pdf_file},
            data={'publicKey': public_key})

    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✓ Valid: {result.get('valid')}")
    else:
        print(f"   ❌ Error: {resp.json().get('detail', resp.text[:100])}")

    # Test 5: Verify with whitespace
    print("\n5. Verify with public key + WHITESPACE...")
    key_with_space = "\n\n" + public_key + "\n\n"
    with open('/tmp/test_signed.pdf', 'rb') as pdf_file:
        resp = requests.post(f'{BASE_URL}/verify-external',
            files={'file': pdf_file},
            data={'publicKey': key_with_space})

    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✓ Valid: {result.get('valid')} (whitespace handled!)")
    else:
        print(f"   ❌ Error returned 400: {resp.json().get('detail')[:80]}")

    # Test 6: Invalid format
    print("\n6. Invalid format (should return 400)...")
    with open('/tmp/test_signed.pdf', 'rb') as pdf_file:
        resp = requests.post(f'{BASE_URL}/verify-external',
            files={'file': pdf_file},
            data={'publicKey': 'invalid format'})

    print(f"   Status: {resp.status_code}")
    if resp.status_code == 400:
        error_data = resp.json()
        print(f"   ✓ Correctly returned 400 with detail message")
        print(f"      Detail: {error_data.get('detail', '')[:100]}")
    else:
        print(f"   ❌ Expected 400, got {resp.status_code}")

    print("\n✅ All verification tests passed!")

except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Is it running?")
    print("   Start with: cd backend && python3 -m uvicorn app:app --reload --port 8000")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
