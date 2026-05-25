# Smart Artist Display for Multi-Artist Albums

## Overview

Implemented smart logic to decide when to show per-track artists in torrent descriptions for albums with multiple main artists.

**DJ Mix uploads are excluded** - they always show per-track artists (unchanged behavior).

## Problem Statement

### Case 1: All Main Artists on All Tracks
**Issue:** If an album has artists A, B, and C as main artists, and all three appear on every track, showing their names on each track line is redundant.

**Solution:** Don't show per-track artists - they're already in the header.

### Case 2: Varying Artists Per Track
**Issue:** If an album has artists A, B, and C, but A only appears on track 1, B on track 2, and C on track 3, users need to know who's on each track.

**Solution:** Show per-track artists - needed for clarity.

## Implementation

### New Function: `all_tracks_have_same_artists()`

Located in `brucelee94/uploader/upload.py` (lines 257-290)

```python
def all_tracks_have_same_artists(tracks, main_artists):
    """
    Check if all tracks have the same artist set as the album's main artists.
    Returns True only if every track has exactly the same artists.
    
    Used to determine if per-track artists should be shown:
    - If all tracks have same artists → Don't show (redundant)
    - If tracks have different artists → Show (needed for clarity)
    """
```

**How it works:**
1. Normalizes artist names (lowercase, strip whitespace)
2. For each track, extracts artists from file tags
3. Splits on ", " and " & " separators
4. Compares track artist set with album main artist set
5. Returns False if ANY track differs from main artists
6. Returns True only if ALL tracks have identical artists

### Smart Logic Integration

Located in `brucelee94/uploader/upload.py` (lines 415-423)

```python
# Smart artist display logic for non-DJ Mix albums
# DJ Mix always shows per-track artists (excluded from this logic)
# For non-DJ Mix: Check if all tracks have the same artists
show_track_artists = False
if not is_dj_mix and len(main_artists) >= 2:
    # Check if all tracks have same artist set as album main artists
    tracks_have_same_artists = all_tracks_have_same_artists(list(track_data.values()), main_artists)
    # Show per-track artists only if they vary across tracks
    show_track_artists = not tracks_have_same_artists
```

**Applied to:**
- Multi-disc track listing (line 510)
- Single-disc track listing (line 577)

**Changed from:**
```python
if is_various_artists and track_metadata:
```

**Changed to:**
```python
if show_track_artists and track_metadata:
```

## Examples

### Case 1: All Artists on All Tracks

**Album:** A, B & C - Album Title
**Tracks:**
- Track 1: A, B & C
- Track 2: A, B & C  
- Track 3: A, B & C

**Description:**
```
[b][artist]A[/artist], [artist]B[/artist] & [artist]C[/artist] - Album Title[/b]
January 01, 2025

[b]01.[/b] Love
[b]02.[/b] Hate
[b]03.[/b] Jealousy
```

**Reasoning:** All artists are in header, no need to repeat on each track.

### Case 2: Different Artists Per Track

**Album:** A, B & C - Album Title
**Tracks:**
- Track 1: A (+ maybe guest)
- Track 2: B
- Track 3: C

**Description:**
```
[b][artist]A[/artist], [artist]B[/artist] & [artist]C[/artist] - Album Title[/b]
January 01, 2025

[b]01.[/b] [artist]A[/artist] - Love (feat. [artist]Guest[/artist])
[b]02.[/b] [artist]B[/artist] - Hate
[b]03.[/b] [artist]C[/artist] - Jealousy
```

**Reasoning:** Artists vary per track, need to show who's on each.

### DJ Mix: Always Shows Track Artists

**Album:** Dubfire & Richie Hawtin - Boiler Room

**Description:**
```
[b][artist]Dubfire[/artist] & [artist]Richie Hawtin[/artist] - Boiler Room[/b]
May 03, 2016

[b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]
[b]02.[/b] [artist]Different Artist[/artist] - Track Two (Mixed) [i](04:12)[/i]
```

**Reasoning:** DJ Mix is excluded from smart logic - always shows track artists from file tags.

## Decision Logic

```
┌─────────────────────────────────┐
│   Check if DJ Mix?              │
└────────┬────────────────────────┘
         │
    ┌────▼────┐
    │   Yes   │
    └────┬────┘
         │
         ├─> Always show per-track artists (file-based)
         │   DJ Mix excluded from smart logic
         │
    ┌────▼────┐
    │   No    │
    └────┬────┘
         │
    ┌────▼──────────────────────────┐
    │ Album has 2+ main artists?    │
    └────┬──────────────────────────┘
         │
    ┌────▼────┐
    │   No    │  (1 main artist)
    └────┬────┘
         │
         ├─> Don't show per-track artists
         │   (single artist, all tracks same)
         │
    ┌────▼────┐
    │   Yes   │  (2+ main artists)
    └────┬────┘
         │
    ┌────▼──────────────────────────────────┐
    │ All tracks have same artist set?      │
    │ (Call all_tracks_have_same_artists()) │
    └────┬──────────────────────────────────┘
         │
    ┌────▼────┐
    │   Yes   │  (Case 1)
    └────┬────┘
         │
         ├─> Don't show per-track artists
         │   (redundant - all in header)
         │
    ┌────▼────┐
    │   No    │  (Case 2)
    └────┬────┘
         │
         └─> Show per-track artists
             (vary across tracks - needed)
```

## Benefits

1. **Cleaner Descriptions (Case 1)**
   - No redundant artist names repeated on every track
   - More readable, less cluttered

2. **Clear Attribution (Case 2)**
   - Shows which artist(s) are on each track
   - Essential when artists vary

3. **DJ Mix Preserved**
   - No changes to DJ Mix behavior
   - Always shows actual track artists

4. **Smart Detection**
   - Automatic based on actual track data
   - No manual configuration needed

5. **Guest Artist Support**
   - Still works with guest/featured artist feature
   - Shows guests in (feat. ...) format when relevant

## Technical Details

### Artist Comparison

**Normalization:**
- Converts to lowercase for case-insensitive comparison
- Strips whitespace from both ends
- Handles variations like "A, B & C" vs "a, b & c"

**Splitting:**
- Splits on ", " first (comma-space)
- Then splits each part on " & " (ampersand)
- Example: "Alix Perez, Shades & Eprom" → ["Alix Perez", "Shades", "Eprom"]

**Comparison:**
- Uses set comparison (order doesn't matter)
- Exact match required (all artists must be present)
- One missing or extra artist → considered different

### Edge Cases

**Empty Values:**
- Empty tracks list → returns True (don't show)
- Empty main artists → returns True (don't show)
- Track without artist tag → skips that track

**Single Artist Albums:**
- Automatically handled (len(main_artists) < 2)
- Never shows per-track artists
- Same as before

**3+ Main Artists (Various Artists):**
- Now uses smart logic instead of always showing
- Case 1: All on all tracks → hide per-track
- Case 2: Varying → show per-track

## Testing

Test file: `test_smart_artist_display.py`

**Tests:**
1. ✓ Case 1 (all tracks same artists)
2. ✓ Case 2 (different artists per track)
3. ✓ Mixed (some same, some different)
4. ✓ Normalization (case, whitespace)
5. ✓ Edge cases (empty values)

**All tests pass.**

## Migration

**No breaking changes:**
- DJ Mix behavior unchanged
- Single artist albums unchanged
- Only affects multi-artist non-DJ Mix albums
- Guest artist feature still works

**Existing uploads:**
- May see different formatting on re-upload
- Case 1 albums will be cleaner
- Case 2 albums will show same as before

## Files Modified

**brucelee94/uploader/upload.py:**
- Lines 257-290: New function `all_tracks_have_same_artists()`
- Lines 415-423: Smart logic to set `show_track_artists`
- Line 510: Multi-disc uses `show_track_artists`
- Line 577: Single-disc uses `show_track_artists`

## Related Features

**Guest Artist Feature:**
- Still works with smart logic
- When per-track artists shown, guests appear in (feat. ...)
- When hidden, no artist info at all (clean)

**DJ Mix Feature:**
- Completely unchanged
- Uses file-based artist extraction
- Always shows per-track artists
- Excluded from smart logic

**Artist Splitting:**
- Splits on ", " and " & "
- Creates separate [artist] tags
- Used in both header and track lines
