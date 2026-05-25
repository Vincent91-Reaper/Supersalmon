# Track Artist Label Removal Fix - Quick Summary

## Problem

User reported that record labels (e.g., "Former City Records") were successfully removed from album artist tags, but still remained in track artist tags ("Performer" field).

**Status:**
- ✅ Album artist: Label removed correctly
- ❌ Track artist: Label still present

## Root Cause

Previous code only handled simple cases:
- Exact matches in lists
- Label as complete substring

But didn't handle:
- **Comma-separated strings** like "Artist1, Former City Records, Artist2"
- **Nested comma-separated values** in lists
- **Label at different positions** (start, middle, end)

## Solution

Enhanced the track artist cleaning logic to:
1. **Split comma-separated strings** into individual parts
2. **Filter out the label** from each part
3. **Rebuild clean artist values** (list or string)
4. **Handle nested structures** (comma-separated values within lists)

## Examples Fixed

### Example 1: Simple Comma-Separated
```
Before: "Swoze, Former City Records"
After:  "Swoze"
```

### Example 2: Label in Middle
```
Before: "Gary Gritness, Former City Records, Swoze"
After:  "Gary Gritness, Swoze"
```

### Example 3: Label at End
```
Before: "Artist, Former City Records"
After:  "Artist"
```

### Example 4: List with Nested Commas
```
Before: ["Artist1, Former City Records", "Artist2"]
After:  ["Artist1", "Artist2"]
```

### Example 5: List with Exact Match
```
Before: ["Gary Gritness", "Former City Records", "Swoze"]
After:  ["Gary Gritness", "Swoze"]
```

## How to Test

### 1. Update brucelee94
```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

### 2. Run Upload
```bash
bl94 up "/path/to/album" -su "https://tidal.com/album/467066754"
```

### 3. Expected Console Output
```
Detected label in album artist: Swoze, Former City Records
Removing label 'Former City Records' from album artist and track artists...
Cleaned album artist: Swoze
  Cleaned track artist in 01 - Track1.flac
  Cleaned track artist in 02 - Track2.flac
  Cleaned track artist in 03 - Track3.flac
Label set in metadata: Former City Records
Album artist and track artists cleaned successfully.
```

## Verification

### Check Track Artist Tags
```bash
# For FLAC files
metaflac --show-tag=ARTIST file.flac

# For MP3 files
id3v2 -l file.mp3 | grep TPE1
```

**Expected:** Track artist should NOT contain "Former City Records"

### Check Album Artist Tags
```bash
# For FLAC files
metaflac --show-tag=ALBUMARTIST file.flac

# For MP3 files
id3v2 -l file.mp3 | grep TPE2
```

**Expected:** Album artist should NOT contain "Former City Records"

### Check Metadata
- Label field: Should show "Former City Records" (preserved for upload)
- Artists: Should NOT include "Former City Records"

## Summary

✅ **Issue:** Track artist still had label
✅ **Fix:** Enhanced comma-splitting and list handling
✅ **Result:** Label removed from all track artist formats
✅ **Status:** Ready for testing

The track artist cleaning now properly removes labels from all tag formats, including comma-separated strings and complex list structures!
