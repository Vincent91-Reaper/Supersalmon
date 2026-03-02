# Automatic Fallback Feature

## Overview

When URL scraping fails, brucelee94 now **automatically** extracts metadata from audio files without prompting the user.

## Behavior

### Before (with prompt)
```
Failed to scrape metadata from <URL>

Would you like to extract metadata from the audio files instead?
This works similar to Tidal/Deezer uploads.
Extract from files? ([y]es, [n]o, [a]bort): _
[Wait for user input]
```

### After (automatic)
```
Failed to scrape metadata from <URL>

Automatically extracting metadata from audio files...
(Similar to Tidal/Deezer uploads)
[Continues immediately]
```

## Benefits

- ✅ **Faster workflow** - No waiting for user input
- ✅ **Seamless** - Automatic recovery
- ✅ **Consistent** - Like Tidal/Deezer
- ✅ **Simpler** - No decisions to make

## User Control

Users can still **abort** at any time by pressing **Ctrl+C**.

## Example

```
Please provide a URL: https://play.qobuz.com/album/q98y2rlbn6u21

Scraping metadata from Qobuz...
Failed to scrape metadata from https://play.qobuz.com/album/q98y2rlbn6u21

Automatically extracting metadata from audio files...
(Similar to Tidal/Deezer uploads)

[Extraction continues]
[Upload proceeds]
```

## Technical Details

- **File:** `brucelee94/tagger/metadata.py`
- **Lines:** 182-195
- **Implementation:** Automatic return of `_extract_from_files` flag
- **Code reduction:** 12 lines removed (simpler code)

## Works For

- Qobuz (missing data)
- Beatport (API issues)
- iTunes (network problems)
- Any metadata source failure

---

**The fallback is now fully automatic - no user interaction required!**
