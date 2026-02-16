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

The new format separates main artists from featured/guest artists, with different behavior based on album type:

### Various Artists Albums (3+ main artists)

For albums with multiple main artists, both main and guest artists are shown:

```
[b]01.[/b] [artist]Jon Hansen[/artist] - My love is forever (feat. [artist]Mary Doufle[/artist]) [i](03:45)[/i]
```

### Regular Albums (1-2 main artists)

For regular albums, only the title and guest artists are shown (main artist is already in the album header):

```
Album header: [b][artist]Jon Hansen[/artist] - His Love for Paris[/b]

Track listing:
[b]01.[/b] Love (feat. [artist]Mary Doufle[/artist]) [i](03:45)[/i]
[b]02.[/b] Hate (feat. [artist]Barbara Lamon[/artist]) [i](04:20)[/i]
[b]03.[/b] Rage [i](03:30)[/i]
[b]04.[/b] Jealousy [i](02:55)[/i]
```

### Format Breakdown

**Various Artists (3+ main artists):**
- **Main artists**: Displayed before the track title
- **Separator**: ` - ` between main artists and title
- **Track title**: In the middle
- **Featured/Guest artists**: Displayed after the title in parentheses with "feat." prefix
- **Duration**: At the end in italics

**Regular Albums (1-2 main artists):**
- **Track title**: Only the title is shown (main artist already in album header)
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

**For Various Artists albums (3+ main artists):**

1. Look up track metadata using disc and track number
2. Extract main and guest artists using `format_track_artists()`
3. Display main artists before title
4. Display guest artists after title in "(feat. ...)" format

**For Regular albums (1-2 main artists):**

1. Look up track metadata using disc and track number
2. Extract guest artists using `format_track_artists()`
3. Display only title (main artist already in album header)
4. Display guest artists after title in "(feat. ...)" format

## Examples

### Various Artists Album

**Album with 3+ main artists:**
```
Album header: [b]Various Artists - Album Title[/b]

Track 1 (Jon Hansen main, Mary Doufle guest):
[b]01.[/b] [artist]Jon Hansen[/artist] - My love is forever (feat. [artist]Mary Doufle[/artist]) [i](03:45)[/i]

Track 2 (Multiple main artists):
[b]02.[/b] [artist]Artist A[/artist], [artist]Artist B[/artist] - Track Title [i](04:20)[/i]
```

### Regular Album

**Album with 1 main artist (Jon Hansen):**
```
Album header: [b][artist]Jon Hansen[/artist] - His Love for Paris[/b]

Track 1 (with guest Mary Doufle):
[b]01.[/b] Love (feat. [artist]Mary Doufle[/artist]) [i](03:45)[/i]

Track 2 (with guest Barbara Lamon):
[b]02.[/b] Hate (feat. [artist]Barbara Lamon[/artist]) [i](04:20)[/i]

Track 3 (no guests):
[b]03.[/b] Rage [i](03:30)[/i]

Track 4 (no guests):
[b]04.[/b] Jealousy [i](02:55)[/i]
```

### Multiple Main Artists (Various Artists)
```
[b]02.[/b] [artist]Artist A[/artist], [artist]Artist B[/artist] - Track Title [i](04:20)[/i]
```

### Multiple Guest Artists (Various Artists)
```
[b]03.[/b] [artist]Main Artist[/artist] - Song Title (feat. [artist]Guest 1[/artist], [artist]Guest 2[/artist]) [i](03:15)[/i]
```

### Multiple Guest Artists (Regular Album)
```
Album header: [b][artist]Solo Artist[/artist] - Album Title[/b]

Track with multiple guests:
[b]01.[/b] Song Title (feat. [artist]Guest 1[/artist], [artist]Guest 2[/artist]) [i](03:15)[/i]
```

### No Guest Artists (Various Artists)
```
[b]04.[/b] [artist]Solo Artist[/artist] - Another Song [i](02:55)[/i]
```

### No Guest Artists (Regular Album)
```
[b]04.[/b] Another Song [i](02:55)[/i]
```

## Benefits

1. **Clarity**: Clear distinction between main and featured artists
2. **Standard Format**: Follows common music industry convention for displaying featured artists
3. **Consistency**: Applies to ALL albums (both Various Artists and regular albums)
4. **No Redundancy**: For regular albums, main artist isn't repeated on each track (already in header)
5. **RED Compatibility**: Uses standard RED BBCode tags for artist linking

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

A comprehensive test suite validates both album types:

**`test_track_artists.py`** - Original tests for format function:
- Single main + guest artist
- Multiple main artists
- Multiple guest artists
- Main artist only (no guests)
- No artists (edge case)

**`test_extended_artist_format.py`** - Tests for album type behavior:
- Regular album (1 main artist) with guest artists on some tracks
- Various Artists album (3+ main artists) with guest artists
- Validates correct format for each album type

All tests pass successfully ✓

## Migration Notes

This feature applies to ALL albums:
- **Various Artists albums (3+ main artists)**: Shows main artists before title and guests after
- **Regular albums (1-2 main artists)**: Shows only title and guests after (main already in header)
- No configuration changes required
- Automatically applied to all new uploads
