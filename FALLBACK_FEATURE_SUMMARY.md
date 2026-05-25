# URL Scraping Fallback Feature - Summary

## Quick Overview

**Feature:** When URL scraping fails, users can now extract metadata from audio files instead (like Tidal/Deezer).

**Requirement Met:** ✅ Fallback mechanism for failed URL scraping

---

## What Happens Now

### Before (Problem)
```
Please provide a URL: https://play.qobuz.com/album/q98y2rlbn6u21
Scraping metadata from Qobuz...
Unexpected scrape error: name 'title' is not defined
Failed to scrape metadata from https://play.qobuz.com/album/q98y2rlbn6u21
URL not recognized or failed to scrape. Please try again.
[User is stuck - can't proceed]
```

### After (Solution)
```
Please provide a URL: https://play.qobuz.com/album/q98y2rlbn6u21
Scraping metadata from Qobuz...
Failed to scrape metadata from https://play.qobuz.com/album/q98y2rlbn6u21

Would you like to extract metadata from the audio files instead?
This works similar to Tidal/Deezer uploads.
Extract from files? ([y]es, [n]o, [a]bort): y

Extracting metadata from file tags...
[Upload continues with file-based metadata]
```

---

## User Options

When scraping fails:

| Option | Action | Result |
|--------|--------|--------|
| **[y]es** | Extract from files | Continue upload with file metadata |
| **[n]o** | Try different URL | Prompt for new URL |
| **[a]bort** | Cancel upload | Exit process |

---

## What Gets Extracted from Files

When user chooses to extract from files:

- ✅ Album artist(s)
- ✅ Album title
- ✅ Track titles
- ✅ Track artists (main and guest)
- ✅ Year and date
- ✅ Label
- ✅ Genres (if tagged)
- ✅ UPC/BARCODE (if tagged)
- ✅ Track/disc numbers
- ✅ ISRC codes (if tagged)

---

## Works For All Sources

Not just Qobuz! The fallback works for:

- ✅ Qobuz
- ✅ Beatport
- ✅ iTunes
- ✅ Apple Music
- ✅ Bandcamp
- ✅ Any other metadata source

**Any time scraping fails, for any reason, the fallback is available.**

---

## Why This Matters

### Common Failure Reasons
- Missing data in API responses
- API rate limits or authentication issues
- Network connectivity problems
- API changes or deprecations
- Incomplete album information

### Before This Fix
- User hits dead-end
- Can't proceed with upload
- Must abandon or find different source

### After This Fix
- User has recovery option
- Can complete upload anyway
- Uses accurate file metadata
- Same experience as Tidal/Deezer

---

## Technical Details

**Implementation:** `brucelee94/tagger/metadata.py` lines 182-202

**How it works:**
1. Scraping attempt fails
2. User prompted for fallback
3. If yes: Returns `{"_extract_from_files": True, "_source_url": url}`
4. Upload handler detects flag
5. Calls `_build_metadata_from_files()`
6. Continues normal upload flow

**Same mechanism as:**
- Tidal URLs (always extract from files)
- Deezer URLs (always extract from files)

---

## Bonus Fix

Also fixed Qobuz code bug:
- **Error:** `NameError: name 'title' is not defined`
- **Location:** `parse_release_type()` method
- **Fix:** Added `title = soup.get("title", "")` at start of method

This prevents crashes when processing Qobuz responses, even with missing data.

---

## Example Usage

### Scenario 1: User Accepts Fallback
```bash
# URL scraping fails
Failed to scrape metadata from https://...

# User is prompted
Extract from files? ([y]es, [n]o, [a]bort): y

# Continues with file extraction
Extracting metadata from file tags...
[Upload succeeds]
```

### Scenario 2: User Tries Different URL
```bash
# URL scraping fails
Failed to scrape metadata from https://qobuz.com/...

# User is prompted
Extract from files? ([y]es, [n]o, [a]bort): n

# Prompts for new URL
Please provide a URL: https://bandcamp.com/...
[Tries again with different source]
```

---

## Files Changed

### Code
- `brucelee94/tagger/metadata.py` - Fallback mechanism
- `brucelee94/tagger/sources/qobuz.py` - Bug fix

### Documentation
- `URL_SCRAPING_FALLBACK.md` - Complete guide
- `FALLBACK_FEATURE_SUMMARY.md` - This file

---

## Status

✅ **Feature Complete**
- Implementation tested
- Documentation complete
- Works for all sources
- User-friendly prompts
- Graceful error handling
- Ready for production

---

## For Users

**Bottom line:** If a URL fails to scrape (for any reason), you can now extract metadata from your audio files and continue uploading. No more dead-ends!

This works exactly like Tidal and Deezer uploads, which always use file-based metadata extraction.
