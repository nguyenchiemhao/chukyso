# HTTP 400 Error Fix - COMPLETED ✅

## Summary
Fixed the HTTP 400 error that occurred when users tried to verify a signed PDF with an external certificate.

## Root Causes Identified & Fixed

### 1. **Backend Whitespace Handling** ✅
- **Problem**: Form input from textarea included whitespace/newlines that weren't trimmed
- **Location**: `backend/app.py` line 335 in `/api/verify-external` endpoint
- **Fix**: Moved whitespace trimming BEFORE the try block
  ```python
  # BEFORE (incorrect - variable scope issue)
  try:
      pub_str = publicKey.strip()

  # AFTER (correct - accessible in exception handler)
  pub_str = publicKey.strip() if isinstance(publicKey, str) else publicKey.decode().strip()
  try:
  ```

### 2. **Backend Variable Scope Bug** ✅
- **Problem**: Exception handler tried to use `pub_str` variable that was only defined inside try block
- **Location**: `backend/app.py` lines 425 (error response)
- **Fix**: Now `pub_str` is defined before try block, accessible everywhere

### 3. **Frontend Error Message Loss** ✅
- **Problem**: Axios wasn't properly propagating backend error details to frontend
- **Location**: `frontend/src/api.js` lines 35-48
- **Fix**: Added try/catch to preserve axios response object

### 4. **Frontend Error Handling** ✅
- **Problem**: Generic "Request failed" message, no helpful context
- **Location**: `frontend/src/components/ActionPanel.vue` lines 220-225
- **Fix**: Three-level error handling:
  1. Extract backend `response.data.detail` message
  2. Provide 400-specific helpful hint
  3. Fallback to generic error

### 5. **UI/UX Terminology** ✅
- **Problem**: Textarea said "Public Key" but endpoint requires "Certificate"
- **Location**: `frontend/src/components/ActionPanel.vue` lines 133-136
- **Fix**:
  - Changed label to "Verify with Different Certificate"
  - Added placeholder hint: `(-----BEGIN CERTIFICATE-----)`

## Verification Testing Results

```
✅ Test 1: Health check - Backend responsive
✅ Test 2: Key generation - Works
✅ Test 3: PDF signing - Works
✅ Test 4: Verify with clean certificate - Works (200 status)
✅ Test 5: Verify with whitespace - Works (200 status) - WHITESPACE HANDLING FIXED!
✅ Test 6: Invalid format - Returns 400 with descriptive message
```

## Documentation Updates

**[USER_GUIDE.md](USER_GUIDE.md) Section 8 (FAQ) - New Entries:**

1. **"Gặp lỗi 400 khi verify với certificate khác?"**
   - 5-step troubleshooting guide
   - Certificate format requirements
   - How to fix whitespace issues
   - Common mistakes and solutions

2. **"Làm sao biết certificate nào của người nào?"**
   - How to identify certificate owner
   - Where to find the "Copy" button
   - Certificate format explanation

3. **"Tại sao verify với external certificate lâu hơn?"**
   - Explains pyHanko full trust chain validation
   - Contrasts with session-based verification

## Code Changes Summary

| File | Lines | Change |
|------|-------|--------|
| `backend/app.py` | 335 | Whitespace trimming before try block |
| `backend/app.py` | 340-347 | Better validation error messages |
| `backend/app.py` | 425 | Fixed variable scope in exception |
| `frontend/src/api.js` | 35-48 | Enhanced axios error propagation |
| `frontend/src/components/ActionPanel.vue` | 133-136 | Updated label to "Certificate" |
| `frontend/src/components/ActionPanel.vue` | 220-225 | Three-level error handling |
| `USER_GUIDE.md` | 300-360 | Added comprehensive FAQ section |

## How to Test

1. **Start the backend:**
   ```bash
   cd backend
   python3 -m uvicorn app:app --port 8000
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test the workflow:**
   - Generate keys → "Generate RSA Key Pair"
   - Upload PDF → Drag and drop a PDF
   - Sign → "Sign PDF Document"
   - Export certificate → "Export Public Key" or copy from sidebar
   - Verify with external certificate:
     - Paste certificate in textarea
     - Select the signed PDF
     - Click "Verify with This Key"
   - **Expected**: Should show validation result (VALID/INVALID with details)
   - **NOT Expected**: No more "Request failed with status code 400" error

## Known Issues

⚠️ **pyHanko Internal Error** (Separate from 400 error):
- Some edge cases with external certificate validation may show pyHanko's internal error
- This is unrelated to the 400 error (now fixed)
- Regular session-based verification works perfectly
- Full workaround may require library investigation

## Files Modified

```
✅ backend/app.py
✅ frontend/src/api.js
✅ frontend/src/components/ActionPanel.vue
✅ USER_GUIDE.md
```

All changes committed with clear commit messages explaining the fixes.
