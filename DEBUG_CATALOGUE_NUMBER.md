# Debugging Catalogue Number Issue for Deezer Uploads

## Problem

User reports that the catalogue number field is still empty for Deezer uploads, even after implementing BARCODE extraction.

## Debug Output Added

We've added comprehensive debug logging to the post-upload update section to help diagnose where the issue is occurring.

### Location

File: `brucelee94/uploader/__init__.py` (around line 546)

### Debug Messages

The following debug messages will appear during upload:

```
[DEBUG] Label to add: '...'
[DEBUG] Catalog to add: '...'
[DEBUG] metadata['catno']: '...'
[DEBUG] metadata['upc']: '...'
```

These messages show:
- **Label to add**: The label that will be sent to RED
- **Catalog to add**: The catalogue number that will be sent to RED (from `generate_catno()`)
- **metadata['catno']**: The catno value stored in metadata (from BARCODE extraction)
- **metadata['upc']**: The UPC value stored in metadata (from BARCODE extraction)

## Testing Instructions

### Step 1: Run a Deezer Upload

```bash
bl94 up /path/to/deezer/album -s Deezer -su "https://www.deezer.com/album/852049722"
```

### Step 2: Watch for Debug Output

Look for the yellow `[DEBUG]` messages in the output. They appear after the torrent is uploaded, during the post-upload update phase.

### Step 3: Check RED Torrent Page

After upload completes, check the torrent page on RED to see if the Catalogue Number field is filled.

## Expected Output Scenarios

### Scenario 1: Working Correctly

```
[DEBUG] Label to add: 'Republic Records'
[DEBUG] Catalog to add: '3491549876543'
[DEBUG] metadata['catno']: '3491549876543'
[DEBUG] metadata['upc']: '3491549876543'
Adding label and catalog to torrent...
  Label: Republic Records
  Catalog: 3491549876543
Label and catalog added successfully!
```

**What this means:**
- ✅ BARCODE extracted correctly (both catno and upc are set)
- ✅ generate_catno() returned the catalogue number
- ✅ Post-upload update triggered
- ✅ API call succeeded

**Expected result:** Catalogue number should appear on RED

---

### Scenario 2: BARCODE Not Extracted

```
[DEBUG] Label to add: ''
[DEBUG] Catalog to add: ''
[DEBUG] metadata['catno']: 'NOT SET'
[DEBUG] metadata['upc']: 'NOT SET'
[DEBUG] Skipping label/catalog update - both empty
```

**What this means:**
- ❌ BARCODE was not extracted from files
- ❌ metadata['catno'] was never set
- ❌ Post-upload update was skipped

**Root cause:** BARCODE extraction logic not working

**Next step:** Verify file has BARCODE tag:
```bash
ffprobe file.flac 2>&1 | grep -i barcode
```

---

### Scenario 3: catno Not Being Used

```
[DEBUG] Label to add: ''
[DEBUG] Catalog to add: ''
[DEBUG] metadata['catno']: '3491549876543'
[DEBUG] metadata['upc']: '3491549876543'
[DEBUG] Skipping label/catalog update - both empty
```

**What this means:**
- ✅ BARCODE extracted correctly (catno and upc are set)
- ❌ generate_catno() returned empty string
- ❌ Post-upload update was skipped

**Root cause:** `generate_catno()` logic issue or config problem

**Next step:** Check if `cfg.upload.compression.use_upc_as_catno` is set, or verify generate_catno() logic

---

### Scenario 4: Update Failing Silently

```
[DEBUG] Label to add: ''
[DEBUG] Catalog to add: '3491549876543'
[DEBUG] metadata['catno']: '3491549876543'
[DEBUG] metadata['upc']: '3491549876543'
Adding label and catalog to torrent...
  Label: 
  Catalog: 3491549876543
[no success message appears]
```

**What this means:**
- ✅ BARCODE extracted correctly
- ✅ generate_catno() worked
- ✅ Post-upload update triggered
- ❌ API call might have failed

**Root cause:** Issue in `update_torrent_metadata()` or API

**Next step:** Check for error messages, verify API response

---

## What to Report

Please provide:

1. **Complete debug output** - Copy all the `[DEBUG]` messages
2. **Whether catalogue number appears on RED** - Yes or No
3. **Screenshot of RED torrent page** - Showing the catalogue number field
4. **File BARCODE verification** - Output of:
   ```bash
   ffprobe file.flac 2>&1 | grep -i barcode
   ```

## Interpretation Guide

### If catno is NOT SET

This means BARCODE was never extracted from the files. Possible reasons:
- File doesn't have BARCODE tag
- BARCODE extraction logic has a bug
- is_deezer flag not being passed correctly

### If catno is SET but catalog_to_add is empty

This means `generate_catno()` is not returning the catno value. Check:
- Is there a config setting blocking it?
- Is the logic in generate_catno() correct?

### If catalog_to_add is SET but no success message

The API call might be failing. Check:
- Are there any error messages?
- Is the field name correct in the API?
- Is the authentication working?

## Field Names

The user mentioned "The catalogue number field is not named 'RemasterCatalogueNumber' on RED". 

Our investigation shows:
- RED API uses `remasterCatalogueNumber` (camelCase) when reading
- RED API uses `remaster_catalogue_number` (snake_case) when posting
- The code uses the correct field names for both operations

## Summary

This debug output will help us identify exactly where the catalogue number is getting lost:
1. During extraction from files
2. During storage in metadata
3. During generate_catno() call
4. During API update

Once we see your debug output, we can implement a targeted fix!
