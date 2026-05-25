# Deezer BARCODE Extraction

## Problem

Deezer files don't have a `UPC` tag in their metadata. Instead, they use a `BARCODE` tag which serves the same purpose - it's the Universal Product Code for the release.

According to the requirement:
> BARCODE = UPC = Catalogue number

This means the BARCODE from Deezer files should be:
1. Extracted from file tags
2. Used as the UPC value
3. Used as the Catalogue number on RED torrent pages

## Solution

The code now automatically extracts the BARCODE from Deezer files and uses it as both the UPC and catalogue number.

## Technical Implementation

### 1. Function Signature Update

**File:** `brucelee94/uploader/__init__.py` (line 840)

```python
def _build_metadata_from_files(path, tags, rls_data, is_deezer=False):
    """
    Build metadata structure from file tags for Tidal and Deezer URLs.
    
    Args:
        path: Path to the album folder
        tags: Dictionary of file tags
        rls_data: Release data dictionary
        is_deezer: Boolean indicating if this is a Deezer upload (for BARCODE handling)
    """
```

The function now accepts an `is_deezer` parameter to enable special BARCODE handling.

### 2. BARCODE Extraction Logic

**File:** `brucelee94/uploader/__init__.py` (lines 1055-1063)

```python
# Extract UPC/Barcode (try both 'upc' and 'barcode' fields)
if hasattr(tagset, 'upc') and tagset.upc:
    upcs.append(str(tagset.upc))
elif hasattr(tagset, 'barcode') and tagset.barcode:
    barcode_value = str(tagset.barcode)
    upcs.append(barcode_value)
    # For Deezer files, BARCODE = UPC = Catalogue number
    # Add to catnos so it's used as the catalogue number
    if is_deezer:
        catnos.append(barcode_value)
```

**Key points:**
- First tries to find `upc` tag
- If not found, looks for `barcode` tag
- If this is a Deezer upload (`is_deezer=True`), adds BARCODE to both:
  - `upcs` list → becomes `metadata["upc"]`
  - `catnos` list → becomes `metadata["catno"]`

### 3. Flag Passing

**File:** `brucelee94/uploader/__init__.py` (line 367)

```python
# Build metadata from file tags (pass is_deezer for BARCODE handling)
metadata = _build_metadata_from_files(path, tags, rls_data, is_deezer=is_deezer)
```

The `is_deezer` flag is passed from the upload workflow where Deezer URLs are detected.

## How It Works

### Complete Flow

1. **Deezer URL Detection**
   - User provides Deezer URL: `https://www.deezer.com/en/album/852049722`
   - System sets `is_deezer=True`

2. **Metadata Extraction**
   - Skip web scraping
   - Extract metadata from downloaded file tags
   - Read each audio file's metadata

3. **BARCODE Processing**
   - Find BARCODE tag in file (e.g., `BARCODE: 3491549876543`)
   - Add to `upcs` list (for UPC field)
   - Add to `catnos` list (for catalogue number field)

4. **Metadata Assignment**
   ```python
   if catnos:
       metadata["catno"] = max(set(catnos), key=catnos.count)
   
   if upcs:
       metadata["upc"] = max(set(upcs), key=upcs.count)
   ```

5. **Upload to RED**
   - `generate_catno(metadata)` uses `metadata["catno"]`
   - Catalogue Number field on RED is populated with BARCODE value

## Before vs After

### Before

**Deezer file tags:**
```
TITLE: Love Story
ARTIST: Taylor Swift
BARCODE: 3491549876543
```

**RED torrent page:**
```
Catalogue Number: [empty or manually entered]
```

### After

**Deezer file tags:**
```
TITLE: Love Story
ARTIST: Taylor Swift
BARCODE: 3491549876543
```

**Extracted metadata:**
```python
metadata["upc"] = "3491549876543"
metadata["catno"] = "3491549876543"
```

**RED torrent page:**
```
Catalogue Number: 3491549876543
```

## Testing

### 1. Check File Has BARCODE

```bash
# Using ffprobe
ffprobe -hide_banner file.flac 2>&1 | grep -i barcode
# Output: BARCODE: 3491549876543

# Using exiftool
exiftool file.flac | grep -i barcode
# Output: Barcode: 3491549876543
```

### 2. Upload with Deezer URL

```bash
bl94 up /path/to/deezer/album \
  -s Deezer \
  -su "https://www.deezer.com/en/album/852049722"
```

### 3. Verify Extraction

During upload, you should see:
```
Extracting metadata from file tags...
[metadata extraction happens]
```

Check the console output or logs to see if BARCODE was extracted.

### 4. Verify on RED

After upload completes:
1. Go to the torrent page on RED
2. Check the "Catalogue Number" field
3. It should contain the BARCODE value from your files

## Understanding BARCODE, UPC, and Catalogue Number

### BARCODE
- **What it is:** A tag field in Deezer audio files
- **Format:** Usually 13 digits (EAN-13 format)
- **Example:** `3491549876543`
- **Purpose:** Identifies the release uniquely

### UPC
- **What it is:** Universal Product Code
- **Same as:** BARCODE (they're equivalent)
- **Usage:** Industry-standard identifier
- **On RED:** Can be used for searching/matching

### Catalogue Number
- **What it is:** Label's catalog number for the release
- **For Deezer:** Same value as BARCODE/UPC
- **On RED:** Displayed on torrent page
- **Usage:** Helps organize and find releases

### Why All Three?

For Deezer uploads:
```
BARCODE (file tag) = UPC (metadata field) = Catalogue Number (RED field)
```

They're all the same identifier, just used in different contexts:
- **BARCODE:** How it's stored in Deezer files
- **UPC:** How it's represented in metadata
- **Catalogue Number:** How it appears on RED

## Benefits

✅ **Automatic** - No manual entry needed
✅ **Accurate** - Uses actual value from files
✅ **Complete** - Both UPC and catno fields populated
✅ **RED compliant** - Proper metadata for the site
✅ **Searchable** - Easier to find and match releases

## Related Features

This feature works with the broader Deezer upload improvements:
- Metadata extraction from files (not web scraping)
- Genre tag preservation
- Artist classification
- Label extraction

See `DEEZER_UPLOAD_GUIDE.md` for the complete Deezer upload workflow.
