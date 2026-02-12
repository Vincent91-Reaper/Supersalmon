# DJ Mix Upload Debugging Guide

## Problem

User reports that despite previous fixes, DJ Mix releases are still:
1. Being uploaded as "Remix" instead of "DJ Mix"
2. Not showing album artist as "DJ/Compiler"
3. Not including track artists from individual files

## Debugging Added

Comprehensive debug output has been added throughout the DJ Mix handling pipeline to identify where the process fails.

### Expected Debug Output Flow

For a properly working DJ Mix upload (e.g., "Dillon Francis at EDC Las Vegas, 2024: Cosmic Meadow Stage (DJ Mix)"), you should see:

```
# 1. iTunes Scraper Detection
Release type: DJ Mix

# 2. Artist Handling (in edit_metadata)
DEBUG: Checking DJ Mix - rls_type: DJ Mix, title: Dillon Francis at EDC Las Vegas, 2024: Cosmic Meadow Stage (DJ Mix)
DEBUG: DJ Mix release type detected, processing artist roles...
DEBUG: Album artists (from albumartist tag): ['Dillon Francis']
DEBUG: Artists from metadata: [('Dillon Francis', 'main')]
DEBUG: Track artists (excluding album artists): ['Artist 1', 'Artist 2', 'Artist 3', ...]
Detected DJ Mix release. DJ/Compiler: Dillon Francis
DEBUG: Final artist list: [('Dillon Francis', 'djcompiler'), ('Artist 1', 'main'), ('Artist 2', 'main'), ...]

# 3. Upload Preparation
DEBUG: Release type before upload: DJ Mix
DEBUG: Title: Dillon Francis at EDC Las Vegas, 2024: Cosmic Meadow Stage (DJ Mix)
DEBUG: Artists: [('Dillon Francis', 'djcompiler'), ('Artist 1', 'main'), ...]
```

## Troubleshooting Based on Output

### Issue 1: Release Type Not "DJ Mix"

**Symptom:** Debug shows `rls_type: Album` or `rls_type: Remix` instead of `DJ Mix`

**Possible Causes:**
- iTunes scraper not detecting "DJ Mix" in title
- Release type being overwritten somewhere in the pipeline
- Pattern `r"DJ[\s\-]*Mix"` not matching the title format

**Solution:** Check iTunes scraper output first. The pattern should match "DJ Mix", "DJMix", "DJ-Mix", etc.

### Issue 2: No Album Artist Found

**Symptom:** `DEBUG: Album artists (from albumartist tag): []` is empty

**Possible Causes:**
- Files don't have the `albumartist` tag set
- Tag name is different (e.g., "ALBUM ARTIST" vs "albumartist")
- File format doesn't support albumartist tag

**Solution:** Ensure files have the albumartist tag set before uploading. The albumartist should be the DJ/mixer (e.g., "Dillon Francis").

### Issue 3: No Track Artists

**Symptom:** `DEBUG: Track artists (excluding album artists): []` is empty

**Possible Causes:**
- Track files don't have individual artist tags
- All track artists are the same as album artist
- Track metadata not being extracted from files

**Solution:** Ensure individual track files have artist tags set to the performing artists, not the DJ/compiler.

### Issue 4: KeyError Warning

**Symptom:** `WARNING: Release type 'DJ Mix' not found in tracker release types`

**Possible Causes:**
- RELEASE_TYPES constant doesn't include "DJ Mix" key
- Typo in the key name (e.g., "DJ-Mix" vs "DJ Mix")
- Tracker class not using RELEASE_TYPES from constants

**Solution:** Verify that `brucelee94/constants.py` has `"DJ Mix": 19` in RELEASE_TYPES.

## Testing Instructions

1. **Prepare a DJ Mix release:**
   - Download a DJ Mix from Apple Music (e.g., the Dillon Francis example)
   - Ensure files have:
     - `albumartist` tag = DJ name (e.g., "Dillon Francis")
     - Individual track `artist` tags = performing artists

2. **Run brucelee94:**
   ```bash
   brucelee94 upload /path/to/dj-mix-folder
   ```

3. **Capture debug output:**
   - Look for all "DEBUG:" and "WARNING:" messages
   - Note which debug messages appear and which don't

4. **Identify the issue:**
   - If release type is wrong: Check iTunes scraper
   - If no album artists: Check albumartist tags in files
   - If no track artists: Check individual track artist tags
   - If KeyError: Check RELEASE_TYPES constant

5. **Report findings:**
   - Provide the captured debug output
   - Mention at which stage the process deviates from expected output

## File Structure Example

For proper DJ Mix handling, your files should be structured like:

```
Dillon Francis - Dillon Francis at EDC Las Vegas, 2024: Cosmic Meadow Stage (DJ Mix)/
  ├── 01. Track 1.flac
  │   └── Tags:
  │       ├── albumartist: Dillon Francis
  │       └── artist: Martin Garrix
  ├── 02. Track 2.flac
  │   └── Tags:
  │       ├── albumartist: Dillon Francis
  │       └── artist: Tiësto
  ├── 03. Track 3.flac
  │   └── Tags:
  │       ├── albumartist: Dillon Francis
  │       └── artist: Armin van Buuren
  ...
```

## Expected RED Upload Result

After proper DJ Mix handling:

**Release Type:** DJ Mix (not Remix)

**Artists:**
- Dillon Francis (DJ/Compiler) - importance 6
- Martin Garrix (main) - importance 1
- Tiësto (main) - importance 1
- Armin van Buuren (main) - importance 1
- [... all other track artists as main]

## Code Locations

Debug output is generated in:
1. `brucelee94/uploader/__init__.py` lines 708-763 (scraped metadata)
2. `brucelee94/uploader/__init__.py` lines 1092-1139 (file-based metadata)
3. `brucelee94/uploader/upload.py` lines 120-135 (upload preparation)

## Next Steps After Diagnosis

Once the debug output identifies the issue:
1. Apply targeted fix to the specific failure point
2. Test with the same DJ Mix release
3. Verify correct upload to RED
4. Remove debug output once confirmed working
