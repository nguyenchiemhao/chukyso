# PUBLIC KEY vs CERTIFICATE - Clarification & Fix

## The Problem You Encountered

**Error message:**
```
Invalid certificate format: Valid PEM but no BEGIN CERTIFICATE/END CERTIFICATE delimiters.
Are you sure this is a certificate?
```

**The Issue:** You pasted a **PUBLIC KEY** instead of a **CERTIFICATE**.

---

## PUBLIC KEY vs CERTIFICATE — What's the Difference?

When you generate RSA keys, you actually get **TWO DIFFERENT formats**:

| Aspect | PUBLIC KEY | CERTIFICATE (X.509) |
|--------|-----------|-----------------|
| **Starts with** | `-----BEGIN PUBLIC KEY-----` | `-----BEGIN CERTIFICATE-----` |
| **Ends with** | `-----END PUBLIC KEY-----` | `-----END CERTIFICATE-----` |
| **Contains** | Just the key material | Key + metadata (subject, issuer, validity dates, serial number) |
| **Use case** | Encryption/Decryption | Digital signatures & verification |
| **Trust info** | None | Has issuer/validity information |

### Visual Example:

```
PUBLIC KEY (❌ doesn't work for verification):
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ...
... (just key bytes)
-----END PUBLIC KEY-----

CERTIFICATE (✅ works for verification):
-----BEGIN CERTIFICATE-----
MIIDHTCCAgWgAwIBAgIUJ924okIf+...
... (key + metadata + signature)
-----END CERTIFICATE-----
```

---

## How to Get the RIGHT Format

### ✅ Correct Way: Use "Export Public Key" Button

1. In the left panel under "Verify Signature"
2. Click the button labeled **"Export Public Key"**
3. This will give you the full **X.509 CERTIFICATE** (wrapped with `-----BEGIN CERTIFICATE-----`)
4. Paste this into the "Verify with Different Certificate" textarea

### ❌ Wrong Way: Using "Copy" Button for Just the Key

- Clicking "Copy" in the Public Key section gives you the raw public key
- This starts with `-----BEGIN PUBLIC KEY-----`
- **This won't work for verification** — it will fail with error 400

---

## What We Fixed

### Backend Improvements (`backend/app.py`)

Added a **proactive check** that detects when user pastes a PUBLIC KEY instead of CERTIFICATE:

```python
# NEW CODE - Checks for common mistakes
if b'-----BEGIN PUBLIC KEY-----' in pub_pem_bytes or b'-----BEGIN RSA PRIVATE KEY-----' in pub_pem_bytes:
    raise HTTPException(
        status_code=400,
        detail="This is a PUBLIC KEY, not a CERTIFICATE. You need to use the 'Export Public Key' button to get the certificate..."
    )
```

**Result**: Instead of a cryptic "Valid PEM but no BEGIN CERTIFICATE" error, you now get a **clear, actionable message** explaining the difference.

### Frontend Improvements (ActionPanel.vue)

Updated the textarea placeholder to explicitly warn about this:

```
"Paste person's CERTIFICATE with -----BEGIN CERTIFICATE----- (NOT -----BEGIN PUBLIC KEY-----).
Use 'Export Public Key' button to get the full certificate."
```

### Documentation Updates (USER_GUIDE.md)

Added a comprehensive FAQ entry explaining:
- The difference between PUBLIC KEY and CERTIFICATE
- How to get the correct format
- Why Certificate is needed for verification
- How to fix if you have the wrong format

---

## Testing Results ✅

All error cases tested and working:

```
✅ Test 1: PUBLIC KEY input → Clear error message about PUBLIC KEY vs CERTIFICATE
✅ Test 2: Invalid format → Proper PEM format validation
✅ Test 3: Whitespace → Properly trimmed before validation
```

---

## What You Should Do Now

### If You Were Pasting a PUBLIC KEY:

1. **Find the "Export Public Key" button** in the left panel (under Verify Signature section)
2. **Click it** to get the full CERTIFICATE
3. **Paste the certificate** into "Verify with Different Certificate"
4. **Try again** — should now work

### If You're Sharing with Others:

- Tell them: "Use the 'Export Public Key' button, not the 'Copy' button"
- Or share the exported certificate text directly (the one starting with `-----BEGIN CERTIFICATE-----`)

---

## Files Changed

| File | What | Why |
|------|------|-----|
| `backend/app.py` | Added PUBLIC KEY detection check | Give users the right error message |
| `frontend/src/components/ActionPanel.vue` | Updated textarea placeholder | Warn before they paste |
| `USER_GUIDE.md` | Added FAQ entry explaining the difference | Help users troubleshoot |

---

## Key Takeaway

- **Public Key** = Just the key material (`-----BEGIN PUBLIC KEY-----`)
- **Certificate** = Key wrapped in X.509 format with metadata (`-----BEGIN CERTIFICATE-----`)
- **For verification**: Always use **CERTIFICATE**, never just the public key
- **How to get it**: Use the **"Export Public Key"** button to export the full certificate
