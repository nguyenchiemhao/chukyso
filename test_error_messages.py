#!/usr/bin/env python3
"""Test error handling for external verify (PUBLIC KEY mode)."""
import requests
import sys

BASE_URL = 'http://127.0.0.1:8000/api'

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs/KOOPKZyuTfBtF7abzr
SlzfA818PPdfD4sDFjjgS/BC7J6jZ2VF0sIu7Sp2H4VASU+t0M3BZm0a9DiF/qZG
snnp5NLNOxdcihWSJ4NqfA2g0rdfxUeghSvRqNc9rKis2Yw+I8xgcc23WPOH2mti
YWI7HXMbKa27evKLEeP+ldFrGPoNmEpyLqPnlyjuXFVADh3DnDe2HYm4kPO7fLPg
FQVs5ueb9edlSd26wm3hDxmX5Yc6IIim0lyhFx+y3NUfskVnnvceRgob7LzWt/lZ
jzpcgFb7TpbFafDowatPRBnY245TQg+HHef4yqdKNFGB6tVp8Eqn/SMZeprC6maZ
HwIDAQAB
-----END PUBLIC KEY-----"""

try:
    print("Testing improved error messages...\n")

    print("1. Testing with PUBLIC KEY (should be accepted)...")
    with open('output/pdf/unsigned_demo.pdf', 'rb') as pdf:
        resp = requests.post(f'{BASE_URL}/verify-external',
            files={'file': pdf},
            data={'publicKey': PUBLIC_KEY})

    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✅ PUBLIC KEY accepted, valid={result.get('valid')}")
    else:
        print(f"   ❌ Unexpected status: {resp.status_code}, detail={resp.text[:120]}")

    print("\n2. Testing with CERTIFICATE on public-key endpoint (should return 400)...")
    cert_resp = requests.post(f'{BASE_URL}/generate-keys')
    cert_resp.raise_for_status()
    cert_value = cert_resp.json()['certificate']

    with open('output/pdf/unsigned_demo.pdf', 'rb') as pdf:
        resp = requests.post(f'{BASE_URL}/verify-external',
            files={'file': pdf},
            data={'publicKey': cert_value})

    if resp.status_code == 400:
        error_msg = resp.json().get('detail', '')
        print(f"   ✅ Correctly rejected certificate: {error_msg[:110]}")
    else:
        print(f"   ❌ Expected 400 for certificate input, got {resp.status_code}")

    print("\n3. Testing with invalid format (non-PEM)...")
    with open('output/pdf/unsigned_demo.pdf', 'rb') as pdf:
        resp = requests.post(f'{BASE_URL}/verify-external',
            files={'file': pdf},
            data={'publicKey': 'not a valid format'})

    if resp.status_code == 400:
        error_msg = resp.json().get('detail', '')
        print(f"   Status: {resp.status_code}")
        print(f"   Error: {error_msg[:100]}\n")
        print("   ✅ Non-PEM format properly rejected")

    print("\n4. Testing with whitespace handling...")
    with open('output/pdf/unsigned_demo.pdf', 'rb') as pdf:
        resp = requests.post(f'{BASE_URL}/verify-external',
            files={'file': pdf},
            data={'publicKey': '  \n' + PUBLIC_KEY + '\n  '})

    if resp.status_code == 200:
        print("   ✅ Whitespace properly stripped before validation")
    else:
        print(f"   ❌ Unexpected status with whitespace: {resp.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ Backend not running. Start with:")
    print("   lsof -ti:8000 | xargs kill -9 2>/dev/null; sleep 1")
    print("   python3 -m uvicorn backend.app:app --port 8000")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All error message tests completed!")
