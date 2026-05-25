═══════════════════════════════════════════════════════════════════════
          DJ MIX TRACK ARTIST FIX - ITUNES SCRAPER
═══════════════════════════════════════════════════════════════════════

REQUIREMENT
═══════════════════════════════════════════════════════════════════════

For DJ Mix releases from iTunes/Apple Music:
- Each track should show the ACTUAL artist of that track
- NOT the album's DJ/Compiler names repeated on all tracks

Example:
  Album: "Dubfire & Richie Hawtin - Boiler Room: DJ Mix"
  Track 1: "Parts & Labour (Mixed)" by "The Junkies"
  
  CORRECT: [b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed)
  WRONG:   [b]01.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Parts & Labour (Mixed)

SOLUTION
═══════════════════════════════════════════════════════════════════════

Modified iTunes scraper to extract per-track artists ONLY for DJ Mix releases.

File: brucelee94/tagger/sources/itunes.py
Function: parse_tracks()

Changes:
1. Detect if release is DJ Mix using parse_release_type()
2. Set is_dj_mix flag
3. IF is_dj_mix = True:
     - Extract per-track artists from JSON-LD byArtist field
     - Extract guest artists from (feat. ...) in title
     - Use per-track artists if found
     - Fall back to album artists if not found
4. IF is_dj_mix = False (regular album):
     - Use album-level artists (UNCHANGED behavior)

IMPACT
═══════════════════════════════════════════════════════════════════════

✓ DJ Mix uploads: NOW shows correct per-track artists
✗ Regular album uploads: NO CHANGE (existing behavior maintained)
✗ Other scrapers: NO CHANGE (only iTunes modified)

IMPLEMENTATION DETAILS
═══════════════════════════════════════════════════════════════════════

Code flow in parse_tracks():

1. Parse JSON-LD data from iTunes
2. Call parse_release_type(soup) to detect DJ Mix
3. Set is_dj_mix = (release_type == "DJ Mix")
4. Extract album-level artists as before
5. For each track:
   a. Default: track_artists = album_artists
   b. IF is_dj_mix:
      - Check if track has "byArtist" field in JSON-LD
      - Extract per-track main artists
      - Extract guest artists from title
      - Use per-track artists if found
   c. ELSE (regular album):
      - Use album artists (no change)
6. Generate track with appropriate artists

Per-track artist extraction (DJ Mix only):
```python
if is_dj_mix:
    per_track_artists = []
    if "byArtist" in track:
        artist_data = track["byArtist"]
        if isinstance(artist_data, dict) and "name" in artist_data:
            per_track_artists = [(artist_data["name"], "main")]
        elif isinstance(artist_data, list):
            per_track_artists = [(a["name"], "main") for a in artist_data if "name" in a]
    
    # Extract guest artists from title
    feat_match = RE_FEAT.search(raw_title)
    if feat_match:
        feat_str = feat_match.group(1)
        guest_artists = _parse_artists_commas(feat_str)
        for guest in guest_artists:
            per_track_artists.append((guest, "guest"))
    
    # Use per-track if found
    if per_track_artists:
        track_artists = per_track_artists
```

EXAMPLES
═══════════════════════════════════════════════════════════════════════

DJ Mix Example:
───────────────────────────────────────────────────────────────────────
Album: "Dubfire & Richie Hawtin - Boiler Room: DJ Mix"

Track 1 metadata:
  JSON-LD: {"name": "Parts & Labour (Mixed)", "byArtist": {"name": "The Junkies"}}

BEFORE fix:
  [b]01.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Parts & Labour (Mixed)

AFTER fix:
  [b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed)

Regular Album Example:
───────────────────────────────────────────────────────────────────────
Album: "Album Artist - Album Name"

Track 1 metadata:
  JSON-LD: {"name": "Track One"}  (no byArtist field)

BEFORE fix:
  [b]01.[/b] Track One

AFTER fix:
  [b]01.[/b] Track One  (UNCHANGED)

TESTING
═══════════════════════════════════════════════════════════════════════

Test file: test_itunes_per_track_artists.py

Test 1: DJ Mix
  ✓ is_dj_mix = True
  ✓ Extracts per-track artist "The Junkies"
  ✓ Does NOT use album DJs

Test 2: Regular Album
  ✓ is_dj_mix = False
  ✓ Uses album artist (existing behavior)
  ✓ Does NOT extract per-track artists

VERIFICATION
═══════════════════════════════════════════════════════════════════════

✓ Syntax check: PASSED
✓ All tests: PASSED (2/2)
✓ DJ Mix behavior: FIXED (shows per-track artists)
✓ Regular album behavior: UNCHANGED
✓ No impact on other uploads: CONFIRMED

FILES MODIFIED
═══════════════════════════════════════════════════════════════════════

1. brucelee94/tagger/sources/itunes.py
   - Modified parse_tracks() function
   - Added is_dj_mix detection
   - Added conditional per-track artist extraction

2. test_itunes_per_track_artists.py
   - Test suite for DJ Mix and regular albums
   - Validates DJ Mix-only behavior

LIMITATIONS
═══════════════════════════════════════════════════════════════════════

1. Only applies to iTunes/Apple Music scraper
2. Other scrapers (Qobuz, Tidal, Deezer, etc.) NOT modified
3. Requires JSON-LD data to include per-track byArtist field
4. Falls back to album artists if per-track data not available

NEXT STEPS (if needed)
═══════════════════════════════════════════════════════════════════════

User would need to approve changes to other scrapers:
- Qobuz
- Tidal  
- Deezer
- Beatport (already has per-track artists)
- Others

Current status: ONLY iTunes scraper modified per user requirement.

SUMMARY
═══════════════════════════════════════════════════════════════════════

✓ Fixed DJ Mix track artist display for iTunes/Apple Music
✓ Shows actual track artists (The Junkies) not album DJs (Dubfire & Richie Hawtin)
✓ Regular albums UNCHANGED (existing behavior preserved)
✓ No impact on other scrapers or upload types
✓ Tests passing
✓ Ready for use

═══════════════════════════════════════════════════════════════════════
                    DJ MIX FIX COMPLETE ✓
═══════════════════════════════════════════════════════════════════════
