═══════════════════════════════════════════════════════════════════════
                    DJ MIX EXCEPTION - SUMMARY
═══════════════════════════════════════════════════════════════════════

CHANGE REVERTED
═══════════════════════════════════════════════════════════════════════

DJ Mix was incorrectly modified to use the new `show_track_main_artist` 
refined logic. This has been reverted.

DJ Mix is now an EXCEPTION to the refined artist display logic.

CURRENT BEHAVIOR
═══════════════════════════════════════════════════════════════════════

┌─────────────────────┬──────────────────────┬────────────────────────┐
│ Release Type        │ Logic Used           │ Per-Track Main Artist  │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ DJ Mix              │ is_various_artists   │ ALWAYS shown           │
│                     │ (exception)          │                        │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ Regular Album       │ show_track_main_     │ Based on count:        │
│ (1 main artist)     │ artist (refined)     │ - 1 main: HIDDEN       │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ Regular Album       │ show_track_main_     │ - 2+ main: SHOWN       │
│ (2+ main artists)   │ artist (refined)     │                        │
└─────────────────────┴──────────────────────┴────────────────────────┘

CODE CHANGES
═══════════════════════════════════════════════════════════════════════

File: brucelee94/uploader/upload.py

1. DJ Mix section (removed show_track_main_artist assignment):

   BEFORE:
   ```python
   is_various_artists = True
   show_track_main_artist = True  # Always show per-track artists for DJ Mix
   ```

   AFTER:
   ```python
   is_various_artists = True
   # DJ Mix is an exception - it uses is_various_artists, not show_track_main_artist
   ```

2. Track display logic (check both flags):

   BEFORE:
   ```python
   if show_track_main_artist and main_artists_str:
       description += f"{main_artists_str} - "
   ```

   AFTER:
   ```python
   if (is_various_artists or show_track_main_artist) and main_artists_str:
       description += f"{main_artists_str} - "
   ```

WHY THIS CHANGE?
═══════════════════════════════════════════════════════════════════════

DJ Mix is a special release type that should ALWAYS show per-track 
artists, regardless of the refined logic based on main artist count.

The refined logic (show_track_main_artist) is designed for regular 
albums to:
  - Hide per-track main for 1 main artist albums (avoid redundancy)
  - Show per-track main for 2+ main artist albums (clarity)

DJ Mix doesn't follow this pattern because:
  - It has a DJ/Compiler in the header (not the track artists)
  - It always shows all performers per track
  - It should not be affected by the count-based logic

EXAMPLES
═══════════════════════════════════════════════════════════════════════

DJ Mix (Exception):
───────────────────────────────────────────────────────────────────────
Album Header:
[b][artist]DJ Name[/artist] - Mix Title[/b]

Track Listing (ALWAYS shows per-track main):
[b]01.[/b] [artist]Artist A[/artist] - Track One (feat. [artist]Guest B[/artist])
[b]02.[/b] [artist]Artist C[/artist] - Track Two

Regular Album with 1 Main Artist (Refined Logic):
───────────────────────────────────────────────────────────────────────
Album Header:
[b][artist]Jon Hansen[/artist] - Album Title[/b]

Track Listing (HIDES per-track main):
[b]01.[/b] Love (feat. [artist]Mary Doufle[/artist])
[b]02.[/b] Hate

Regular Album with 2 Main Artists (Refined Logic):
───────────────────────────────────────────────────────────────────────
Album Header:
[b][artist]David Ide[/artist] & [artist]Zoe MacDonald[/artist] - Album Title[/b]

Track Listing (SHOWS per-track main):
[b]01.[/b] [artist]David Ide[/artist] - Love (feat. [artist]Mary Doufle[/artist])
[b]02.[/b] [artist]Zoe MacDonald[/artist] - Hate

TESTING
═══════════════════════════════════════════════════════════════════════

Test Suite: test_dj_mix_exception.py

✓ DJ Mix uses is_various_artists (always shows per-track main)
✓ Regular albums use show_track_main_artist (refined logic)
✓ All tests pass

SUMMARY
═══════════════════════════════════════════════════════════════════════

✓ DJ Mix is an EXCEPTION
✓ Uses is_various_artists flag
✓ Always shows per-track main artists
✓ NOT affected by refined artist count logic
✓ Regular albums continue using refined logic

═══════════════════════════════════════════════════════════════════════
                       STATUS: REVERTED ✓
═══════════════════════════════════════════════════════════════════════
