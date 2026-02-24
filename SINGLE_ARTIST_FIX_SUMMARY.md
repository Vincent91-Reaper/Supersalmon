# Single-Artist Redundancy Fix - Summary

## Problem
For non-DJ mix albums with only 1 main artist, the artist name was being shown next to every track in the torrent description, even though this is redundant (the album header already shows the artist).

## Solution
Modified the artist display logic to never show per-track artists for single-artist albums.

## Before Fix
```
Album: "Solo Album" by Artist A
[b]01.[/b] Artist A - Track One
[b]02.[/b] Artist A - Track Two  
[b]03.[/b] Artist A - Track Three
```
❌ Artist A is repeated on every track (redundant)

## After Fix
```
Album: "Solo Album" by Artist A
[b]01.[/b] Track One
[b]02.[/b] Track Two
[b]03.[/b] Track Three
```
✅ Clean and non-redundant!

## Artist Display Logic (Non-DJ Mix Albums)

### Case 1: Single-Artist Album
- **Condition:** Album has 1 main artist
- **Action:** Never show per-track artists
- **Reason:** Redundant (artist already in album header)

### Case 2: Multi-Artist Album (All Artists on All Tracks)
- **Condition:** Album has multiple main artists, all contribute to all tracks
- **Example:** Album by "Artist A, Artist B, Artist C" and all tracks have all 3 artists
- **Action:** Don't show per-track artists  
- **Reason:** Redundant (same artists on every track)

### Case 3: Multi-Artist Album (Artists Vary Per Track)
- **Condition:** Album has multiple main artists, different artists on different tracks
- **Example:** Album by "Artist A, Artist B, Artist C" but Track 1 has only A, Track 2 has only B, Track 3 has only C
- **Action:** Show per-track artists
- **Reason:** Needed for clarity (artists vary)

## DJ Mix Albums
DJ Mix albums are **excluded** from this logic and have their own separate artist display handling.

## Applies To
This fix applies to all non-DJ mix uploads from:
- ✅ Qobuz
- ✅ Tidal  
- ✅ Deezer
- ✅ Beatport
- ✅ Apple Music

## Testing
All test scenarios pass:
- ✅ Single-artist album → Don't show per-track
- ✅ Multi-artist, same on all → Don't show per-track
- ✅ Multi-artist, varying → Show per-track
- ✅ DJ Mix → Excluded from logic

## Code Change
File: `brucelee94/uploader/upload.py` (lines 474-482)

```python
if not is_dj_mix:
    # For single-artist albums, never show per-track artists (redundant)
    if len(main_artists) == 1:
        show_track_artists = False
    else:
        # For multi-artist albums, check if artists vary
        tracks_have_same_artists = all_tracks_have_same_artists(...)
        show_track_artists = not tracks_have_same_artists
```

## Status
✅ **Production Ready** - Tested and working correctly!
