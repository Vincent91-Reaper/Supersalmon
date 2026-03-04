# Record Label Detection and Various Artists Conversion

## Problem

Streaming services (Tidal, Deezer, Qobuz, Apple Music) sometimes incorrectly tag a record label name as the album artist for various artists compilations, instead of using "Various Artists".

### Example: Qobuz War Child Records Album

**URL:** https://www.qobuz.com/us-en/album/help2-war-child-records/naszhk00bfnly

**Issue:**
- Album artist: "War Child Records" (record label)
- Track artists: Arctic Monkeys, Damon Albarn, Coldplay, etc. (various different artists)
- Should be: Album artist "Various Artists"

**Consequences:**
1. Wrong album artist in file metadata
2. Wrong folder name ("War Child Records - ..." instead of "Various Artists - ...")
3. Upload doesn't properly treat it as a Various Artists compilation
4. All track artists shown redundantly on every track

---

## Solution

Brucelee94 now automatically detects when a record label is tagged as the album artist and corrects it:

1. **Detects** record label albums using smart criteria
2. **Retags** all files' albumartist field to "Various Artists"
3. **Renames** folder from "Record Label - Album..." to "Various Artists - Album..."
4. **Applies** proper Various Artists treatment for uploads

All **completely automatic** - no user action needed!

---

## How Detection Works

### Detection Criteria (All Three Must Be Met)

**1. Label Keyword Check**
- Album artist name contains keywords indicating a record label:
  - "Records"
  - "Music"
  - "Entertainment"
  - "Label"
  - "Recordings"
  - "Productions"

**2. Multiple Artists Check**
- Album has **3 or more** different track artists
- Indicates a compilation, not a single artist album

**3. Name Mismatch Check**
- **None** of the track artist names match the album artist name
- If a track artist matches, it's probably a real artist, not a label

### Detection Logic

```python
def _is_record_label_album(albumartist, track_artists_list):
    # Check 1: Contains label keywords?
    if not any(keyword in albumartist.lower() for keyword in label_keywords):
        return False  # Not a label
    
    # Check 2: Has 3+ different track artists?
    if len(track_artists_list) < 3:
        return False  # Not enough variety
    
    # Check 3: Any track artist matches album artist?
    for track_artist in track_artists_list:
        if albumartist.lower() in track_artist.lower():
            return False  # Real artist, not label
    
    return True  # All criteria met - it's a record label album!
```

---

## What Gets Changed

### 1. File Metadata (Retagging)

**Function:** `_retag_albumartist_to_various_artists(tags)`

Changes every file's `albumartist` field:
- **Before:** "War Child Records"
- **After:** "Various Artists"

Track artists remain **unchanged** (Arctic Monkeys, Damon Albarn, etc.)

### 2. Folder Name (Renaming)

**Function:** `_rename_folder_with_various_artists(path)`

Renames the folder:
- **Before:** `War Child Records - HELP(2) (2026) [WEB FLAC] [24-96]`
- **After:** `Various Artists - HELP(2) (2026) [WEB FLAC] [24-96]`

### 3. Upload Treatment

Clears `album_artists_set` so all track artists are treated as **"main" artists**, not "guest" artists. This triggers the existing Various Artists handling logic.

---

## Example Flow

### Input

```
Folder: War Child Records - HELP(2) (2026) [WEB FLAC] [24-96]

File Metadata:
  albumartist: War Child Records
  Track 1 artist: Arctic Monkeys
  Track 2 artist: Damon Albarn
  Track 3 artist: Coldplay
  Track 4 artist: Radiohead
  ... (multiple different artists)
```

### Detection Process

```
Step 1: Check album artist "War Child Records"
  ✓ Contains "Records" → Label keyword found

Step 2: Count unique track artists
  ✓ 4+ different artists → Multiple artists confirmed

Step 3: Check for name matches
  ✓ "Arctic Monkeys" ≠ "War Child Records"
  ✓ "Damon Albarn" ≠ "War Child Records"
  ✓ "Coldplay" ≠ "War Child Records"
  ✓ No track artist matches album artist

→ DETECTED: Record label album!
```

### Console Output

```
Detected record label as album artist: War Child Records
This appears to be a various artists compilation.
Retagging album artist to 'Various Artists'...

Renamed folder:
  From: War Child Records - HELP(2) (2026) [WEB FLAC] [24-96]
  To:   Various Artists - HELP(2) (2026) [WEB FLAC] [24-96]

Album will be treated as Various Artists compilation.
```

### Output

```
Folder: Various Artists - HELP(2) (2026) [WEB FLAC] [24-96]

File Metadata (updated):
  albumartist: Various Artists  ← CHANGED
  Track 1 artist: Arctic Monkeys  ← UNCHANGED
  Track 2 artist: Damon Albarn  ← UNCHANGED
  Track 3 artist: Coldplay  ← UNCHANGED
  Track 4 artist: Radiohead  ← UNCHANGED

Upload Treatment:
  - All track artists = main artists
  - Proper Various Artists handling
  - Correct metadata on RED
```

---

## Before vs After Comparison

### Before Fix

**Folder:**
```
War Child Records - HELP(2) (2026) [WEB FLAC] [24-96]
```

**File Tags:**
```
albumartist: War Child Records
Track 1: Arctic Monkeys - There'd Better Be A Mirrorball
Track 2: Damon Albarn - Royal Morning Blue
Track 3: Coldplay - All My Love
```

**Upload (Torrent Description):**
```
Album Artist: War Child Records
Track List:
  01. Arctic Monkeys - There'd Better Be A Mirrorball
  02. Damon Albarn - Royal Morning Blue
  03. Coldplay - All My Love
  
(Shows artist on every track - redundant and cluttered)
```

### After Fix

**Folder:**
```
Various Artists - HELP(2) (2026) [WEB FLAC] [24-96]
```

**File Tags:**
```
albumartist: Various Artists  ← FIXED
Track 1: Arctic Monkeys - There'd Better Be A Mirrorball
Track 2: Damon Albarn - Royal Morning Blue
Track 3: Coldplay - All My Love
```

**Upload (Torrent Description):**
```
Artists: Arctic Monkeys, Damon Albarn, Coldplay, ... (Various Artists)
Track List:
  01. There'd Better Be A Mirrorball
  02. Royal Morning Blue
  03. All My Love
  
(No artist shown per track - proper Various Artists treatment)
```

---

## Detection Examples

### Will Detect ✓

1. **"War Child Records"** with Arctic Monkeys, Coldplay, Radiohead
   - ✓ Contains "Records"
   - ✓ 3+ different artists
   - ✓ No name match

2. **"Parlophone Music"** with various different artists
   - ✓ Contains "Music"
   - ✓ Multiple artists
   - ✓ No overlap

3. **"Universal Entertainment"** with 5 different artists
   - ✓ Contains "Entertainment"
   - ✓ Many artists
   - ✓ No match

### Will NOT Detect ✗

1. **"Taylor Swift"** with Taylor Swift on all tracks
   - ✓ No label keywords
   - ✗ Not a label name

2. **"Sony Music"** with only 1-2 artists
   - ✓ Contains "Music"
   - ✗ Not enough variety (< 3 artists)

3. **"Atlantic Records"** if track artist is "Atlantic Records Band"
   - ✓ Contains "Records"
   - ✓ Multiple artists
   - ✗ Track artist name matches! (probably a real band name)

4. **"Various Artists"** (already correct)
   - ✗ Skipped explicitly
   - No change needed

---

## Technical Details

### Three Main Functions

**1. Detection: `_is_record_label_album(albumartist, track_artists_list)`**

```python
def _is_record_label_album(albumartist, track_artists_list):
    """
    Detect if album artist is a record label for a various artists album.
    
    Returns: Boolean indicating if this is a record label album
    """
    # Check for label keywords
    label_keywords = ['records', 'music', 'entertainment', 'label', 'recordings', 'productions']
    has_label_keyword = any(keyword in albumartist.lower() for keyword in label_keywords)
    
    # Check for multiple artists (3+)
    has_multiple_artists = len(track_artists_list) >= 3
    
    # Check for name mismatch (no track artist matches album artist)
    has_no_match = all(
        albumartist.lower() not in track_artist.lower() and 
        track_artist.lower() not in albumartist.lower()
        for track_artist in track_artists_list
    )
    
    return has_label_keyword and has_multiple_artists and has_no_match
```

**2. Retagging: `_retag_albumartist_to_various_artists(tags)`**

```python
def _retag_albumartist_to_various_artists(tags):
    """
    Retag all files' albumartist field to "Various Artists".
    """
    for filename, tagset in tags.items():
        tagset.albumartist = "Various Artists"
        tagset.save()  # Save changes to file
```

**3. Renaming: `_rename_folder_with_various_artists(path)`**

```python
def _rename_folder_with_various_artists(path):
    """
    Rename folder from "Record Label - Album..." to "Various Artists - Album..."
    
    Returns: New folder path
    """
    basename = os.path.basename(path)
    parent_dir = os.path.dirname(path)
    
    # Match pattern: "Artist - Album..."
    pattern = r"^(.+?)\s+-\s+(.+)$"
    match = re.match(pattern, basename)
    
    if match:
        new_basename = f"Various Artists - {match.group(2)}"
        new_path = os.path.join(parent_dir, new_basename)
        os.rename(path, new_path)
        return new_path
    
    return path
```

### Integration

Called in `_build_metadata_from_files()` after extracting album artists but before processing tracks:

```python
# After first pass (extracting album artists):
# Pre-scan all track artists
track_artists_for_detection = set()
for filename, tagset in tags.items():
    # ... extract all track artists ...
    track_artists_for_detection.add(artist)

# Detect record label album
is_record_label_album = _is_record_label_album(original_albumartist, list(track_artists_for_detection))

if is_record_label_album:
    # Show messages
    # Retag files
    # Rename folder
    # Clear album_artists_set (triggers Various Artists treatment)
```

---

## User Experience

### What Users See

```
Extracting metadata from file tags...

[If record label detected:]
Detected record label as album artist: War Child Records
This appears to be a various artists compilation.
Retagging album artist to 'Various Artists'...

Renamed folder:
  From: War Child Records - HELP(2) (2026) [WEB FLAC] [24-96]
  To:   Various Artists - HELP(2) (2026) [WEB FLAC] [24-96]

Album will be treated as Various Artists compilation.

[Continue with normal upload process...]
```

### What Users Don't Need to Do

- ✗ No manual file retagging
- ✗ No manual folder renaming
- ✗ No configuration needed
- ✗ No choices to make

**It just works automatically!** ✨

---

## Benefits

### For Users

✅ **Automatic** - No manual intervention needed
✅ **Accurate** - Smart detection prevents false positives
✅ **Complete** - Handles files, folder, and upload
✅ **Seamless** - Clear messages, smooth workflow

### For Uploads

✅ **Correct metadata** - "Various Artists" instead of record label
✅ **Proper treatment** - All track artists recognized as main artists
✅ **Better descriptions** - Clean track lists without redundant artists
✅ **RED compliance** - Follows Various Artists conventions

---

## Testing

### Test Case: Qobuz War Child Records

**Steps:**
1. Download album from Qobuz: https://www.qobuz.com/us-en/album/help2-war-child-records/naszhk00bfnly
2. Files will have albumartist = "War Child Records"
3. Run brucelee94 upload
4. Should detect record label
5. Should retag to "Various Artists"
6. Should rename folder
7. Should upload with proper Various Artists treatment

**Expected Results:**
- ✓ Detection message shown
- ✓ Files retagged to "Various Artists"
- ✓ Folder renamed to "Various Artists - ..."
- ✓ Upload treats all track artists as main
- ✓ Clean track list on RED

### Test Case: False Positive Prevention

**Scenario:** Album by "Atlantic Records Band" (hypothetical band name)
**Expected:** Should NOT detect as record label because track artist name matches album artist

---

## Summary

**TL;DR:**

When streaming services incorrectly tag a record label as the album artist (e.g., "War Child Records" instead of "Various Artists"), brucelee94 now automatically:

1. ✓ Detects it using smart criteria
2. ✓ Retags all files to "Various Artists"
3. ✓ Renames folder appropriately
4. ✓ Applies proper Various Artists upload treatment

No user action needed - completely automatic! 🎉
