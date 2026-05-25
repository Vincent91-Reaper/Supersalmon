# DJ Mix - Unified Detection and Per-Track Artist Extraction

## Overview

This document describes the unified approach for detecting DJ Mix releases and extracting per-track artists across all scrapers (iTunes, Qobuz, Tidal, Deezer, Beatport).

## User Requirements

1. **Detect DJ Mix by checking if "DJ mix" appears in release name**
2. **If DJ Mix detected, extract per-track artists for torrent description**

## Implementation

### 1. DJ Mix Detection

All scrapers now use a consistent approach to detect DJ Mix releases:

**Detection Method:**
- Check the release title/name for "DJ Mix" pattern
- Use regex: `r"DJ[\s\-]*Mix"` (case-insensitive)

**Pattern Matches:**
- `"DJ Mix"`
- `"DJ-Mix"`
- `"DJMix"`
- `"dj mix"`
- `"Various Artists - Boiler Room (DJ Mix)"`
- `"Live DJ Mix from Berlin"`

**Pattern Does NOT Match:**
- `"DJ Shadow - Endtroducing"` (DJ is artist name, not DJ Mix)
- `"Mixer Selection"`
- `"Regular Album"`

### 2. Implementation by Scraper

#### iTunes (`brucelee94/tagger/sources/itunes.py`)

```python
def parse_release_type(self, soup):
    title = soup.find("meta", {"name": "apple:title"})["content"].strip()
    # Check for DJ Mix first
    if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
        return "DJ Mix"
    # ... other checks
```

**Per-Track Artist Extraction:**
- Parses HTML track list (`.songs-list-row` elements)
- Extracts artists from `.by-line` elements
- Uses `parse_artists_track()` helper function
- Only for DJ Mix releases

#### Qobuz (`brucelee94/tagger/sources/qobuz.py`)

```python
def parse_release_type(self, soup):
    title = soup.get("title", "")
    # Check for DJ Mix first
    if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
        return "DJ Mix"
    # ... other checks
```

**Per-Track Artist Extraction:**
- Already extracts from `track["performer"]["name"]` field
- Automatically works for all releases including DJ Mix
- No special handling needed

#### Tidal (`brucelee94/tagger/sources/tidal.py`)

```python
def parse_release_type(self, soup):
    title = soup.get("title", "")
    # Check for DJ Mix first
    if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
        return "DJ Mix"
    # Try RECORD_TYPES mapping
    try:
        return RECORD_TYPES[soup["type"]]
    except KeyError:
        return None
```

**Per-Track Artist Extraction:**
- Parses `track["artists"]` for each track
- Already extracts per-track artists
- Works automatically for DJ Mix

#### Deezer (`brucelee94/tagger/sources/deezer.py`)

```python
def parse_release_type(self, soup):
    title = soup.get("title", "")
    # Check for DJ Mix first
    if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
        return "DJ Mix"
    # Try RECORD_TYPES mapping
    try:
        return RECORD_TYPES[soup["record_type"]]
    except KeyError:
        return None
```

**Per-Track Artist Extraction:**
- Parses `track["SNG_CONTRIBUTORS"]` and `track["ARTISTS"]`
- Already extracts per-track artists
- Works automatically for DJ Mix

#### Beatport (`brucelee94/tagger/sources/beatport.py`)

```python
def parse_release_type(self, soup):
    try:
        title = soup["state"]["data"]["results"][0]["release"]["name"]
        # Check for DJ Mix
        if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
            return "DJ Mix"
        return "EP"  # Default for Beatport
    except (KeyError, IndexError):
        return "EP"
```

**Per-Track Artist Extraction:**
- Parses artists from track data
- Already extracts per-track artists
- Works automatically for DJ Mix

## 3. Torrent Description Generation

The upload logic (`brucelee94/uploader/upload.py`) uses the release type:

```python
if metadata.get("rls_type") == "DJ Mix":
    # Use DJ/Compiler artists in header
    # Mark as Various Artists (shows per-track artists)
    is_various_artists = True
```

**DJ Mix Track Format:**
```
[b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]
```

Not:
```
[b]01.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Parts & Labour (Mixed)
```

## 4. Testing

### Pattern Testing

```python
import re
pattern = r"DJ[\s\-]*Mix"

# Should match
assert re.search(pattern, "Various Artists - DJ Mix", re.IGNORECASE)
assert re.search(pattern, "Boiler Room (DJ-Mix)", re.IGNORECASE)

# Should not match
assert not re.search(pattern, "DJ Shadow - Album", re.IGNORECASE)
```

### Integration Testing

Test file: `test_dj_mix_detection_all_scrapers.py`
- Tests pattern matching
- Tests each scraper's `parse_release_type()` method
- Verifies DJ Mix is detected correctly
- Verifies non-DJ Mix is not falsely detected

## 5. Benefits

1. **Consistent Detection:** All scrapers use same pattern
2. **Correct Artist Display:** Shows actual track artists, not DJs
3. **Non-Breaking:** Regular albums unaffected
4. **Automatic:** No manual configuration needed
5. **Universal:** Works across all music sources

## 6. Example Output

### Before (Incorrect)

```
Dubfire & Richie Hawtin - Boiler Room: Dubfire b2b Richie Hawtin
May 03, 2016

[b]01.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]
[b]02.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Another Track (Mixed) [i](04:12)[/i]
```

### After (Correct)

```
Dubfire & Richie Hawtin - Boiler Room: Dubfire b2b Richie Hawtin
May 03, 2016

[b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]
[b]02.[/b] [artist]Different Artist[/artist] - Another Track (Mixed) [i](04:12)[/i]
```

## 7. Files Modified

1. `brucelee94/tagger/sources/qobuz.py` - Added DJ Mix detection
2. `brucelee94/tagger/sources/tidal.py` - Added DJ Mix detection
3. `brucelee94/tagger/sources/deezer.py` - Added DJ Mix detection
4. `brucelee94/tagger/sources/beatport.py` - Added `parse_release_type()` with DJ Mix detection
5. `brucelee94/tagger/sources/itunes.py` - Already had DJ Mix detection
6. `test_dj_mix_detection_all_scrapers.py` - New test suite

## 8. Summary

✅ **Detection:** All scrapers detect DJ Mix from release title
✅ **Extraction:** All scrapers extract per-track artists automatically
✅ **Display:** Torrent descriptions show correct track artists
✅ **Consistency:** Unified approach across all sources
✅ **Testing:** Comprehensive test coverage

The implementation follows the user's preferred approach exactly as requested.
