# Guest Artist Display Fix Documentation

## Problem Statement

For Tidal uploads, brucelee94 correctly identifies main and guest artists in metadata (fixed in commit 00df465), but guest artists were not appearing in the torrent description.

### User's Example

**Track "03. ZigZagueZ" from album "ORSUJE":**
```
Album/Performer (albumartist): Ismail Candide, Eddy Woogy
Performer (artist): Ismail Candide, Eddy Woogy, Christine Ly

Identified correctly:
  Main artists: Ismail Candide, Eddy Woogy
  Guest artist: Christine Ly

Expected in description:
  [b]03.[/b] ZigZagueZ (feat. [artist]Christine Ly[/artist])

Actual (before fix):
  [b]03.[/b] ZigZagueZ
  (Christine Ly not shown)
```

## Root Cause

### Smart Artist Display Logic

Commit c051225 added smart artist display logic:
- If all tracks have the same main artists, don't show per-track artists (redundant)
- Sets `show_track_artists = False` when main artists don't vary

### The Bug

When `show_track_artists = False`, the code path was:

**brucelee94/uploader/upload.py (before fix):**
```python
if show_track_artists and track_metadata:
    # Show main artists and guests
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    # ... display main and guests ...
else:
    # BUG: Only show title, ignore all artists including guests!
    description += f"{track['t'].title} [i]({length})[/i]\n"
```

**Problem:** The `else` branch completely ignored guest artists, even though they exist in `track_metadata`.

## Solution

### Modified Logic

When `show_track_artists` is `False`:
1. Don't show main artists (they don't vary, already in header)
2. **But DO check for and display guest artists**

**brucelee94/uploader/upload.py (after fix):**
```python
if show_track_artists and track_metadata:
    # Show main artists and guests
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    # ... display main and guests ...
else:
    # Main artists don't vary, so don't show them per-track
    # But still check for guest artists to display
    title = track['t'].title
    
    # Check if title already has inline guest artists
    if title_has_inline_guests:
        # Add BBCode to inline guests
        description += add_artist_bbcode_to_feat(title)
    else:
        # No inline guests in title
        description += title
        # Check metadata for guest artists and append if present
        if track_metadata:
            _, guest_artists_str = format_track_artists(track_metadata)
            if guest_artists_str:
                description += f" (feat. {guest_artists_str})"
    
    description += f" [i]({length})[/i]\n"
```

### Key Points

1. **Main artists:** Not shown when they don't vary (smart display logic preserved)
2. **Guest artists:** Always shown when present (new fix)
3. **Inline guests:** Handled with BBCode if already in title
4. **Metadata guests:** Appended in (feat. ...) format if not in title

## Code Changes

### File: brucelee94/uploader/upload.py

**Change 1: Multi-disc section (lines 583-604)**

Before:
```python
else:
    # No artist separation for non-various albums
    description += f"{track['t'].title} [i]({length})[/i]\n"
```

After:
```python
else:
    # Main artists don't vary, so don't show them per-track
    # But still check for guest artists to display
    title = track['t'].title
    
    # Check if title already has inline guest artists
    import re
    title_has_inline_guests = re.search(r'\((feat\.|ft\.|featuring)', title, re.IGNORECASE)
    
    if title_has_inline_guests:
        # Add BBCode to inline guests
        description += add_artist_bbcode_to_feat(title)
    else:
        # No inline guests in title
        description += title
        # Check metadata for guest artists and append if present
        if track_metadata:
            _, guest_artists_str = format_track_artists(track_metadata)
            if guest_artists_str:
                description += f" (feat. {guest_artists_str})"
    
    description += f" [i]({length})[/i]\n"
```

**Change 2: Single-disc section (lines 663-684)**

Same logic applied to single-disc albums for consistency.

## Examples

### Example 1: User's Scenario (Tidal - ORSUJE)

**Album:** ORSUJE by Ismail Candide, Eddy Woogy

**Tracks:**
- Track 01: "Track One" (Ismail + Eddy)
- Track 02: "Track Two" (Ismail + Eddy)
- Track 03: "ZigZagueZ" (Ismail + Eddy + Christine Ly)

**Logic:**
- All tracks have same main artists: Ismail Candide, Eddy Woogy
- `show_track_artists = False` (main artists don't vary)
- Track 03 has guest artist: Christine Ly

**Before Fix:**
```
[b][artist]Ismail Candide[/artist], [artist]Eddy Woogy[/artist] - ORSUJE[/b]

[b]01.[/b] Track One
[b]02.[/b] Track Two
[b]03.[/b] ZigZagueZ
```
❌ Christine Ly not shown

**After Fix:**
```
[b][artist]Ismail Candide[/artist], [artist]Eddy Woogy[/artist] - ORSUJE[/b]

[b]01.[/b] Track One
[b]02.[/b] Track Two
[b]03.[/b] ZigZagueZ (feat. [artist]Christine Ly[/artist])
```
✅ Christine Ly shown as guest

### Example 2: Inline Guest in Title

**Track title:** "My Love (feat. Guest Artist)"

**Before Fix:** (Same as after for inline guests)
```
[b]01.[/b] My Love (feat. Guest Artist)
```

**After Fix:**
```
[b]01.[/b] My Love (feat. [artist]Guest Artist[/artist])
```
✅ BBCode added to inline guest mention

### Example 3: No Guests

**Track:** Only main artists, no guests

**Output:**
```
[b]01.[/b] Track Title
```
✅ No feat. suffix when no guests

### Example 4: Various Artists Album

**Album:** Various Artists (main artists vary per track)

**Logic:**
- Main artists differ across tracks
- `show_track_artists = True`
- Original logic applies (unchanged by this fix)

**Output:**
```
[b]01.[/b] [artist]Artist A[/artist] - Track One (feat. [artist]Guest[/artist])
[b]02.[/b] [artist]Artist B[/artist] - Track Two
```
✅ Shows both main and guest artists per track

## Testing

### Test File: test_guest_display_logic.py

**Test Scenario:**
- Album with 2 main artists (Ismail, Eddy) on all tracks
- Track 3 has additional guest artist (Christine)
- Validates that guest appears even when `show_track_artists = False`

**Test Results:**
```
✓ Guest artist 'Christine Ly' found in track 3 metadata
✓ show_track_artists is False (main artists don't vary)
✓ With fix: Guests are displayed regardless of show_track_artists

Test PASSED! ✓
```

## Benefits

1. ✅ **Guest artists always displayed** when present in metadata
2. ✅ **Smart main artist logic preserved** (don't show redundant mains)
3. ✅ **Inline guest handling** (BBCode added to existing feat. mentions)
4. ✅ **Metadata-based guests** (appended when not in title)
5. ✅ **Consistent behavior** across multi-disc and single-disc albums

## Impact

### Fixed
- ✅ Tidal uploads: Guest artists now appear
- ✅ All file-based metadata sources with guest artists
- ✅ User's example scenario works correctly

### Unchanged
- ✅ DJ Mix handling (separate code path)
- ✅ Smart main artist display logic
- ✅ Inline guest BBCode feature
- ✅ Various Artists albums (main artists vary)
- ✅ Other metadata sources (iTunes, Qobuz, Deezer, Beatport)

## Related Commits

- **00df465** - Tidal artist identification fix (main vs guest)
- **c051225** - Smart artist display logic
- **1122a7e** - Inline guest BBCode feature
- **18b4b2f** - Guest artist display fix (this commit)

## Edge Cases Handled

1. **No track metadata:** Gracefully handled (no crash)
2. **No guest artists:** No feat. suffix added
3. **Inline guests in title:** BBCode added, no duplication
4. **Multiple guests:** All shown in feat. list
5. **Guest + inline:** Inline takes precedence (no duplication)

## Future Considerations

1. **Consistency:** Ensure all metadata sources benefit from guest display
2. **Testing:** Add integration tests with real Tidal files
3. **Documentation:** Update user guide with guest artist examples
4. **Validation:** Verify guest artists are properly detected from various file formats

## Summary

This fix ensures that guest artists are always displayed in torrent descriptions, regardless of whether main artists vary across tracks. It preserves the smart artist display logic while ensuring no artist information is lost.

**Before:** Guest artists ignored when main artists don't vary
**After:** Guest artists always shown when present in metadata
