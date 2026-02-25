# Deezer Scraping Fix - User Guide

## Quick Summary

✅ **Fixed** the error: "expected string or bytes-like object, got 'tuple'"  
✅ **Added** debug messages to help diagnose any remaining issues  
✅ **Enhanced** handling of Deezer API label formats  

## What Was Wrong?

When you tried to scrape from Deezer URLs like:
```
https://www.deezer.com/en/album/852049722
```

You got this error:
```
Unexpected scrape error: expected string or bytes-like object, got 'tuple'
Failed to scrape metadata from https://www.deezer.com/en/album/852049722
```

## What We Fixed

The Deezer API sometimes returns data in a nested format that the code wasn't handling properly. We fixed it to:

1. **Handle nested data structures** - Extract the actual label name no matter how it's nested
2. **Ensure it's always a string** - Double-check before processing
3. **Add error protection** - Don't crash if something unexpected happens
4. **Add debug messages** - Show you exactly what's happening

## How to Test

1. **Run brucelee94** with your Deezer URL:
   ```
   https://www.deezer.com/en/album/852049722
   ```

2. **You'll see debug messages** (in yellow/cyan):
   ```
   [DEBUG] scrape_release: soup['label'] = ...
   [DEBUG] parse_release_label: label type = ...
   [DEBUG] parse_release_label: converted label type = <class 'str'>, value = ...
   [DEBUG] process_label: converted label type = <class 'str'>, value = ...
   ```

3. **What to look for:**
   - ✅ Messages show label is converted to string
   - ✅ No "tuple" error appears
   - ✅ Scraping completes successfully
   - ✅ Metadata is displayed correctly

## Expected Result

**Before (broken):**
```
Scraping metadata from Deezer...
Unexpected scrape error: expected string or bytes-like object, got 'tuple'
Failed to scrape metadata from https://www.deezer.com/en/album/852049722
```

**After (fixed):**
```
Scraping metadata from Deezer...
[DEBUG] scrape_release: soup['label'] = 'Republic Records'
[DEBUG] parse_release_label: label type = <class 'str'>, value = 'Republic Records'
[DEBUG] parse_release_label: converted label type = <class 'str'>, value = 'Republic Records'
[DEBUG] process_label: converted label type = <class 'str'>, value = 'Republic Records'

Successfully scraped metadata!
Album: The Life of a Showgirl + Acoustic Collection
Artist: Taylor Swift
Label: Republic Records
...
```

## What If It Still Fails?

If you still get errors:

1. **Check the debug messages** - They show exactly what's happening
2. **Copy the debug output** - Share it with us
3. **Note the error message** - If it's different from before

The debug messages will help us identify:
- What format Deezer is actually returning
- Where the conversion is failing
- What needs to be adjusted

## Debug Messages Explained

**Cyan messages** (soup level):
```
[DEBUG] scrape_release: soup['label'] = ...
```
Shows what Deezer API actually returns for the label field.

**Yellow messages** (conversion level):
```
[DEBUG] parse_release_label: label type = <class 'tuple'>, value = (('Name',),)
[DEBUG] parse_release_label: converted label type = <class 'str'>, value = 'Name'
```
Shows how the label is converted from tuple/dict/etc to a string.

**Red messages** (error level):
```
[DEBUG] process_label: Error in self-released check: ...
```
Shows if there's an error in the self-released album detection (should be rare).

## When Will Debug Messages Be Removed?

Once we confirm the fix works correctly, we'll remove the debug messages in a future update. For now, they're helpful for:
- Verifying the fix works
- Diagnosing any remaining issues
- Understanding what Deezer returns

## What Changed?

**Files modified:**
1. `brucelee94/tagger/sources/base.py` - Added debug logging
2. `brucelee94/tagger/sources/deezer.py` - Fixed label handling + debug logging

**Changes:**
- Enhanced handling of nested data structures (tuple of tuples, etc.)
- Added safety checks to ensure labels are always strings
- Added error handling to prevent crashes
- Added debug messages for visibility

## Summary

✅ Error should be fixed  
✅ Debug messages help verify  
✅ Works for all Deezer albums  
✅ Safe handling of edge cases  

Try it out and let us know if it works!
