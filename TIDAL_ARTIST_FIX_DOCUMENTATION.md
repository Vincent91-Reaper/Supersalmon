# Tidal Artist Identification Fix - Complete Documentation

## Overview

This document describes the fix for Tidal uploads where brucelee94 was incorrectly classifying all track artists as "main" artists, failing to distinguish between main artists and guest artists.

## Problem Statement

### Issue

For Tidal uploads, brucelee94 extracts metadata from the original FLAC files instead of scraping from the provided URL. The previous implementation incorrectly identified main artists and guest artists from the extracted metadata.

**Incorrect Behavior:**
- All track artists were marked as "main"
- No distinction between album-level artists and track-only artists
- Guest artists appeared incorrectly in the main artist list

### User's Example

Track "03. ZigZagueZ" from the album "ORSUJE":

```
General
Complete name                            : D:\Music\Ismail Candide, Eddy Woogy - ORSUJE (2023)\03. ZigZagueZ.flac
Album                                    : ORSUJE
Album/Performer                          : Ismail Candide, Eddy Woogy
Track name                               : ZigZagueZ
Performer                                : Ismail Candide, Eddy Woogy, Christine Ly
```

**Metadata Fields:**
- `Album/Performer` (albumartist): "Ismail Candide, Eddy Woogy"
- `Performer` (artist): "Ismail Candide, Eddy Woogy, Christine Ly"

**Expected Result:**
- **Main artists:** Ismail Candide, Eddy Woogy (appear in both album and track)
- **Guest artist:** Christine Ly (appears only in track, not in album)

**Previous (Incorrect) Result:**
- **Main artists:** Ismail Candide, Eddy Woogy, Christine Ly (all marked as main)
- **Guest artists:** (none)

## Solution

### Correct Logic

Artists should be classified based on their presence at album level vs track level:

1. **Main Artist:** Appears at BOTH album level (`albumartist` field) AND track level (`artist` field)
2. **Guest Artist:** Appears ONLY at track level (`artist` field), NOT at album level

### Algorithm

```
1. Extract album artists from albumartist field
   → Build a set of album-level artists (normalized to lowercase)

2. For each track:
   a. Extract track artists from artist field
   b. For each track artist:
      - If artist.lower() IN album_artists_set → importance = "main"
      - If artist.lower() NOT IN album_artists_set → importance = "guest"

3. Deduplicate artists with priority:
   - If same artist appears as both "guest" and "main" → keep "main"
```

## Implementation

### Code Changes

**File:** `brucelee94/uploader/__init__.py`

**Function:** `_build_metadata_from_files(path, tags, rls_data)`

#### Change 1: Extract Album Artists (First Pass)

**Lines 833-847:**

```python
# First pass: Extract album artists to distinguish main artists from guest artists
# Album artists are artists who appear at the album level (albumartist field)
# Track artists who also appear as album artists are "main" artists
# Track artists who don't appear as album artists are "guest" artists
album_artists_set = set()
for filename, tagset in tags.items():
    if hasattr(tagset, 'albumartist') and tagset.albumartist:
        aa_list = tagset.albumartist if isinstance(tagset.albumartist, list) else [tagset.albumartist]
        for aa in aa_list:
            if aa and aa.strip():
                # Split by comma to handle cases like "Ismail Candide, Eddy Woogy"
                individual_artists = [a.strip() for a in str(aa).split(',') if a.strip()]
                for individual_artist in individual_artists:
                    # Store in lowercase for case-insensitive comparison
                    album_artists_set.add(individual_artist.lower())
```

**Purpose:**
- Extract all album-level artists from the `albumartist` tag
- Handle both single artist and comma-separated multiple artists
- Normalize to lowercase for case-insensitive comparison
- Build a set for efficient lookup

#### Change 2: Classify Track Artists (Second Pass)

**Lines 869-883:**

```python
# Extract artist(s)
track_artists = []
if hasattr(tagset, 'artist') and tagset.artist:
    artist_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
    for artist in artist_list:
        if artist and artist.strip():
            # Split by comma to handle cases like "Gayga, Din" -> ["Gayga", "Din"]
            individual_artists = [a.strip() for a in str(artist).split(',') if a.strip()]
            for individual_artist in individual_artists:
                # Determine if this artist is a main artist or guest artist
                # Main artist: appears at both album level (albumartist) and track level
                # Guest artist: appears only at track level (not in albumartist)
                if individual_artist.lower() in album_artists_set:
                    importance = "main"
                else:
                    importance = "guest"
                
                track_artists.append((individual_artist, importance))
                all_artists.append((individual_artist, importance))
```

**Purpose:**
- For each track artist, check if they appear in album_artists_set
- Assign "main" importance if artist is in album artists
- Assign "guest" importance if artist is NOT in album artists
- Preserve original capitalization while comparing lowercase

#### Change 3: Enhanced Deduplication with Priority

**Lines 1020-1038:**

```python
# Deduplicate and assign artists
# Prioritize "main" importance over "guest" for the same artist
seen_artists = {}  # dict to track artist name (lowercase) -> (original_name, importance)
for artist, importance in all_artists:
    artist_lower = artist.lower()
    if artist_lower not in seen_artists:
        # First time seeing this artist
        seen_artists[artist_lower] = (artist, importance)
    else:
        # Artist already seen - prioritize "main" over "guest"
        existing_name, existing_importance = seen_artists[artist_lower]
        if existing_importance == "guest" and importance == "main":
            # Upgrade guest to main
            seen_artists[artist_lower] = (artist, importance)
        # If existing is "main" and new is "guest", keep existing (main)
        # If both are same importance, keep existing

# Convert dict values to list
unique_artists = list(seen_artists.values())

metadata["artists"] = unique_artists
```

**Purpose:**
- Deduplicate artists while preserving importance
- Handle edge case where same artist appears with different importance in different tracks
- Prioritize "main" over "guest" (upgrade if needed)
- Maintain original capitalization from first occurrence

### Examples

#### Example 1: User's Scenario

**Input:**
- `albumartist`: "Ismail Candide, Eddy Woogy"
- Track 03 `artist`: "Ismail Candide, Eddy Woogy, Christine Ly"

**Processing:**

1. Extract album artists:
   ```
   album_artists_set = {"ismail candide", "eddy woogy"}
   ```

2. Process track artists:
   ```
   "Ismail Candide" → in album_artists_set → importance = "main"
   "Eddy Woogy" → in album_artists_set → importance = "main"
   "Christine Ly" → NOT in album_artists_set → importance = "guest"
   ```

3. Result:
   ```python
   [
       ("Ismail Candide", "main"),
       ("Eddy Woogy", "main"),
       ("Christine Ly", "guest")
   ]
   ```

**Torrent Description:**
```
[b]Track 03.[/b] ZigZagueZ (feat. [artist]Christine Ly[/artist])
```

#### Example 2: All Artists are Main

**Input:**
- `albumartist`: "Artist A, Artist B"
- Track 01 `artist`: "Artist A, Artist B"

**Processing:**

1. album_artists_set = {"artist a", "artist b"}
2. Both track artists are in album_artists_set
3. Result: Both marked as "main"

**Output:**
```python
[("Artist A", "main"), ("Artist B", "main")]
```

#### Example 3: Deduplication Priority

**Input:**
- Track 01 `artist`: "Guest X" (not in albumartist)
- Track 05 `artist`: "Guest X" (but Guest X is now in albumartist)

**Processing:**

1. Track 01: "Guest X" → importance = "guest"
2. Track 05: "Guest X" → importance = "main"
3. Deduplication: Upgrade "guest" to "main"

**Output:**
```python
[("Guest X", "main")]
```

## Testing

### Test Suite

**File:** `test_tidal_artist_fix.py`

#### Test 1: User's Example

Tests the exact scenario from the problem statement.

```python
def test_artist_identification():
    """Test classification with Ismail Candide, Eddy Woogy, Christine Ly"""
```

**Result:** ✓ Pass
- Main: Ismail Candide, Eddy Woogy
- Guest: Christine Ly

#### Test 2: Deduplication Priority

Tests that main importance overrides guest.

```python
def test_artist_deduplication_priority():
    """Test that main is prioritized over guest"""
```

**Result:** ✓ Pass
- Artist B upgraded from guest to main

#### Test 3: Missing albumartist Field

Tests behavior when no albumartist field exists.

```python
def test_no_albumartist_field():
    """Test fallback behavior without albumartist"""
```

**Result:** ✓ Pass
- Gracefully handles missing field

### Running Tests

```bash
cd /home/runner/work/Supersalmon/Supersalmon
python3 test_tidal_artist_fix.py
```

**Expected Output:**
```
============================================================
Testing Tidal Artist Identification Fix
============================================================

Album artists (from albumartist field):
  ['eddy woogy', 'ismail candide']

Track 03 artists classification:
  Ismail Candide: main
  Eddy Woogy: main
  Christine Ly: guest

✓ Test passed! Artists correctly classified.
...
============================================================
All tests passed! ✓
============================================================
```

## Benefits

1. **Correct Attribution:** Guest artists are properly identified and displayed
2. **Metadata-Based:** Uses authoritative `albumartist` field
3. **Case-Insensitive:** Handles variations in capitalization
4. **Edge Cases:** Handles missing fields and duplicates
5. **Non-Breaking:** Only affects Tidal uploads, other sources unchanged
6. **DJ Mix Safe:** Does not interfere with existing DJ Mix logic

## Impact

### What Changed

**Tidal Uploads:**
- ✅ Guest artists now correctly identified
- ✅ Appear in torrent description as "(feat. [artist]Name[/artist])"
- ✅ Not listed in main artist line

### What Stayed the Same

**Other Sources:**
- ✅ iTunes, Qobuz, Deezer, Beatport (use scraped metadata)
- ✅ DJ Mix handling (has separate logic at lines 1105-1155)
- ✅ Non-Tidal file-based extraction logic

## Edge Cases Handled

### 1. Missing albumartist Field

**Scenario:** File has `artist` but no `albumartist`

**Behavior:**
- album_artists_set is empty
- All track artists marked as "guest"
- Downstream logic may promote them to main

### 2. Artist in Some Tracks Only

**Scenario:** Artist appears in track 1 but not track 2

**Behavior:**
- Artist is only added once (deduplication)
- Importance from first occurrence preserved

### 3. Same Artist, Different Cases

**Scenario:** "Eddy Woogy" vs "eddy woogy"

**Behavior:**
- Comparison is case-insensitive
- Original capitalization preserved

### 4. Comma-Separated Artists

**Scenario:** "Artist A, Artist B"

**Behavior:**
- Properly split into individual artists
- Each classified separately

### 5. Priority Conflict

**Scenario:** Same artist is guest in one track, main in another

**Behavior:**
- Deduplication upgrades to "main"
- "main" takes priority over "guest"

## Future Considerations

### Potential Enhancements

1. **Support for ampersand separator:** Currently only handles comma
2. **Album-specific guest artists:** Artists who guest on entire album
3. **Explicit guest tags:** Some files have separate guest artist field
4. **Remixer handling:** Distinguish remixers from guests

### Related Features

- **Guest artist display:** Shows in torrent description as "(feat. ...)"
- **Smart artist display:** Shows/hides per-track artists based on variation
- **DJ Mix handling:** Special logic for DJ compilations
- **Inline BBCode:** Adds [artist] tags to existing (feat. ...) in titles

## Files Modified

1. **brucelee94/uploader/__init__.py**
   - Function: `_build_metadata_from_files()`
   - Lines: 833-847 (album artist extraction)
   - Lines: 869-883 (track artist classification)
   - Lines: 1020-1038 (deduplication with priority)

2. **test_tidal_artist_fix.py** (new)
   - Comprehensive test suite
   - 3 test scenarios
   - All tests passing

## Commit Information

**Commit Hash:** 00df465

**Commit Message:**
```
Fix Tidal artist identification - correctly distinguish main vs guest artists

Fixed issue where Tidal uploads incorrectly classified all track artists as main artists.
```

**Files Changed:**
- `brucelee94/uploader/__init__.py` (+30, -7)
- `test_tidal_artist_fix.py` (+194, new file)

## Conclusion

This fix ensures that Tidal uploads properly classify artists as main or guest based on their presence at the album level. Guest artists now appear correctly in torrent descriptions, improving accuracy and user experience.

The implementation is robust, handles edge cases, and does not affect other upload sources or existing features like DJ Mix handling.
