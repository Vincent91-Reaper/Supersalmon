# Track Artist Display Format - Documentation

## Overview

This document describes the improved track artist display format in torrent group descriptions, which separates main artists from featured/guest artists.

## Problem Statement

Previously, all artists (both main and featured/guest) were displayed together before the track title, separated by commas:

```
[b]01.[/b] [artist]Jon Hansen[/artist], [artist]Mary Doufle[/artist] - My love is forever [i](03:45)[/i]
```

This format didn't distinguish between the main artist and featured/guest artists, making it unclear who the primary artist was.

## Solution

The new format separates main artists from featured/guest artists:

```
[b]01.[/b] [artist]Jon Hansen[/artist] - My love is forever (feat. [artist]Mary Doufle[/artist]) [i](03:45)[/i]
```

### Format Breakdown

- **Main artists**: Displayed before the track title
- **Separator**: ` - ` between main artists and title
- **Track title**: In the middle
- **Featured/Guest artists**: Displayed after the title in parentheses with "feat." prefix
- **Duration**: At the end in italics

## Implementation Details

### New Helper Function

`format_track_artists(track_metadata)` - Separates artists by importance:
- Returns tuple: `(main_artists_str, guest_artists_str)`
- Main artists have importance = "main"
- Guest/featured artists have importance = "guest"
- Each artist is wrapped in `[artist]...[/artist]` tags
- Multiple artists are joined with ", "

### Metadata Mapping

The implementation creates a mapping from track identifiers to metadata:
```python
metadata_tracks_map[(disc_num, track_num)] = track_metadata
```

This allows efficient lookup of track artist information during description generation.

### Formatting Logic

For Various Artists albums (3+ main artists):

1. Look up track metadata using disc and track number
2. Extract main and guest artists using `format_track_artists()`
3. Display main artists before title
4. Display guest artists after title in "(feat. ...)" format

For non-Various Artists albums:
- No per-track artist display (uses album artist in header)

## Examples

### Single Main + Single Guest
```
[b]01.[/b] [artist]Jon Hansen[/artist] - My love is forever (feat. [artist]Mary Doufle[/artist]) [i](03:45)[/i]
```

### Multiple Main Artists
```
[b]02.[/b] [artist]Artist A[/artist], [artist]Artist B[/artist] - Track Title [i](04:20)[/i]
```

### Multiple Guest Artists
```
[b]03.[/b] [artist]Main Artist[/artist] - Song Title (feat. [artist]Guest 1[/artist], [artist]Guest 2[/artist]) [i](03:15)[/i]
```

### No Guest Artists
```
[b]04.[/b] [artist]Solo Artist[/artist] - Another Song [i](02:55)[/i]
```

## Benefits

1. **Clarity**: Clear distinction between main and featured artists
2. **Standard Format**: Follows common music industry convention for displaying featured artists
3. **Consistency**: Same format used across all tracks in Various Artists albums
4. **RED Compatibility**: Uses standard RED BBCode tags for artist linking

## Technical Details

### Files Modified

- `brucelee94/uploader/upload.py`
  - Added `format_track_artists()` helper function
  - Modified `generate_description()` to use new format
  - Updated both single-disc and multi-disc track display logic

### Artist Importance Levels

From `brucelee94/constants.py`:
```python
ARTIST_IMPORTANCES = {
    "main": 1,
    "guest": 2,
    "remixer": 3,
    "composer": 4,
    "conductor": 5,
    "djcompiler": 6,
    "producer": 7,
}
```

The implementation currently uses:
- `"main"` - Primary artist(s) of the track
- `"guest"` - Featured/guest artist(s)

### Future Enhancements

Potential improvements:
- Support for other artist types (remixer, producer, etc.)
- Configurable display format
- Different format for different release types

## Testing

A comprehensive test suite (`test_track_artists.py`) validates:
- Single main + guest artist
- Multiple main artists
- Multiple guest artists
- Main artist only (no guests)
- No artists (edge case)

All tests pass successfully ✓

## Migration Notes

This is a non-breaking change:
- Applies only to Various Artists albums
- Non-Various Artists albums remain unchanged
- No configuration changes required
- Automatically applied to all new uploads
