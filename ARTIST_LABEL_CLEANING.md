# Artist + Label Cleaning Feature

## Problem Statement

Some streaming services (Tidal, Qobuz, Deezer, Apple Music) tag albums with **both** the real artist name and the record label in the album artist field, separated by commas.

### Example

**Tidal Album:** https://tidal.com/album/467066754

```
Album artist: "Swoze, Former City Records"
Track artists: "Swoze" (consistent on all tracks)
Label: "Former City Records"
Folder: "Swoze, Former City Records - New Rims (2025) [WEB FLAC] [16-44.1]"
```

**The Problem:**
- Album artist should be just "Swoze"
- Folder name should be just "Swoze - New Rims..."
- Label should still be "Former City Records" for upload

---

## Solution

Detect when album artist contains both artist name and label, then:
1. **Remove the label** from album artist tags in files
2. **Rename the folder** to remove the label
3. **Preserve the label** for upload to RED

---

## Detection Logic

The `_detect_label_in_albumartist()` function checks 4 criteria:

### 1. Album Artist Has Multiple Parts
- Album artist contains commas
- Can be split into 2+ parts
- Example: "Swoze, Former City Records" → ["Swoze", "Former City Records"]

### 2. One Part Contains Label Keywords
- Check each part for keywords:
  - "records", "music", "entertainment", "label"
  - "recordings", "productions", "media", "group"
  - "collective", "imprint"
- Example: "Former City Records" has "Records" ✓

### 3. Album Has ONE Consistent Track Artist
- NOT a Various Artists compilation
- Fewer than 3 different track artists
- Example: All tracks by "Swoze" ✓

### 4. Track Artist Matches Non-Label Part
- The real artist part matches track artists
- Example: "Swoze" (album artist part) matches "Swoze" (track artist) ✓

**All 4 criteria must be met for detection.**

---

## Actions Taken

### 1. Clean Album Artist Tags

Remove the label from album artist in all files:

```python
Before: albumartist = "Swoze, Former City Records"
After:  albumartist = "Swoze"
```

### 2. Rename Folder

Update folder name to remove the label:

```
Before: Swoze, Former City Records - New Rims (2025) [WEB FLAC] [16-44.1]
After:  Swoze - New Rims (2025) [WEB FLAC] [16-44.1]
```

### 3. Preserve Label

Ensure label is set correctly for upload:

```python
metadata["label"] = "Former City Records"
```

---

## Example Flow

### Input (From Tidal)

```
Folder: Swoze, Former City Records - New Rims (2025) [WEB FLAC] [16-44.1]

File Tags:
  albumartist: "Swoze, Former City Records"
  Track 1 artist: "Swoze"
  Track 2 artist: "Swoze"
  Track 3 artist: "Swoze"

Metadata:
  label: "Former City Records"
```

### Detection Process

```
Step 1: Check for comma-separated parts
  "Swoze, Former City Records" → ["Swoze", "Former City Records"] ✓

Step 2: Find part with label keywords
  "Swoze" → No keywords
  "Former City Records" → Has "Records" ✓

Step 3: Check track artist count
  3 tracks, all by "Swoze" → Single artist (< 3 different) ✓

Step 4: Verify track artist matches
  Track artist "Swoze" matches album artist part "Swoze" ✓

→ DETECTED: Label to remove = "Former City Records"
```

### Output

```
Detected label in album artist: Swoze, Former City Records
Removing label 'Former City Records' from album artist...
New album artist: Swoze

Renamed folder:
  From: Swoze, Former City Records - New Rims (2025) [WEB FLAC] [16-44.1]
  To:   Swoze - New Rims (2025) [WEB FLAC] [16-44.1]

Label preserved for upload: Former City Records

Album artist cleaned successfully.
```

### Result

```
Folder: Swoze - New Rims (2025) [WEB FLAC] [16-44.1]

File Tags:
  albumartist: "Swoze"  ← CLEANED!
  Track 1 artist: "Swoze"  (unchanged)
  Track 2 artist: "Swoze"  (unchanged)
  Track 3 artist: "Swoze"  (unchanged)

Metadata:
  label: "Former City Records"  ← PRESERVED!

Upload to RED:
  Artist: Swoze
  Album: New Rims
  Label: Former City Records  ← CORRECT!
```

---

## Differences from Various Artists Case

### This Case (Artist + Label)

```
Album artist: "Swoze, Former City Records"
Track artists: ONE consistent artist ("Swoze")
Action: Remove label, keep artist name
Result: "Swoze - New Rims"
```

### Various Artists Case

```
Album artist: "Ed Banger Records"
Track artists: MULTIPLE different artists (Mr Oizo, Breakbot, etc.)
Action: Change to "Various Artists"
Result: "Various Artists - ED REC Vol.X"
```

### Comparison Table

| Aspect | Artist + Label | Various Artists |
|--------|----------------|-----------------|
| Album Artist | "Artist, Label" | "Label" |
| Track Artists | ONE consistent | MULTIPLE (3+) |
| Detection | Label in artist | Artist = Label |
| Action | Remove label | Change to VA |
| Result | Artist name | "Various Artists" |

---

## Order of Detection

The artist+label case is checked **BEFORE** the Various Artists case:

```python
# 1. FIRST: Check for artist+label case (NEW)
label_to_remove = _detect_label_in_albumartist(...)
if label_to_remove:
    # Clean and return

# 2. THEN: Check for Various Artists case (existing)
elif is_record_label_album(...):
    # Change to Various Artists
```

**Why this order?**
- Artist+label has fewer track artists (< 3)
- Various Artists requires 3+ track artists
- No conflict between the two cases

---

## Supported Sources

This feature works for:
- ✅ Tidal
- ✅ Qobuz
- ✅ Deezer
- ✅ Apple Music

(Any source that tags albums this way)

---

## Testing

### Test with Tidal Album

```bash
# Update brucelee94
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again

# Test with example album
bl94 up /path/to/album -su "https://tidal.com/album/467066754"
```

### Expected Results

1. ✅ Console shows: "Detected label in album artist: Swoze, Former City Records"
2. ✅ Console shows: "New album artist: Swoze"
3. ✅ Folder renamed to "Swoze - New Rims..."
4. ✅ Files have albumartist = "Swoze"
5. ✅ Upload shows label = "Former City Records"

### Verification Checklist

- [ ] Detection message shown
- [ ] Album artist cleaned in files
- [ ] Folder renamed correctly
- [ ] Label preserved for upload
- [ ] Upload succeeds with correct metadata

---

## Benefits

✅ **Correct artist names** - No label mixed with artist
✅ **Clean folder names** - Artist only, no label
✅ **Preserved label** - Upload shows correct label
✅ **Automatic** - No manual intervention needed
✅ **Universal** - Works for all streaming sources

---

## Summary

**Problem:** Album artist contains both artist name and label
**Detection:** 4 criteria (parts, keywords, single artist, match)
**Action:** Remove label from tags and folder, preserve for upload
**Result:** Clean artist name everywhere, correct label on RED

The feature automatically detects and cleans this common tagging issue from streaming services!
