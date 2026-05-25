# Deezer Upload Guide

## Overview

Deezer uploads now work the same way as Tidal uploads - instead of scraping metadata from the Deezer URL, brucelee94 extracts metadata directly from your downloaded files. This is more reliable and preserves accurate information.

### What Changed

**Before:**
- Provided Deezer URL → brucelee94 tried to scrape metadata from website
- Scraping was unreliable and often failed
- Had to manually enter metadata on failures

**After:**
- Provided Deezer URL → brucelee94 detects it and skips scraping
- Extracts all metadata from your downloaded files
- Uses actual genre tags from Deezer files (not "electronic" fallback)
- More reliable and accurate

## How It Works

### Step-by-Step Workflow

1. **URL Detection**
   ```
   You provide: https://www.deezer.com/en/album/852049722
   brucelee94 detects: Deezer URL pattern
   Shows: "Deezer URL detected - skipping metadata scraping"
   ```

2. **Metadata Extraction**
   ```
   Shows: "Extracting metadata from file tags..."
   Reads from your downloaded FLAC files:
   - Artists (main vs guest classification)
   - Album title and edition
   - Year and full date
   - Label (from copyright field)
   - Genres (from file tags)
   - Track information
   - UPC/Barcode
   - Catalog number
   ```

3. **Genre Handling** (KEY DIFFERENCE FROM TIDAL)
   ```
   Deezer files have genre tags → uses actual genres
   Example: ["Electronic", "House"] → "electronic,house"
   
   Tidal files don't have genre tags → uses "electronic" fallback
   ```

4. **Upload Process**
   ```
   - Skips retagging (files already correct)
   - Skips edit metadata prompts
   - Runs folder structure check (genre-aware)
   - Generates torrent description
   - Uploads to RED
   ```

## Tidal vs Deezer Comparison

| Feature | Tidal | Deezer |
|---------|-------|--------|
| **Skip URL scraping** | ✅ Yes | ✅ Yes |
| **Extract from files** | ✅ Yes | ✅ Yes |
| **Has genre tags in files** | ❌ No | ✅ Yes |
| **Genre handling** | Fallback to "electronic" | Use actual genres |
| **Folder structure check** | Always runs | Genre-aware (only if needed) |
| **Skip retagging** | ✅ Yes | ✅ Yes |
| **Artist classification** | ✅ Main/Guest | ✅ Main/Guest |
| **Label extraction** | ✅ From copyright | ✅ From copyright |
| **DJ Mix detection** | ✅ Yes | ✅ Yes |
| **Various Artists handling** | ✅ Yes | ✅ Yes |

## Genre Handling Details

### Why It's Different

**Tidal:**
- Files downloaded from Tidal don't have genre tags
- `convert_genres([])` returns `"electronic"` as fallback
- Required to prevent RED upload failures
- Folder structure check always runs (no genre info)

**Deezer:**
- Files downloaded from Deezer DO have genre tags
- `convert_genres(["Electronic", "House"])` returns `"electronic,house"`
- Uses actual genres from the files
- Folder structure check uses genre info (more intelligent)

### Example

**Deezer file tags:**
```
Genre: Electronic
Genre: House
```

**Upload to RED:**
```
Genres: electronic,house
```

**NOT:**
```
Genres: electronic  (This would be the Tidal behavior)
```

## Example Workflow

### User Input
```bash
bl94 up "/path/to/Taylor Swift - The Life of a Showgirl + Acoustic Collection (2025) [WEB FLAC] [16-44.1]" \
  -s Deezer \
  -su "https://www.deezer.com/en/album/852049722"
```

### Expected Output
```
Processing /path/to/Taylor Swift - The Life of a Showgirl...

Please provide a URL to scrape metadata from (or [m]anual, [a]bort): https://www.deezer.com/en/album/852049722
Deezer URL detected - skipping metadata scraping
Extracting metadata from file tags...

[Builds metadata from files...]

Album: The Life of a Showgirl + Acoustic Collection
Artist: Taylor Swift
Year: 2025
Label: Republic Records
Genres: pop,country
Tracks: 16

[Continues with upload process...]
```

### What Gets Extracted

From your downloaded Deezer files, brucelee94 extracts:

1. **Artists**
   - Album artists from `albumartist` tag
   - Track artists from `artist` tag
   - Classifies as "main" or "guest" based on album artist list

2. **Album Info**
   - Title from `album` tag
   - Edition (if part of title, e.g., "Deluxe Edition")
   - Year from `date` or `recordingdate` tag

3. **Label**
   - From `copyright` tag (preferred)
   - Falls back to `label` tag
   - Detects "Self-Released" for artist-owned labels

4. **Genres**
   - From `genre` tag (this is the key difference!)
   - Preserves actual Deezer genres

5. **Track Info**
   - Track numbers and disc numbers
   - Track titles
   - Track artists

6. **Catalog Info**
   - UPC/Barcode
   - Catalog number (if present)

## Benefits

### 1. More Reliable
- No dependency on Deezer website scraping
- Works even if Deezer changes their website
- No more "failed to scrape" errors

### 2. More Accurate
- Uses metadata directly from your files
- Preserves exact artist names and roles
- Correct label information from copyright tags

### 3. Genre Aware
- Uses actual genres from Deezer files
- Better compliance with RED genre requirements
- More accurate genre classification

### 4. Faster
- Skips scraping step
- Skips retagging workflow
- Fewer prompts and confirmations

### 5. More Control
- See exactly what metadata is being used
- Metadata comes from your files (what you're uploading)
- Consistent with other upload sources

## Testing Instructions

### How to Verify It Works

1. **Download Deezer album** (with dl-deezer or similar)

2. **Run brucelee94 with Deezer URL:**
   ```bash
   bl94 up /path/to/album -s Deezer -su "https://www.deezer.com/en/album/ALBUM_ID"
   ```

3. **Check for these messages:**
   ```
   ✓ "Deezer URL detected - skipping metadata scraping"
   ✓ "Extracting metadata from file tags..."
   ```

4. **Verify metadata is correct:**
   - Album title matches your files
   - Artists are correctly classified
   - Year is correct
   - Label is correct
   - **Genres match your file tags** (not just "electronic")

5. **Check torrent description:**
   - Genres should be from your files (e.g., "pop,country")
   - Not just "electronic" (unless that's the actual genre)

### Example Test

**File to test with:**
```
Taylor Swift - The Life of a Showgirl + Acoustic Collection (2025) [WEB FLAC]
URL: https://www.deezer.com/en/album/852049722
```

**Expected genres:**
- From files: Pop, Country
- In description: pop,country
- NOT: electronic

## Troubleshooting

### Issue: "Failed to scrape metadata"
**Solution:** Make sure you're using the full album URL, not a track URL.
```
✓ Correct: https://www.deezer.com/en/album/852049722
✗ Wrong: https://www.deezer.com/en/track/123456789
```

### Issue: All genres show as "electronic"
**Cause:** Your files don't have genre tags.
**Solution:** Check your files with a tag editor. Deezer files should have genre tags. If they don't, you may need to re-download or manually add genre tags.

### Issue: Artists are classified wrong (all main or all guest)
**Cause:** Album artist tags might be missing or incorrect.
**Solution:** Check the `albumartist` tag in your files. It should contain the main album artists. Track artists not in `albumartist` will be classified as guests.

### Issue: Label shows as artist name instead of actual label
**This is intentional:** When the label matches the artist name, brucelee94 changes it to "Self-Released" to comply with RED rules.
```
Artist: Taylor Swift
Copyright: Taylor Swift
→ Label: Self-Released
```

### Issue: Folder structure check keeps prompting
**Cause:** Files have long paths (>180 chars) or is classical music.
**Solution:** This is normal. Follow the prompts to rename files/folders to comply with RED path length requirements.

## Summary

✅ **Deezer uploads now work like Tidal uploads**
- Skip unreliable web scraping
- Extract metadata from downloaded files
- More reliable and accurate

✅ **BUT with proper genre handling**
- Deezer files have genre tags → uses them
- Tidal files don't have genre tags → uses "electronic" fallback
- Better compliance with RED requirements

✅ **All other Tidal rules apply**
- Skip retagging workflow
- Intelligent artist classification
- Label extraction from copyright
- DJ Mix detection
- Various Artists handling

**Result:** More reliable Deezer uploads with accurate genre information!
