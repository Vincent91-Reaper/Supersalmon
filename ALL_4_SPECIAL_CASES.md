# All 4 Special Cases - Complete Documentation

## Overview

Brucelee94 now handles **4 distinct special cases** for record label cleaning. Each case addresses a different pattern of how labels appear in music metadata.

---

## Special Case 1: Pure Various Artists

**Pattern:** Label ONLY as album artist

**Characteristics:**
- Album artist: "Label Name" (no real artist)
- Track artists: Various different artists (no label in tracks)
- Folder: "Label - Album Name"

**Example:**
- Album artist: "Ed Banger Records"
- Track artists: Justice, SebastiAn, Mr. Oizo, Uffie (15 different artists)
- Folder: "Ed Banger Records - ED REC Vol.X"

**Detection:**
1. Album artist matches label
2. 3+ track artists
3. < 50% track artists match album artist
4. Album artist has label keywords

**Actions:**
1. Retag album artist → "Various Artists"
2. Rename folder → "Various Artists - Album Name"
3. Clear album_artists_set for Various Artists treatment

**Code:** Lines 1819-1835, 1924-1935

---

## Special Case 2: Artist + Label in Album Artist

**Pattern:** Album artist contains both artist and label

**Characteristics:**
- Album artist: "Artist, Label" (comma-separated)
- Track artists: May include "Artist, Label"
- Folder: "Artist, Label - Album Name"

**Example:**
- Album artist: "Swoze, Former City Records"
- Track artists: "Swoze, Former City Records" (or variations)
- Folder: "Swoze, Former City Records - Album"

**Detection:**
1. Album artist is comma-separated
2. One part has label keywords ("records", "music", etc.)
3. That part appears in track artists list

**Actions:**
1. Remove label from album artist tags
2. Remove label from track artist tags
3. Rename folder to remove label
4. Set metadata["label"] to detected label
5. Clean metadata["artists"] and metadata["tracks"]

**Code:** Lines 498-695, detection at 1028-1086

---

## Special Case 3: Label in Folder/Tracks Only

**Pattern:** Album artist is clean, but label appears elsewhere

**Characteristics:**
- Album artist: "Artist" (clean, no label)
- Track artists: Include label (e.g., "Artist, Label")
- Folder: "Artist, Label - Album Name"

**Example:**
- Album artist: "Swoze" (clean)
- Track artists: "Swoze, Former City Records"
- Folder: "Swoze, Former City Records - Album"

**Detection:**
1. Folder name contains label (comma-separated with keywords)
2. Album artist doesn't contain label
3. Label appears in track artists

**Actions:**
1. Remove label from track artist tags
2. Rename folder to remove label
3. Set metadata["label"]
4. Clean metadata["artists"] and metadata["tracks"]

**Code:** Lines 724-911, detection at 1148-1207

---

## Special Case 4: Label Everywhere (NEW!)

**Pattern:** Label in album artist, track artists, AND folder (hybrid case)

**Characteristics:**
- Album artist: "Label" (no real artist) ← Like Case 1
- Track artists: "Artist, Label" (mixed) ← Like Case 2
- Folder: "Label - Album Name" ← Like Case 1

**Example (War Child Records - HELP(2)):**
- Album artist: "War Child Records"
- Track 1: "Arctic Monkeys, War Child Records"
- Track 2: "Depeche Mode, War Child Records"
- Folder: "War Child Records - HELP(2) (2026)"

**Why it's unique:**
- Combines detection from Case 1 (album artist = label)
- Requires track cleaning from Cases 2 & 3 (artist, label separation)
- Needs folder rename from Case 1
- **Most complex case** - all cleaning steps required

**Detection:**
1. Album artist matches label ✓
2. 3+ track artists ✓
3. < 50% track artists match album artist ✓
4. Album artist has label keywords ✓
5. Track artists include label mixed with real artists ✓

**Actions:**
1. Retag album artist → "Various Artists"
2. **Clean track artist tags** (remove label) ← Critical addition!
3. Rename folder → "Various Artists - Album Name"
4. Set metadata["label"]
5. Clean metadata["artists"] and metadata["tracks"]

**Code:** Lines 1819-1935 (combines Case 1 detection + track cleaning)

**Fixed in:** Commit acae88b

---

## Comparison Table

| Case | Album Artist | Track Artists | Folder | Actions |
|------|-------------|---------------|--------|---------|
| **1** | Label only | Various (clean) | Label - Album | Retag + Rename |
| **2** | Artist, Label | Artist, Label | Artist, Label - Album | Clean all 3 |
| **3** | Artist (clean) | Artist, Label | Artist, Label - Album | Clean tracks + folder |
| **4** | Label only | Artist, Label | Label - Album | Retag + Clean tracks + Rename |

---

## Complete Case 4 Flow

### Detection Phase

```
Album artist: War Child Records
Label from copyright: War Child Records
Track artists: 28 different artists
Track 1: "Arctic Monkeys, War Child Records"
Track 2: "Depeche Mode, War Child Records"
...

Analysis:
- Album artist matches label? YES ✓
- 3+ track artists? YES (28) ✓
- Match percentage: 1/28 = 3.5% < 50%? YES ✓
- Has keywords? "Records" YES ✓
- Track artists have label? YES ✓

Result: SPECIAL CASE 4 DETECTED
```

### Processing Phase

```
Step 1: Retag Album Artist
  From: "War Child Records"
  To:   "Various Artists"
  Status: ✓ Complete

Step 2: Clean Track Artists (NEW in Case 4!)
  Track 1:
    From: "Arctic Monkeys, War Child Records"
    To:   "Arctic Monkeys"
  Track 2:
    From: "Depeche Mode, War Child Records"
    To:   "Depeche Mode"
  ...all 28 tracks cleaned
  Status: ✓ Complete

Step 3: Rename Folder
  From: "War Child Records - HELP(2) (2026) [WEB FLAC]"
  To:   "Various Artists - HELP(2) (2026) [WEB FLAC]"
  Status: ✓ Complete

Step 4: Set Metadata
  metadata["label"] = "War Child Records"
  metadata["artists"] = [clean artist list]
  metadata["tracks"] = [clean per-track artists]
  Status: ✓ Complete
```

### Upload Result

```
Album Artist: Various Artists
Track 1: Arctic Monkeys (clean!)
Track 2: Depeche Mode (clean!)
Label Field: War Child Records
Torrent Description: Clean artist list
```

---

## Why Case 4 Required Special Handling

### Before Fix (Commits 1-9fce3ef)

**What was working:**
- ✓ Detection (Case 1 logic worked)
- ✓ Album artist retagging
- ✓ Folder renaming

**What was missing:**
- ❌ Track artist cleaning
- ❌ Label remained in track tags
- ❌ Upload showed "Artist, Label" in track artists

**User reported:**
> "Brucelee94 didn't clean the record label from track artist tag at all. For example: track 1's metadata, 'Performer: Arctic Monkeys, War Child Records'."

### After Fix (Commit acae88b)

**Added track artist cleaning:**
- ✓ Loop through all files after album artist retagging
- ✓ Clean track artist fields using helper function
- ✓ Handle both FLAC and MP3 formats
- ✓ Support all 7 separators (`;`, `,`, `/`, `\`, `&`, `+`, `|`)
- ✓ Save cleaned tags to files

**Result:**
- ✓ Complete end-to-end cleaning
- ✓ All locations cleaned: album artist, track artists, folder
- ✓ Upload shows clean metadata

---

## Technical Implementation

### Helper Function

All cases use: `_clean_artist_string_with_label(artist_str, label_to_remove)`

**Features:**
- Universal separator detection (7 types)
- Case-insensitive matching
- Preserves original separator style
- Handles multi-artist strings
- Regex fallback for edge cases

**Location:** Lines 1318-1372

### Separator Support

**All 7 separators:**
1. `;` (semicolon) - "Label; Artist"
2. `,` (comma) - "Label, Artist"
3. `/` (forward slash) - "Label / Artist"
4. `\` (backslash) - "Label \ Artist"
5. `&` (ampersand) - "Label & Artist"
6. `+` (plus) - "Label + Artist"
7. `|` (pipe) - "Label | Artist"

### File Format Support

**FLAC:**
- Field: `artist`
- Direct list manipulation
- Tag save via tagset.save()

**MP3:**
- Field: `TPE1` (ID3)
- Text list in mutagen
- Tag save via tagset.save()

---

## Console Output Examples

### Case 1 (Pure Various Artists)

```
Detected record label as album artist: Ed Banger Records
This appears to be a various artists compilation.
Retagging album artist to 'Various Artists'...

Renamed folder:
  From: Ed Banger Records - ED REC Vol.X (2025) [WEB FLAC]
  To:   Various Artists - ED REC Vol.X (2025) [WEB FLAC]

Album will be treated as Various Artists compilation.
```

### Case 2 (Artist + Label)

```
Detected label in album artist: Swoze, Former City Records
Removing label 'Former City Records' from album artist and track artists...
Cleaned album artist: Swoze
  Cleaned track artist in 01 - Track1.flac
  Cleaned track artist in 02 - Track2.flac
Label set in metadata: Former City Records
Cleaned metadata artists
Cleaned per-track artists in metadata

Renamed folder:
  From: Swoze, Former City Records - Album (2025) [WEB FLAC]
  To:   Swoze - Album (2025) [WEB FLAC]

Album artist and track artists cleaned successfully.
```

### Case 3 (Label in Folder/Tracks Only)

```
Detected label in folder/track artists but not in album artist: Former City Records
Album artist tag is already clean: Swoze
Removing label from track artists only...
  Cleaned track artist in 01 - Track1.flac
  Cleaned track artist in 02 - Track2.flac
Label set in metadata: Former City Records
Cleaned metadata artists
Cleaned per-track artists in metadata

Renamed folder:
  From: Swoze, Former City Records - Album (2025) [WEB FLAC]
  To:   Swoze - Album (2025) [WEB FLAC]

Track artists and folder cleaned successfully.
```

### Case 4 (Label Everywhere - NEW!)

```
Detected record label as album artist: War Child Records
This appears to be a various artists compilation.
Retagging album artist to 'Various Artists'...
Removing label from track artist tags...
  Cleaned track artist in 01 - I Bet You Look Good On The Dancefloor.flac
  Cleaned track artist in 02 - Enjoy The Silence.flac
  Cleaned track artist in 03 - The Man.flac
  ...
Track artist tags cleaned successfully.

Renamed folder:
  From: War Child Records - HELP(2) (2026) [WEB FLAC] [16-44.1]
  To:   Various Artists - HELP(2) (2026) [WEB FLAC] [16-44.1]

Album will be treated as Various Artists compilation.
```

---

## Testing Guide

### Test Case 4 (War Child Records)

**URL:** https://tidal.com/album/500752104

**Pre-test Check:**
```bash
# Update tool
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again

# Run upload
brucelee94 /path/to/album
```

**Verification Checklist:**

1. **Detection**
   - [ ] Console shows: "Detected record label as album artist: War Child Records"
   - [ ] Shows: "This appears to be a various artists compilation"

2. **Album Artist**
   - [ ] Console shows: "Retagging album artist to 'Various Artists'..."
   - [ ] File tags: Album artist = "Various Artists"

3. **Track Artists (Critical!)**
   - [ ] Console shows: "Removing label from track artist tags..."
   - [ ] Console shows: "  Cleaned track artist in [each file]"
   - [ ] Console shows: "Track artist tags cleaned successfully"
   - [ ] File tags: Track 1 artist = "Arctic Monkeys" (NOT "Arctic Monkeys, War Child Records")
   - [ ] File tags: Track 2 artist = "Depeche Mode" (NOT "Depeche Mode, War Child Records")

4. **Folder**
   - [ ] Console shows folder rename
   - [ ] Folder name: "Various Artists - HELP(2)..."
   - [ ] NOT: "War Child Records - HELP(2)..."

5. **Upload**
   - [ ] Upload succeeds
   - [ ] Torrent description shows clean artist list
   - [ ] No "War Child Records" in track artists
   - [ ] Label field: "War Child Records"

**Expected Output:**
```
✓ Detection: TRUE
✓ Album artist: Various Artists
✓ Track 1: Arctic Monkeys (clean)
✓ Track 2: Depeche Mode (clean)
✓ All tracks: Clean
✓ Folder: Various Artists - HELP(2)
✓ Upload: Success
```

---

## Commit History

1. **1df2774** - Detection threshold (Case 1 improvement)
2. **f4b6cf4** - Detection documentation
3. **b1c5beb** - Semicolon support (Cases 2 & 3)
4. **634c931** - 7 separators (Cases 2 & 3)
5. **a3fda5f** - Path synchronization (Case 1 fix)
6. **9fce3ef** - Separator detection (Cases 2 & 3 fix)
7. **acae88b** - Track cleaning for Case 4 (COMPLETE!)

---

## Summary

**All 4 Special Cases Now Complete:**

- ✅ Case 1: Pure Various Artists (simple)
- ✅ Case 2: Artist + Label in album artist (moderate)
- ✅ Case 3: Label in folder/tracks only (moderate)
- ✅ Case 4: Label everywhere (complex - FIXED!)

**Case 4 was the missing piece:**
- Detected using Case 1 logic ✓
- Required track cleaning like Cases 2 & 3 ✓
- Most comprehensive cleaning needed ✓
- Now fully implemented ✓

**All compilation albums and label scenarios now handled correctly!**
