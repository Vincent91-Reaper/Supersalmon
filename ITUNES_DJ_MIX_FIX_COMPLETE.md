# iTunes DJ Mix Per-Track Artist Fix - Complete Documentation

## Problem Statement

DJ Mix torrent descriptions were showing the DJ's name next to every track instead of the actual track artist.

### Example of the Issue

**Incorrect (Before Fix):**
```
Dubfire & Richie Hawtin - Boiler Room: Dubfire b2b Richie Hawtin in Berlin
May 03, 2016

[b]01.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Parts & Labour (Mixed) (03:59)
[b]02.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Another Track (Mixed) (04:12)
```

**Correct (After Fix):**
```
Dubfire & Richie Hawtin - Boiler Room: Dubfire b2b Richie Hawtin in Berlin
May 03, 2016

[b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed) (03:59)
[b]02.[/b] [artist]Different Artist[/artist] - Another Track (Mixed) (04:12)
```

## Root Cause Analysis

### Initial Approach (Failed)
The first fix attempted to extract per-track artists from iTunes JSON-LD data at `track["byArtist"]`. However:

**Problem:** iTunes JSON-LD structure does NOT include per-track artist information.

```json
{
  "@type": "MusicAlbum",
  "byArtist": {...},  // Album-level artist only
  "tracks": [
    {
      "name": "Parts & Labour",
      // NO byArtist field here!
    }
  ]
}
```

### Correct Approach (Working)
Per-track artist information is only available in the HTML, not in JSON-LD.

**HTML Structure:**
```html
<div class="songs-list-row">
  <div class="songs-list__col--song">
    <div class="song-name">Parts & Labour (Mixed)</div>
    <div class="by-line typography-caption">
      By The Junkies
    </div>
  </div>
</div>
```

The `.by-line` element contains the actual track artist!

## Implementation Details

### Changes to iTunes Scraper

**File:** `brucelee94/tagger/sources/itunes.py`

**Key Changes:**

1. **Detect DJ Mix releases:**
   ```python
   release_type = self.parse_release_type(soup)
   is_dj_mix = (release_type == "DJ Mix")
   ```

2. **Parse HTML track list elements (DJ Mix only):**
   ```python
   html_tracks = []
   if is_dj_mix:
       html_tracks = soup.select(".songs-list-row")
   ```

3. **Extract per-track artists from HTML:**
   ```python
   if is_dj_mix:
       per_track_artists = []
       if index - 1 < len(html_tracks):
           html_track = html_tracks[index - 1]
           track_artist_names = parse_artists_track(html_track)
           for artist_name in track_artist_names:
               per_track_artists.append((artist_name, "main"))
   ```

4. **Extract guest artists from title:**
   ```python
   feat_match = RE_FEAT.search(raw_title)
   if feat_match:
       feat_str = feat_match.group(1)
       guest_artists = _parse_artists_commas(feat_str)
       for guest in guest_artists:
           per_track_artists.append((guest, "guest"))
   ```

### Flow Diagram

```
iTunes DJ Mix Scraping Flow
├── 1. Detect release type (DJ Mix)
├── 2. Parse JSON-LD for basic track data (title, duration)
├── 3. Parse HTML for track list elements
│   └── Select .songs-list-row elements
├── 4. For each track:
│   ├── Get JSON-LD data (title, etc.)
│   ├── Get corresponding HTML element (by index)
│   ├── Extract per-track artist from .by-line
│   ├── Extract guest artists from (feat. ...)
│   └── Combine into track metadata
└── 5. Generate track objects with correct artists
```

## Scope and Impact

### What Changed

✅ **DJ Mix uploads from iTunes:**
- Now extract per-track artists from HTML
- Show actual track artists in torrent description
- Correctly separate main vs guest artists

### What Didn't Change

✅ **Regular album uploads from iTunes:**
- Still use album-level artists
- No change to existing behavior
- No HTML parsing performed

✅ **Other scrapers (Qobuz, Tidal, Deezer, etc.):**
- No changes required
- Already handle per-track artists correctly
- Qobuz: Uses `performer` field from API
- Other scrapers: Have their own methods

## Testing

### Test Cases

**1. DJ Mix with per-track artists:**
```python
# Track 1: The Junkies - Parts & Labour
# Track 2: Different Artist - Another Track
# Expected: Each track shows its own artist, not the DJs
```

**2. Regular album:**
```python
# Album: Jon Hansen - Regular Album
# Track 1: Track One
# Track 2: Track Two
# Expected: All tracks show album artist "Jon Hansen"
```

**3. DJ Mix with guest artists:**
```python
# Track: Main Artist - Title (feat. Guest Artist)
# Expected: Main Artist (main), Guest Artist (guest)
```

### Test Files

- `test_itunes_dj_mix_html_extraction.py` - Unit tests for HTML extraction
- `test_dj_mix_track_artists.py` - Integration tests for DJ Mix behavior

## Benefits

### For Users

1. **Accurate Artist Attribution:**
   - Each DJ Mix track shows the actual artist who created it
   - Not the DJ who mixed it (that's in the album header)

2. **Better Discoverability:**
   - Users can find tracks by their actual artist
   - RED's artist linking works correctly

3. **Industry Standard:**
   - Matches how DJ Mixes are credited in the music industry
   - Consistent with other music platforms

### For the Codebase

1. **Targeted Fix:**
   - Only affects DJ Mix releases
   - No impact on regular albums
   - Minimal code changes

2. **Uses Existing Functions:**
   - Reuses `parse_artists_track()` function
   - Leverages existing artist parsing logic
   - No duplicate code

3. **Well-Tested:**
   - Comprehensive test coverage
   - Validates both DJ Mix and regular albums
   - Ensures no regressions

## Comparison with Other Scrapers

### Qobuz (Already Correct)
```python
# Qobuz API provides per-track performer data
performer = safe_get(track, ["performer", "name"])
if performer:
    artists.append((performer, "main"))
```

### iTunes (Now Fixed)
```python
# iTunes requires HTML parsing for per-track artists
if is_dj_mix:
    html_track = html_tracks[index - 1]
    track_artist_names = parse_artists_track(html_track)
```

## Future Considerations

### If iTunes Changes Their HTML Structure

If iTunes updates their website structure:

1. **CSS Selectors might break:**
   - `.songs-list-row` might change
   - `.by-line` might be renamed
   
2. **Fallback behavior:**
   - Code will fall back to album artists
   - Same as current behavior for regular albums
   
3. **Detection:**
   - Scraper will raise ScrapeError if structure changes significantly
   - Manual testing with real URLs will catch issues

### If iTunes Adds JSON-LD Track Artists

If iTunes adds per-track artist data to JSON-LD in the future:

1. **Current code will still work:**
   - HTML parsing takes precedence for DJ Mix
   - No breaking changes needed

2. **Potential optimization:**
   - Could switch to JSON-LD if available
   - Would be faster (no HTML parsing needed)
   - Could be added as a future enhancement

## Summary

**Fixed:** DJ Mix torrent descriptions now show actual track artists instead of DJ names.

**Method:** Parse HTML track list elements to extract per-track artists (iTunes specific).

**Scope:** Only affects DJ Mix uploads from iTunes. Regular albums and other scrapers unchanged.

**Impact:** Better artist attribution, improved discoverability, industry-standard formatting.

**Status:** ✅ Complete and tested.
