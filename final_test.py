#!/usr/bin/env python3
"""Final comprehensive test of RSA Digital Signature Demo"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_all():
    print("=" * 70)
    print(" FINAL COMPREHENSIVE TEST - RSA Digital Signature Demo System")
    print("=" * 70)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Health check
    try:
        print("\n[1/7] Health Check...")
        resp = requests.get(f'{BASE_URL}/health')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'ok'
        print("✅ Backend is healthy")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
        return

    # Test 2: Generate keys
    try:
        print("\n[2/7] Generate RSA Key Pair (RSA-2048)...")
        resp = requests.post(f'{BASE_URL}/generate-keys')
        assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text}"
        data = resp.json()
        session = data.get('sessionId')
        pubkey = data.get('publicKey')
        privkey = data.get('privateKey')
        cert = data.get('certificate')
        assert session, f"Missing sessionId"
        assert pubkey, f"Missing publicKey"
        assert privkey, f"Missing privateKey"
        assert cert, f"Missing certificate"
        assert '-----BEGIN PUBLIC KEY-----' in pubkey
        assert '-----BEGIN PRIVATE KEY-----' in privkey or '-----BEGIN ENCRYPTED PRIVATE KEY-----' in privkey
        assert '-----BEGIN CERTIFICATE-----' in cert
        print(f"✅ Generated session: {session}")
        print(f"   - Public Key: {len(pubkey)} chars")
        print(f"   - Private Key: {len(privkey)} chars")
        print(f"   - Certificate: {len(cert)} chars")
        tests_passed += 1
    except Exception as e:
        import traceback
        print(f"❌ Failed: {e}")
        traceback.print_exc()
        tests_failed += 1
        return

    # Test 3: Upload PDF
    try:
        print("\n[3/7] Upload PDF and Compute SHA-256...")
        with open('output/pdf/unsigned_demo.pdf', 'rb') as f:
            resp = requests.post(f'{BASE_URL}/upload', files={'file': f})
        assert resp.status_code == 200
        data = resp.json()
        file_id = data['fileId']
        hash_val = data['hash']
        print(f"✅ Uploaded: {data['fileName']}")
        print(f"   - File ID: {file_id}")
        print(f"   - File Size: {data['fileSize']} bytes")
        print(f"   - SHA-256: {hash_val[:32]}...")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
        return

    # Test 4: Sign PDF
    try:
        print("\n[4/7] Sign PDF with Private Key...")
        resp = requests.post(f'{BASE_URL}/sign',
            data={'fileId': file_id, 'sessionId': session})
        assert resp.status_code == 200
        data = resp.json()
        signed_id = data['signedFileId']
        sig_preview = data['signaturePreview']
        print(f"✅ Signed PDF: {data['fileName']}")
        print(f"   - Signed File ID: {signed_id}")
        print(f"   - File Size: {data['fileSize']} bytes")
        print(f"   - Signature (hex): {sig_preview[:48]}...")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
        return

    # Test 5: Download signed PDF
    try:
        print("\n[5/7] Download Signed PDF...")
        resp = requests.get(f'{BASE_URL}/download/{signed_id}')
        assert resp.status_code == 200
        assert len(resp.content) > 1000
        with open('/tmp/test_final_signed.pdf', 'wb') as f:
            f.write(resp.content)
        print(f"✅ Downloaded: {len(resp.content)} bytes")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
        return

    # Test 6: Verify signature (session-based)
    try:
        print("\n[6/7] Verify Signature (Session-based with Public Key)...")
        with open('/tmp/test_final_signed.pdf', 'rb') as f:
            resp = requests.post(f'{BASE_URL}/verify',
                files={'file': f},
                data={'sessionId': session})
        assert resp.status_code == 200
        data = resp.json()
        assert data['valid'] == True
        assert 'VALID SIGNATURE' in data['message']
        print(f"✅ Verification Result: {data['message']}")
        print(f"   - Hash: {data['hash'][:32]}...")
        if data.get('details'):
            d = data['details'][0]
            print(f"   - Signer: {d['signer']}")
            print(f"   - Algorithm: {d['hashAlgorithm'].upper()} with {d['signatureMechanism']}")
            print(f"   - Coverage: {d['coverage']}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1

    # Test 7: Export public key
    try:
        print("\n[7/7] Export Public Key for Sharing...")
        resp = requests.post(f'{BASE_URL}/export-public-key',
            data={'sessionId': session})
        assert resp.status_code == 200
        data = resp.json()
        exported_cert = data['certificate']
        assert '-----BEGIN CERTIFICATE-----' in exported_cert
        print(f"✅ Exported Certificate: {len(exported_cert)} chars")
        print(f"   - Session: {data['sessionId']}")
        print(f"   - Format: PEM (X.509)")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1

    # Summary
    print("\n" + "=" * 70)
    print(f" TEST RESULTS: {tests_passed}/7 Passed | {tests_failed}/7 Failed")
    print("=" * 70)

    if tests_failed == 0:
        print("\n🎉 SUCCESS! All tests passed. System is fully functional.")
        print("\n📋 Summary:")
        print("  ✅ RSA-2048 key generation")
        print("  ✅ PDF upload with SHA-256 hashing")
        print("  ✅ PDF signing with private key")
        print("  ✅ PDF file download")
        print("  ✅ Signature verification with public key")
        print("  ✅ Public key export for sharing")
        print("  ✅ All API endpoints working")
    else:
        print(f"\n⚠️  Some tests failed. Current status: {tests_passed}/7 working")

if __name__ == '__main__':
    test_all()
