# Debug Testing Guide for Record Label Detection

## Problem

The record label detection isn't working for the Ed Banger Records album from Qobuz. We've added debug output to diagnose the issue.

## Update to Debug Version

```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

## Run the Test

Upload the Ed Banger Records album again:

```bash
bl94 up "/path/to/Ed Banger Records - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]" -su "https://www.qobuz.com/us-en/album/ed-rec-volx-mr-oizo-krazy-baldhead-breakbot-busy-p-mr-flash-justice-cassius-boston-bun/5060281613875"
```

## What to Look For

After the "Retagging files..." message, you should see purple/magenta **[DEBUG]** messages. These will help us understand why detection isn't working.

### Expected Debug Output

```
Retagging files...
Retagged X file(s) with correct artist tags from scraped metadata.

[DEBUG] Starting record label detection...
[DEBUG] Album artist from tags: <value>
[DEBUG] Label from metadata: <value>
[DEBUG] Final extracted label: <value>
[DEBUG] Track artists found: <count> - [list of artists]
[DEBUG] Calling detection function...
[DEBUG] Detection result: <True/False>
```

## Debug Message Meanings

### 1. `[DEBUG] Starting record label detection...`
This confirms the detection code is running.

### 2. `[DEBUG] Album artist from tags: <value>`
Shows what album artist was extracted from the file tags. Should show "Ed Banger Records".

**If shows "None"**: Tags don't have albumartist field set yet.

### 3. `[DEBUG] Label from metadata: <value>`
Shows what label was in the scraped metadata from Qobuz. 

**If shows "None"**: Qobuz metadata doesn't include label field, will try copyright field next.

### 4. `[DEBUG] Final extracted label: <value>`
Shows the final label after trying copyright field extraction.

**If shows "None"**: Couldn't extract label from anywhere - this is the problem!

### 5. `[DEBUG] Track artists found: <count> - [list]`
Shows how many unique track artists were found.

**If shows less than 3**: Won't detect as various artists (needs 3+).

### 6. `[DEBUG] Calling detection function...`
Confirms detection function is being called.

**If this doesn't appear**: Either no label or less than 3 artists.

### 7. `[DEBUG] Detection result: <True/False>`
Shows if detection function determined this is a record label album.

**If False**: Album artist and label don't match, or track artist matches album artist.

### 8. `[DEBUG] Detection skipped - label: <bool>, artists: <count>`
Shows why detection was skipped if it didn't run.

### 9. `[DEBUG] No album artist found in tags`
Album artist wasn't extracted from tags.

## Possible Scenarios

### Scenario 1: No Album Artist
```
[DEBUG] No album artist found in tags
```
**Problem**: Tags don't have albumartist field at this point in the code.
**Solution**: Need to check why tags aren't set yet.

### Scenario 2: No Label Extracted
```
[DEBUG] Album artist from tags: Ed Banger Records
[DEBUG] Label from metadata: None
[DEBUG] Final extracted label: None
[DEBUG] Detection skipped - label: False, artists: 10
```
**Problem**: Couldn't extract label from metadata or copyright field.
**Solution**: Need to fix label extraction logic.

### Scenario 3: Not Enough Artists
```
[DEBUG] Album artist from tags: Ed Banger Records
[DEBUG] Label from metadata: None
[DEBUG] Final extracted label: Ed Banger Records
[DEBUG] Track artists found: 2 - ['Mr Oizo', 'Breakbot']
[DEBUG] Detection skipped - label: True, artists: 2
```
**Problem**: Found less than 3 track artists.
**Solution**: Need to check track artist extraction logic.

### Scenario 4: Detection Returns False
```
[DEBUG] Album artist from tags: Ed Banger Records
[DEBUG] Label from metadata: None
[DEBUG] Final extracted label: Ed Banger Records
[DEBUG] Track artists found: 10 - ['Mr Oizo', 'Breakbot', ...]
[DEBUG] Calling detection function...
[DEBUG] Detection result: False
```
**Problem**: Detection function says they don't match.
**Solution**: Need to check comparison logic in detection function.

## What We Need

Please run the upload and share:
1. The **complete console output** including all debug messages
2. Any error messages
3. Whether detection messages appeared or not

This will help us identify exactly where the issue is!

## Next Steps

Based on the debug output, we can:
- Fix label extraction if that's the issue
- Fix track artist collection if that's the issue
- Fix the detection comparison logic if that's the issue
- Fix the timing if tags aren't ready yet
