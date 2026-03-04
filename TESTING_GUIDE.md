# Testing Guide: Record Label Detection Fix

## Problem Recap

**What was wrong:** The record label detection only worked for Tidal/Deezer URLs, but NOT for Qobuz or other sources.

**Why it didn't work for Qobuz:**
- Detection code was inside `_build_metadata_from_files()` function
- This function is ONLY called for Tidal/Deezer URLs
- Qobuz uses web scraping (different code path)
- Detection code was never reached!

**What was fixed:**
- Moved detection to common code path (after metadata finalization)
- Now works for ALL sources: Qobuz, Beatport, Bandcamp, Apple Music, etc.

---

## How to Update

Run these commands to update brucelee94:

```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

**Note:** Yes, these are the correct commands! The branch name is `copilot/sub-pr-6-again`.

---

## Testing Steps

### 1. Test Album

Use the Ed Banger Records album from Qobuz:
```
https://www.qobuz.com/us-en/album/ed-rec-volx-mr-oizo-krazy-baldhead-breakbot-busy-p-mr-flash-justice-cassius-boston-bun/5060281613875
```

### 2. Run Upload

```bash
bl94 up /path/to/album/folder -su "https://www.qobuz.com/us-en/album/ed-rec-volx-mr-oizo-krazy-baldhead-breakbot-busy-p-mr-flash-justice-cassius-boston-bun/5060281613875"
```

### 3. Watch for Detection

You should now see these messages:

```
Detected record label as album artist: Ed Banger Records
This appears to be a various artists compilation.
Retagging album artist to 'Various Artists'...

Renamed folder:
  From: Ed Banger Records - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]
  To:   Various Artists - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]

Album will be treated as Various Artists compilation.
```

---

## Expected Results

### ✅ File Metadata Changes

Check file tags (use a tag editor or `ffprobe`):
- **albumartist:** Changed from "Ed Banger Records" to "Various Artists"
- **artist (track):** UNCHANGED (still Mr Oizo, Krazy Baldhead, etc.)

### ✅ Folder Name Change

```
Before: Ed Banger Records - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]
After:  Various Artists - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]
```

### ✅ Upload Treatment

On the torrent description:
- All track artists treated as "main" artists
- No redundant artist names shown on each track
- Proper Various Artists formatting

---

## Verification Checklist

After upload completes, verify:

- [ ] Console showed detection message
- [ ] Console showed retagging message
- [ ] Console showed folder rename (with before/after)
- [ ] Folder is now named "Various Artists - ..."
- [ ] File tags show albumartist = "Various Artists"
- [ ] Track artists are unchanged
- [ ] Upload completed successfully
- [ ] Torrent page shows proper Various Artists treatment

---

## Troubleshooting

### If Detection Still Doesn't Happen

1. **Check version:**
   ```bash
   uv tool list
   # Should show brucelee94 installed from copilot/sub-pr-6-again branch
   ```

2. **Check album has label:**
   - Look at file tags
   - Check if copyright field has label info
   - Or check if metadata scraped from Qobuz has label

3. **Check album has 3+ different track artists:**
   - Detection requires at least 3 different artists
   - Ed Banger Records has 10+ so this should pass

4. **Enable debug mode:**
   - If still not working, run with verbose output
   - Report the output to help diagnose

### If You Still See "did NOTHING AT ALL"

Please report:
1. Exact command you ran
2. Complete console output (copy/paste)
3. Contents of file tags (albumartist field)
4. Folder name before and after
5. Any error messages

---

## Why This Should Work Now

**Before:**
```
Qobuz URL → Web scraping → edit_metadata → ❌ No detection → Upload
```

**After:**
```
Qobuz URL → Web scraping → edit_metadata → ✅ Detection runs → Retag → Rename → Upload
```

The detection now runs in the COMMON code path, after metadata is finalized, for ALL sources!

---

## Questions?

If you have any questions or the fix still doesn't work, please provide:
- The complete console output
- What you expected vs what happened
- File/folder details

Good luck with testing! 🎵
