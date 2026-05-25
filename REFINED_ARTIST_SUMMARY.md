═══════════════════════════════════════════════════════════════════════
         REFINED ARTIST DISPLAY LOGIC - IMPLEMENTATION COMPLETE ✓
═══════════════════════════════════════════════════════════════════════

NEW REQUIREMENT ADDRESSED
═══════════════════════════════════════════════════════════════════════

The user requested refined behavior based on album main artist count:

1. Albums with 1 main artist: Hide per-track main (already in header)
2. Albums with 2 main artists: Show per-track main (may vary)
3. Albums with 3+ main artists: Show per-track main (varies)

IMPLEMENTATION
═══════════════════════════════════════════════════════════════════════

Key Logic:
  show_track_main_artist = len(main_artists) >= 2

This flag determines whether to show the main artist on each track.

═══════════════════════════════════════════════════════════════════════
                EXAMPLE 1: ALBUM WITH 1 MAIN ARTIST
═══════════════════════════════════════════════════════════════════════

Album: "Jon Hansen - His Love for Paris"
Main Artists: Jon Hansen (1)

Album Header:
[b][artist]Jon Hansen[/artist] - His Love for Paris[/b]

Track Listing:
[b]01.[/b] Love (feat. [artist]Mary Doufle[/artist])
[b]02.[/b] Hate (feat. [artist]Barbara Lamon[/artist])
[b]03.[/b] Rage
[b]04.[/b] Jealousy

✓ Main artist NOT shown per track (already in header)
✓ Guest artists shown after title in (feat. ...)
✓ No redundancy

═══════════════════════════════════════════════════════════════════════
               EXAMPLE 2: ALBUM WITH 2 MAIN ARTISTS
═══════════════════════════════════════════════════════════════════════

Album: "David Ide & Zoe MacDonald - Vietnam love"
Main Artists: David Ide, Zoe MacDonald (2)

Album Header:
[b][artist]David Ide[/artist] & [artist]Zoe MacDonald[/artist] - Vietnam love[/b]

Track Listing:
[b]01.[/b] [artist]David Ide[/artist] - Love (feat. [artist]Mary Doufle[/artist])
[b]02.[/b] [artist]Zoe MacDonald[/artist] - Love (feat. [artist]Jason Moroe[/artist])
[b]03.[/b] [artist]David Ide[/artist] - Love (feat. [artist]Barbara Lamon[/artist])

✓ Main artist SHOWN per track (different artists on different tracks)
✓ Guest artists shown after title in (feat. ...)
✓ Clear which main artist is on each track

═══════════════════════════════════════════════════════════════════════
             EXAMPLE 3: ALBUM WITH 3+ MAIN ARTISTS (VARIOUS)
═══════════════════════════════════════════════════════════════════════

Album: "Various Artists - Compilation"
Main Artists: Multiple (3+)

Album Header:
[b]Various Artists - Compilation[/b]

Track Listing:
[b]01.[/b] [artist]Jon Hansen[/artist] - My love is forever (feat. [artist]Mary Doufle[/artist])
[b]02.[/b] [artist]Artist A[/artist], [artist]Artist B[/artist] - Another Track

✓ Main artist SHOWN per track (many different artists)
✓ Guest artists shown after title in (feat. ...)
✓ Standard Various Artists behavior

═══════════════════════════════════════════════════════════════════════
                         COMPARISON TABLE
═══════════════════════════════════════════════════════════════════════

┌─────────────────┬────────────────────┬──────────────────────────────┐
│ Main Artists    │ Show Per-Track     │ Track Format                 │
├─────────────────┼────────────────────┼──────────────────────────────┤
│ 1               │ No (False)         │ Title (feat. [Guest])        │
├─────────────────┼────────────────────┼──────────────────────────────┤
│ 2               │ Yes (True)         │ [Main] - Title (feat. [G])   │
├─────────────────┼────────────────────┼──────────────────────────────┤
│ 3+              │ Yes (True)         │ [Main] - Title (feat. [G])   │
└─────────────────┴────────────────────┴──────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
                         CODE CHANGES
═══════════════════════════════════════════════════════════════════════

File: brucelee94/uploader/upload.py

1. Added show_track_main_artist flag:
   show_track_main_artist = len(main_artists) >= 2

2. Changed condition in track display:
   FROM: if is_various_artists and main_artists_str:
   TO:   if show_track_main_artist and main_artists_str:

3. Applied to both:
   - DJ Mix releases
   - Regular album releases
   - Multi-disc sections
   - Single-disc sections

═══════════════════════════════════════════════════════════════════════
                           TESTING
═══════════════════════════════════════════════════════════════════════

Test Suite 1: test_track_artists.py
  ✓ Artist formatting function tests

Test Suite 2: test_extended_artist_format.py
  ✓ Regular vs Various Artists albums

Test Suite 3: test_refined_artist_format.py
  ✓ 1 main artist album
  ✓ 2 main artists album
  ✓ 3+ main artists album

ALL TESTS PASSED ✓

Security Scan: 0 alerts ✓

═══════════════════════════════════════════════════════════════════════
                           BENEFITS
═══════════════════════════════════════════════════════════════════════

✓ Smart display based on context
✓ No redundancy for single artist albums
✓ Clear per-track attribution for multi-artist albums
✓ Handles collaboration albums correctly (2 artists)
✓ Follows music industry conventions
✓ RED BBCode compatible

═══════════════════════════════════════════════════════════════════════
                           COMMITS
═══════════════════════════════════════════════════════════════════════

259ff3b - Extend to all albums (1st iteration)
8dc9d6e - Refine logic for 1/2/3+ main artists
81aff00 - Update documentation

═══════════════════════════════════════════════════════════════════════
                        INSTALLATION
═══════════════════════════════════════════════════════════════════════

uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again

═══════════════════════════════════════════════════════════════════════
                    STATUS: COMPLETE ✓
═══════════════════════════════════════════════════════════════════════
