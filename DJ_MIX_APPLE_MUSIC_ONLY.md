# DJ Mix Detection - Apple Music Only

## Summary

DJ Mix detection is now **ONLY** active for Apple Music (iTunes) uploads, as requested by the user.

## Current Implementation

### ✅ Apple Music (iTunes)
- **Detection:** Active
- **Pattern:** `r"DJ[\s\-]*Mix"` (case-insensitive)
- **Location:** `parse_release_type()` in `brucelee94/tagger/sources/itunes.py`
- **Behavior:** 
  - Detects DJ Mix from release title
  - Extracts per-track artists from HTML track list
  - Shows correct track artists in torrent description

### ❌ Other Music Sources

**Qobuz, Tidal, Deezer, Beatport:**
- **Detection:** Disabled (reverted)
- **Behavior:** Use default release type detection
- **Artist Handling:** Standard (album-level artists)

## Detection Pattern

The iTunes scraper uses this regex pattern to detect DJ Mix:

```python
r"DJ[\s\-]*Mix"  # Case-insensitive
```

**Matches:**
- "DJ Mix"
- "DJ-Mix"
- "DJMix"
- "dj mix"
- "Various Artists - Boiler Room (DJ Mix)"

**Does NOT match:**
- "DJ Shadow - Album" (DJ is artist name)
- "Mixer" (different word)
- "Regular Album"

## Example Output

### Apple Music DJ Mix

**Before Fix:**
```
[b]01.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Parts & Labour (Mixed)
```

**After Fix:**
```
[b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed)
```

### Other Sources (Qobuz, Tidal, Deezer, Beatport)

**Behavior:**
- No DJ Mix detection
- Standard release type detection
- Standard artist handling

## Technical Details

### iTunes Implementation

**File:** `brucelee94/tagger/sources/itunes.py`

**Detection (parse_release_type):**
```python
def parse_release_type(self, soup):
    try:
        title = soup.find("meta", {"name": "apple:title"})["content"].strip()
        # Check for DJ Mix first
        if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
            return "DJ Mix"
        # ... other type checks
    except TypeError as e:
        raise ScrapeError("Could not parse release type.") from e
```

**Per-Track Artist Extraction (parse_tracks):**
```python
# For DJ Mix: Parse HTML track elements to extract per-track artists
if is_dj_mix:
    html_tracks = soup.select(".songs-list-row")
    # Extract artist from HTML .by-line elements
    # Match to JSON-LD tracks by index
```

### Other Scrapers

**Files:**
- `brucelee94/tagger/sources/qobuz.py`
- `brucelee94/tagger/sources/tidal.py`
- `brucelee94/tagger/sources/deezer.py`
- `brucelee94/tagger/sources/beatport.py`

**Status:** DJ Mix detection code has been removed. These scrapers use their default release type detection.

## Testing

**Test File:** `test_dj_mix_apple_music_only.py`

**Tests:**
1. ✅ iTunes has DJ Mix detection pattern
2. ✅ Pattern correctly matches DJ Mix titles
3. ✅ Pattern doesn't match non-DJ Mix titles
4. ✅ Qobuz does NOT have DJ Mix detection
5. ✅ Tidal does NOT have DJ Mix detection
6. ✅ Deezer does NOT have DJ Mix detection
7. ✅ Beatport does NOT have DJ Mix detection

## Change History

### Latest Change (Current)
**Reverted DJ Mix detection to Apple Music only**
- Removed DJ Mix detection from Qobuz
- Removed DJ Mix detection from Tidal
- Removed DJ Mix detection from Deezer
- Removed DJ Mix detection from Beatport
- Kept DJ Mix detection in iTunes (Apple Music)

### Previous Changes (Reverted)
- Had added DJ Mix detection to all scrapers (Qobuz, Tidal, Deezer, Beatport)
- User requested to keep it Apple Music only

## Why Apple Music Only?

Per user request, DJ Mix detection should only work for Apple Music uploads. The rationale:
- Apple Music has specific DJ Mix formatting in their metadata
- Other sources may not have the same DJ Mix conventions
- Simpler to maintain detection in one scraper
- Reduces risk of false positives on other platforms

## Future Considerations

If DJ Mix detection is needed for other sources in the future:
1. Verify the source has DJ Mix releases with proper metadata
2. Test the detection pattern doesn't cause false positives
3. Ensure per-track artist data is available in the source's API/HTML
4. Add detection following the same pattern as iTunes
5. Add comprehensive tests

## Status

✅ **IMPLEMENTATION COMPLETE**
- DJ Mix detection: Apple Music only
- Other sources: Reverted to default behavior
- Tests passing
- Documentation complete
