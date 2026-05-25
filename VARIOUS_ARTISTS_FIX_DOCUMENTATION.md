# Various Artists Special Case - Complete Documentation

## Problem Statement

### Issue

Files downloaded from Tidal (or scraped from Qobuz/Deezer/Apple Music) sometimes have "Various Artists" as the album artist, which causes upload failures.

**Error Message:**
```
"Site upload failed: Please enter at least one main artist (200)"
```

### User's Example

```
Album: Musik GPS
Album/Performer: Various Artists
Track 1: Mwin Le Pi Mwin Minm
Track 1 Performer: Anaëlle Latchimy
```

**Current Behavior:**
- Album artist "Various Artists" is passed to upload manager
- Upload fails because "Various Artists" is not a valid artist name

**Expected Behavior:**
- Use track artist "Anaëlle Latchimy" as album main artist
- Upload succeeds

## Solution

### Overview

Replace "Various Artists" with actual track artists when it's the **only** album artist.

### Implementation

**New Function:** `replace_various_artists_with_track_artists(artists, metadata)`

**Location:** `brucelee94/uploader/__init__.py` lines 791-828

**Logic:**
1. Check if album artists list contains ONLY "Various Artists" (case-insensitive)
2. If yes: Extract all unique track artists with "main" importance
3. Replace "Various Artists" with collected track artists
4. If no: Keep original artist list

**Applied At:**
1. **Line 1045:** After Tidal file-based metadata extraction
2. **Line 698:** After Qobuz/Deezer/Apple scraped + file metadata combination

**NOT Applied To:**
- Beatport (excluded as per user requirement)

### Code

```python
def replace_various_artists_with_track_artists(artists, metadata):
    """
    Replace "Various Artists" with actual track artists when it's the only album artist.
    
    This handles special cases where files from Tidal (or scraped from Qobuz/Deezer/Apple)
    have "Various Artists" as the album artist, which causes upload failures.
    
    Args:
        artists: List of (artist_name, importance) tuples
        metadata: Metadata dict containing tracks information
    
    Returns:
        List of (artist_name, importance) tuples with "Various Artists" replaced if needed
    """
    # Check if "Various Artists" is the only album artist
    if len(artists) == 1 and artists[0][0].lower() == "various artists":
        # Extract all unique track artists (main importance only)
        track_artists = set()
        
        if "tracks" in metadata and metadata["tracks"]:
            for disc_tracks in metadata["tracks"].values():
                for track_info in disc_tracks.values():
                    if "artists" in track_info:
                        for artist_name, importance in track_info["artists"]:
                            if importance == "main":
                                track_artists.add(artist_name)
        
        # Replace "Various Artists" with track artists if we found any
        if track_artists:
            return [(artist, "main") for artist in sorted(track_artists)]
    
    # Keep original artists if:
    # - Not "Various Artists"
    # - "Various Artists" plus other artists (intentional)
    # - No track artists found (fallback)
    return artists
```

## Examples

### Example 1: User's Scenario (Tidal)

**Input:**
```python
artists = [("Various Artists", "main")]
metadata = {
    "tracks": {
        1: {
            1: {"title": "Mwin Le Pi Mwin Minm", "artists": [("Anaëlle Latchimy", "main")]},
        }
    }
}
```

**Output:**
```python
[("Anaëlle Latchimy", "main")]
```

**Result:** ✅ Upload succeeds with actual track artist

### Example 2: Various Artists with Other Artists

**Input:**
```python
artists = [("Various Artists", "main"), ("Compilation Producer", "main")]
```

**Output:**
```python
[("Various Artists", "main"), ("Compilation Producer", "main")]
```

**Result:** ✅ Kept as is (not replaced) - multiple artists means it's intentional

### Example 3: No Various Artists

**Input:**
```python
artists = [("Normal Artist", "main")]
```

**Output:**
```python
[("Normal Artist", "main")]
```

**Result:** ✅ Unchanged - no replacement needed

### Example 4: Multiple Track Artists

**Input:**
```python
artists = [("Various Artists", "main")]
metadata = {
    "tracks": {
        1: {
            1: {"artists": [("Artist A", "main")]},
            2: {"artists": [("Artist B", "main")]},
            3: {"artists": [("Artist A", "main")]},  # Duplicate
        }
    }
}
```

**Output:**
```python
[("Artist A", "main"), ("Artist B", "main")]
```

**Result:** ✅ Unique artists collected and sorted (duplicates removed)

### Example 5: Track with Guest Artists

**Input:**
```python
artists = [("Various Artists", "main")]
metadata = {
    "tracks": {
        1: {
            1: {"artists": [("Main Artist", "main"), ("Guest Artist", "guest")]},
        }
    }
}
```

**Output:**
```python
[("Main Artist", "main")]
```

**Result:** ✅ Only "main" importance artists included (guests excluded)

## Testing

**Test File:** `test_various_artists_fix.py`

**Test Scenarios:**

1. ✅ **Various Artists only** → Replaced with track artists
2. ✅ **Various Artists + other artists** → Kept original
3. ✅ **No Various Artists** → Unchanged
4. ✅ **Multiple unique track artists** → All collected and sorted
5. ✅ **Guest artists present** → Only main importance used

**Test Results:**
```
==================================================
Testing Various Artists Replacement Logic
==================================================

Test 1: Various Artists only (should be replaced)
  ✓ Various Artists replaced with track artists

Test 2: Various Artists with other artists (should NOT be replaced)
  ✓ Kept original (Various Artists + other artists)

Test 3: No Various Artists (should remain unchanged)
  ✓ Unchanged (no Various Artists)

Test 4: Various Artists with multiple unique track artists
  ✓ All unique track artists collected and sorted

Test 5: Various Artists with guest artists (should only use main)
  ✓ Only main importance artists included

==================================================
All tests passed! ✓
==================================================
```

## Benefits

1. ✅ **Upload Success** - No more "Please enter at least one main artist" error
2. ✅ **Accurate Attribution** - Uses actual track artists instead of generic "Various Artists"
3. ✅ **Smart Detection** - Only replaces when "Various Artists" is the ONLY album artist
4. ✅ **Preserves Intent** - Keeps "Various Artists" if other artists are also present
5. ✅ **Source Agnostic** - Works for both file-based and scraped metadata
6. ✅ **Beatport Excluded** - As requested, Beatport logic remains unchanged
7. ✅ **Guest Artist Safe** - Only uses main importance artists (excludes guests)

## Impact

### Fixed

- ✅ Tidal file-based uploads with "Various Artists"
- ✅ Qobuz scraped uploads with "Various Artists"
- ✅ Deezer scraped uploads with "Various Artists"
- ✅ Apple Music scraped uploads with "Various Artists"
- ✅ Upload errors for compilation albums

### Unchanged

- ✅ Beatport uploads (excluded from logic)
- ✅ Albums with multiple artists including "Various Artists"
- ✅ Albums without "Various Artists"
- ✅ DJ Mix handling
- ✅ Guest artist identification
- ✅ Smart artist display logic

## Edge Cases Handled

1. **Various Artists ONLY** → Replace with track artists ✓
2. **Various Artists + others** → Keep original ✓
3. **No Various Artists** → Unchanged ✓
4. **Duplicate track artists** → Deduplicated via set ✓
5. **No track artists found** → Keep Various Artists (fallback) ✓
6. **Guest artists present** → Excluded (only main importance) ✓
7. **Empty tracks metadata** → Keep Various Artists (fallback) ✓

## Integration Points

### Tidal File-Based Metadata

**Location:** `_build_metadata_from_files()` function, line 1045

After metadata is built from file tags, the function is called:
```python
metadata["artists"] = replace_various_artists_with_track_artists(metadata["artists"], metadata)
```

### Scraped Metadata (Qobuz/Deezer/Apple)

**Location:** `edit_metadata()` function, line 698

After artists are extracted/deduplicated, the function is called:
```python
metadata["artists"] = replace_various_artists_with_track_artists(metadata["artists"], metadata)
```

## Files Modified

1. **brucelee94/uploader/__init__.py**
   - Lines 791-828: New function `replace_various_artists_with_track_artists()`
   - Line 1045: Applied to file-based metadata (Tidal)
   - Line 698: Applied to scraped + file metadata (Qobuz/Deezer/Apple)

2. **test_various_artists_fix.py** (new)
   - Comprehensive test suite with 5 scenarios
   - All tests passing

## Related Features

- **Tidal Artist Identification** (commit 00df465) - Correctly identifies main vs guest artists
- **Smart Artist Display** (commit c051225) - Shows/hides per-track artists based on variation
- **Guest Artist Display** (commit 18b4b2f) - Displays guest artists in torrent descriptions

## Future Considerations

1. **User Confirmation** - Could add optional prompt before replacing Various Artists
2. **Threshold** - Could require minimum number of track artists before replacement
3. **Logging** - Could add debug logging to show replacement happened
4. **Configuration** - Could make this feature configurable via settings

## Commit Information

**Commit:** 2877edc
**Date:** 2026-02-20
**Summary:** Handle Various Artists special case - replace with track artists

## Status

✅ **PRODUCTION READY**

- Issue fixed ✓
- All tests passing ✓
- Upload errors resolved ✓
- No regressions ✓
- Documented ✓
