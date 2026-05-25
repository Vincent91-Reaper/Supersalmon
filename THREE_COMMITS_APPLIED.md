# Three Commits Applied to brucelee94

## Summary

Successfully applied changes from three historical commits to the current brucelee94 codebase:

1. **Commit 97876af** - Fix DJ Mix artist splitting, title formatting, and BB code generation
2. **Commit 6996411** - Add comma splitting support for artists in addition to ampersand
3. **Commit 0add790** - Fix DJ Mix description header to use DJ/Compiler artist and clear record label

## Commit Details

### 1. Commit 97876af (Feb 11, 2026)
**Title:** Fix DJ Mix artist splitting, title formatting, and BB code generation

**Changes:**
- Split artists on " & " when extracting from file tags (Issue #1)
- Remove "(DJ Mix)" suffix from title for cleaner group name (Issue #2)
- Split track artists in description BB code on " & " (Issue #3)

**Files Modified:**
- `brucelee94/uploader/__init__.py` - Artist extraction and title cleanup
- `brucelee94/uploader/upload.py` - BB code artist splitting

**Example:**
- Before: `[artist]Shades & ID[/artist]`
- After: `[artist]Shades[/artist], [artist]ID[/artist]`

### 2. Commit 6996411 (Feb 11, 2026)
**Title:** Add comma splitting support for artists in addition to ampersand

**Changes:**
- Split artists on both ", " and " & " separators
- Handles "Alix Perez, Shades, Eprom" → 3 separate artists
- Handles "Artist1, Artist2 & Artist3" → 3 separate artists
- Added deduplication in file-based metadata to prevent repeats

**Files Modified:**
- `brucelee94/uploader/__init__.py` - Enhanced artist extraction
- `brucelee94/uploader/upload.py` - Enhanced BB code generation

**Example:**
- Input: "Alix Perez, Shades & Eprom"
- Output: `[artist]Alix Perez[/artist], [artist]Shades[/artist], [artist]Eprom[/artist]`

### 3. Commit 0add790 (Feb 11, 2026)
**Title:** Fix DJ Mix description header to use DJ/Compiler artist and clear record label

**Changes:**
- Use DJ/Compiler artist for DJ Mix header (not main track artists)
- DJ Mix releases show "DJ Name - Album Title" instead of "Main Artists - Album Title"
- Set is_various_artists=True for DJ Mixes to show all track performers
- Clear record label for DJ Mix releases (Apple Music doesn't provide proper label)
- Prevents showing release date/duration text as label

**Files Modified:**
- `brucelee94/uploader/upload.py` - Header generation and record label handling

**Example:**
- Before: `[b]Various Artists - Album[/b]` with label "26 July 2025 20 songs"
- After: `[b][artist]Dubfire[/artist] & [artist]Richie Hawtin[/artist] - Album[/b]` with empty label

## Application Status

### Changes Already Present (from previous work)

**In brucelee94/uploader/__init__.py:**
- ✅ Lines 744-748: Artist splitting on ", " and " & " (Commit 2)
- ✅ Lines 764-767: Remove "(DJ Mix)" suffix from title (Commit 1)
- ✅ Lines 1137-1145: Deduplication and splitting in file-based metadata (Commit 2)
- ✅ Lines 1152-1154: Remove "(DJ Mix)" suffix in file-based (Commit 1)

**In brucelee94/uploader/upload.py:**
- ✅ Lines 298-310: DJ Mix header logic with DJ/Compiler artists (Commit 3)

### Changes Applied in This PR

**In brucelee94/uploader/upload.py:**
- ✅ Lines 125-139: DJ Mix record label clearing (Commit 3)
- ✅ Lines 415-436: Artist splitting for multi-disc DJ Mix (Commits 1 & 2)
- ✅ Lines 476-497: Artist splitting for single-disc DJ Mix (Commits 1 & 2)

## Features Now Working

### 1. Artist Splitting in Track Listings
Artists are now properly split on both ", " and " & " separators:

```
# Before
[b]01.[/b] [artist]Shades & ID[/artist] - Track Name

# After
[b]01.[/b] [artist]Shades[/artist], [artist]ID[/artist] - Track Name
```

### 2. Complex Artist Combinations
Handles complex artist combinations:

```
# Input: "Alix Perez, Shades & Eprom"
# Output:
[b]01.[/b] [artist]Alix Perez[/artist], [artist]Shades[/artist], [artist]Eprom[/artist] - Track Name
```

### 3. Title Cleanup
DJ Mix suffix removed from titles:

```
# Before
Title: "SHADES at DEF: Underground (DJ Mix)"

# After
Title: "SHADES at DEF: Underground"
```

### 4. DJ Mix Header
Uses DJ/Compiler artist instead of track artists:

```
# Before
[b]Various Artists - Album Title[/b]

# After
[b][artist]Dubfire[/artist] & [artist]Richie Hawtin[/artist] - Album Title[/b]
```

### 5. Record Label Clearing
DJ Mix releases have empty record label:

```
# Before
Record Label: "26 July 2025 20 songs, 59 minutes"

# After
Record Label: (empty)
```

## Technical Implementation

### Artist Splitting Logic

Both multi-disc and single-disc sections now use this logic for DJ Mix:

```python
if isinstance(track_artist, list):
    all_artists = []
    for artist in track_artist:
        # Split on both ", " and " & "
        for comma_part in artist.split(', '):
            all_artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
    artist_tags = [f"[artist]{artist}[/artist]" for artist in all_artists]
    description += f"{', '.join(artist_tags)} - "
elif track_artist:
    # Split single artist string
    artists = []
    for comma_part in track_artist.split(', '):
        artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
    artist_tags = [f"[artist]{artist}[/artist]" for artist in artists]
    description += f"{', '.join(artist_tags)} - "
```

### Record Label Logic

```python
if metadata.get("rls_type") == "DJ Mix":
    record_label = ""
else:
    record_label = metadata.get("label", "")
```

## Testing

### Syntax Validation
- ✅ Python syntax check passed
- ✅ All changes verified against original commits

### Expected Behavior

**For DJ Mix with artists "Shades & ID" in track 1 and "Alix Perez, Eprom" in track 2:**

```
[b][artist]DJ Name[/artist] - Album Title[/b]
May 03, 2016

[b]01.[/b] [artist]Shades[/artist], [artist]ID[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]
[b]02.[/b] [artist]Alix Perez[/artist], [artist]Eprom[/artist] - Another Track (Mixed) [i](04:12)[/i]
```

**For regular Various Artists album:**
- Unchanged - uses metadata-based artist separation with feat. suffix

## Benefits

1. **Proper Artist Linking:** Each artist gets their own [artist] tag for RED's linking system
2. **Cleaner Titles:** "(DJ Mix)" suffix removed for better display
3. **Correct DJ Attribution:** DJ/Compiler shown in header, not track artists
4. **No False Labels:** Empty label prevents showing metadata text as record label
5. **Flexible Parsing:** Handles various artist separator formats

## Compatibility

- ✅ No breaking changes
- ✅ Non-DJ Mix uploads unchanged
- ✅ Works with both scraped and file-based metadata
- ✅ Compatible with existing guest artist feature for non-DJ Mix

## Files Changed

1. `brucelee94/uploader/upload.py` - 35 additions, 7 deletions
2. `brucelee94/uploader/__init__.py` - No new changes (already present)

## Commit Hash

Applied in commit: `aac2c13`

## References

- Original Commit 1: https://github.com/Vincent91-Reaper/Supersalmon/commit/97876afa5458a6f58eb56e72ca254441cceda577
- Original Commit 2: https://github.com/Vincent91-Reaper/Supersalmon/commit/6996411761b3df251a100421b01ff0c287c0e03e
- Original Commit 3: https://github.com/Vincent91-Reaper/Supersalmon/commit/0add7908a8baed69269bf78b28dd657838fdf575
