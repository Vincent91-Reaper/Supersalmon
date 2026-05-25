# Debug Guide for Various Artists Issue

## Overview

This guide helps you diagnose why the "Various Artists" replacement isn't working in your specific case.

## Debug Messages Added

The code now includes comprehensive debug logging that will show exactly what's happening with the Various Artists detection and replacement.

## How to Use

1. **Run your upload command** with the problematic files
2. **Check the console output** for debug messages
3. **Look for the debug messages** starting with `[DEBUG]`
4. **Share the output** to help identify the issue

## Debug Message Flow

### 1. Function Call Check

```
[DEBUG] Various Artists check for file-based metadata - Before: [...]
```
or
```
[DEBUG] Various Artists check for scraped metadata - Before: [...]
```

**What this shows:** The artist list before calling the replacement function
**What to check:** Is the function being called? What artists are in the list?

### 2. Function Entry

```
[DEBUG] VA Replacement - Before: [...]
```

**What this shows:** The artist list received by the replacement function
**What to check:** Does the list match what was passed in?

### 3. Detection Result

**If Various Artists is detected:**
```
[DEBUG] Various Artists detected as only album artist
[DEBUG] Collecting track artists from metadata...
```

**If NOT detected:**
```
[DEBUG] Not replacing - Various Artists is not the only artist (count: N)
```

**What to check:** 
- Is "Various Artists" being detected?
- If not, why? (Maybe it's spelled differently or there are other artists)

### 4. Track Artist Collection

```
[DEBUG] Found track artists: ['Artist A', 'Artist B', ...]
```

**What this shows:** The unique track artists found in the metadata
**What to check:** 
- Are track artists being found?
- If empty, the track metadata might not have artist information

### 5. Replacement Result

**If replacement succeeded:**
```
[DEBUG] VA Replacement - After: [('Artist A', 'main'), ('Artist B', 'main')]
```

**If no track artists found:**
```
[DEBUG] No track artists found - keeping Various Artists
[DEBUG] VA Replacement - After: [('Various Artists', 'main')]
```

**What to check:** Did the replacement actually happen?

### 6. Final Artist List

```
[DEBUG] Various Artists check for file-based metadata - After: [...]
[DEBUG] Final artist list being passed to upload: [...]
```

**What this shows:** The final artist list that will be passed to the upload system
**What to check:** Is this the expected list? Is "Various Artists" still there?

## Common Issues and What to Look For

### Issue 1: "Various Artists" Not Detected

**Debug Output:**
```
[DEBUG] VA Replacement - Before: [('Various Artists', 'main'), ('Another Artist', 'main')]
[DEBUG] Not replacing - Various Artists is not the only artist (count: 2)
```

**Problem:** "Various Artists" is present but there are other artists too
**Explanation:** The replacement only happens when "Various Artists" is the ONLY album artist. If there are other artists, they're kept as is.
**Solution:** This is intentional behavior. If you want to replace anyway, the logic needs adjustment.

### Issue 2: Artist Name Not Exactly "Various Artists"

**Debug Output:**
```
[DEBUG] VA Replacement - Before: [('VariousArtists', 'main')]
[DEBUG] Not replacing - Various Artists is not the only artist (count: 1)
```

**Problem:** The artist name isn't exactly "Various Artists" (case-insensitive check is done)
**Explanation:** The check is `.lower() == "various artists"` so spacing matters
**Solution:** Report the exact artist string and we can adjust the detection

### Issue 3: No Track Artists Found

**Debug Output:**
```
[DEBUG] Various Artists detected as only album artist
[DEBUG] Collecting track artists from metadata...
[DEBUG] Found track artists: []
[DEBUG] No track artists found - keeping Various Artists
```

**Problem:** Track metadata doesn't contain artist information
**Explanation:** The function looks for track artists in `metadata["tracks"][disc][track]["artists"]`
**Solution:** The track metadata extraction may need debugging

### Issue 4: Function Not Called

**Debug Output:** (No debug messages at all)

**Problem:** The replacement function isn't being called
**Explanation:** Wrong code path (e.g., Beatport which is excluded)
**Solution:** Check which scraper/source is being used

## Example Complete Debug Output

Here's what a successful replacement looks like:

```
[DEBUG] Various Artists check for file-based metadata - Before: [('Various Artists', 'main')]
[DEBUG] VA Replacement - Before: [('Various Artists', 'main')]
[DEBUG] Various Artists detected as only album artist
[DEBUG] Collecting track artists from metadata...
[DEBUG] Found track artists: ['Anaëlle Latchimy', 'Artist B', 'Artist C']
[DEBUG] VA Replacement - After: [('Anaëlle Latchimy', 'main'), ('Artist B', 'main'), ('Artist C', 'main')]
[DEBUG] Various Artists check for file-based metadata - After: [('Anaëlle Latchimy', 'main'), ('Artist B', 'main'), ('Artist C', 'main')]
[DEBUG] Final artist list being passed to upload: [('Anaëlle Latchimy', 'main'), ('Artist B', 'main'), ('Artist C', 'main')]
```

## What to Share

When reporting the issue, please share:

1. **All debug messages** from your console output (everything with `[DEBUG]`)
2. **The exact error message** you're getting
3. **The source** you're using (Tidal, Qobuz, Deezer, Apple, Beatport)
4. **Sample file metadata** (like the mediainfo output you shared before)

## Next Steps

Based on the debug output, we can:
1. Identify exactly where the logic is failing
2. Determine if it's a detection issue, extraction issue, or something else
3. Provide a targeted fix for your specific case

## Quick Reference

| Debug Message | Meaning |
|--------------|---------|
| `VA Replacement - Before` | Artist list entering function |
| `Various Artists detected` | VA found as only artist |
| `Found track artists: [...]` | Track artists extracted |
| `No track artists found` | Extraction failed |
| `Not replacing` | VA not only artist or other condition failed |
| `VA Replacement - After` | Final artist list from function |
| `Final artist list being passed to upload` | What upload system receives |
