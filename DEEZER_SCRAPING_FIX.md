# Deezer Scraping Fix Documentation

## Problem

User reported the following error when scraping from Deezer URLs:

```
Enter a metadata/source URL to use for brucelee94 (or leave blank to enter it when brucelee prompts): https://www.deezer.com/en/album/852049722

Processing /mnt/d/Music to upload to redacted/Taylor Swift - The Life of a Showgirl + Acoustic Collection (2025) [WEB FLAC] [16-44.1]

Please provide a URL to scrape metadata from (or [m]anual, [a]bort): https://www.deezer.com/en/album/852049722
Scraping metadata from Deezer...
Unexpected scrape error: expected string or bytes-like object, got 'tuple'
Failed to scrape metadata from https://www.deezer.com/en/album/852049722
URL not recognized or failed to scrape. Please try again.
```

## Root Cause

The error "expected string or bytes-like object, got 'tuple'" indicates that somewhere in the code, a regex operation (like `re.search()` or `re.sub()`) was being called on a tuple instead of a string.

### Investigation

1. The error occurs during Deezer metadata scraping
2. The `parse_copyright()` function uses `re.search()` on the label field
3. Deezer API can return the `label` field in various formats:
   - String: `"Republic Records"`
   - Dict: `{"name": "Republic Records"}`  
   - Tuple/List: `("Republic Records",)` or `[("Republic Records",)]`
   - Nested structures: `(("Republic Records",),)`

4. The original code handled dict and single-level tuple/list:
   ```python
   if isinstance(label, dict):
       label = label.get("name", "")
   elif isinstance(label, (tuple, list)):
       label = label[0] if label else ""
   ```

5. But if `label[0]` was still a tuple, it would be passed to `parse_copyright()`, causing the regex error.

## Solution

### Fix 1: Nested Tuple Handling

Added a while loop to handle nested structures:

```python
elif isinstance(label, (tuple, list)):
    # If tuple/list, take first element (usually the name)
    # Handle nested structures: extract until we get a string
    while label and isinstance(label, (tuple, list)):
        label = label[0] if label else ""
```

This extracts elements recursively until we get a non-tuple/list value.

### Fix 2: Final Type Check

Added a final safety check:

```python
# Ensure label is a string
if not isinstance(label, str):
    label = str(label) if label else ""
```

This guarantees `label` is always a string before being passed to `parse_copyright()`.

### Fix 3: Error Handling in Self-Released Check

Added try/except in `process_label()`:

```python
try:
    if any(
        label.lower().startswith(artist_name.lower()) and role == "main" 
        for artist_name, role in data["artists"]
    ):
        return "Self-Released"
except (TypeError, AttributeError) as e:
    click.secho(f"[DEBUG] process_label: Error in self-released check: {e}", fg="red")
    # Continue with original label if check fails
```

This prevents crashes if artist iteration fails.

## Debug Logging

Comprehensive debug logging was added to help diagnose the issue:

### Location 1: scrape_release() in base.py

```python
click.secho(f"[DEBUG] scrape_release: soup keys = {list(soup.keys())}", fg="cyan")
click.secho(f"[DEBUG] scrape_release: soup['label'] = {repr(soup.get('label'))}", fg="cyan")
```

Shows what the API actually returns.

### Location 2: parse_release_label() in deezer.py

```python
click.secho(f"[DEBUG] parse_release_label: label type = {type(label)}, value = {repr(label)}", fg="yellow")
# ... conversion logic ...
click.secho(f"[DEBUG] parse_release_label: converted label type = {type(label)}, value = {repr(label)}", fg="yellow")
```

Shows label before and after conversion.

### Location 3: process_label() in deezer.py

```python
click.secho(f"[DEBUG] process_label: label type = {type(label)}, value = {repr(label)}", fg="yellow")
click.secho(f"[DEBUG] process_label: artists = {repr(data.get('artists', []))}", fg="yellow")
# ... conversion logic ...
click.secho(f"[DEBUG] process_label: converted label type = {type(label)}, value = {repr(label)}", fg="yellow")
```

Shows label and artists data during processing.

## Expected Debug Output

When running with the fix, you should see:

```
[DEBUG] scrape_release: soup keys = ['id', 'title', 'label', 'release_date', ...]
[DEBUG] scrape_release: soup['label'] = 'Republic Records'  # or tuple/dict

[DEBUG] parse_release_label: label type = <class 'str'>, value = 'Republic Records'
[DEBUG] parse_release_label: converted label type = <class 'str'>, value = 'Republic Records'

[DEBUG] process_label: label type = <class 'str'>, value = 'Republic Records'
[DEBUG] process_label: artists = [('Taylor Swift', 'main')]
[DEBUG] process_label: converted label type = <class 'str'>, value = 'Republic Records'
```

If the label was originally a tuple, you'd see:

```
[DEBUG] parse_release_label: label type = <class 'tuple'>, value = ('Republic Records',)
[DEBUG] parse_release_label: converted label type = <class 'str'>, value = 'Republic Records'
```

Or for nested tuples:

```
[DEBUG] parse_release_label: label type = <class 'tuple'>, value = (('Republic Records',),)
[DEBUG] parse_release_label: converted label type = <class 'str'>, value = 'Republic Records'
```

## Testing

### Test with the Problematic URL

```bash
# Run brucelee94 with the URL that was failing
Enter a metadata/source URL: https://www.deezer.com/en/album/852049722
```

### Expected Result

1. Debug messages appear showing label conversion
2. No "expected string or bytes-like object, got 'tuple'" error
3. Metadata scraping succeeds
4. Label is correctly extracted and displayed

### What to Check

1. **Debug messages show label as string:**
   - After conversion, type should be `<class 'str'>`
   
2. **No errors during scraping:**
   - Should complete without "Unexpected scrape error"
   
3. **Metadata is correct:**
   - Label field should show the actual label name
   - Other fields (artists, tracks, etc.) should be populated

## Removing Debug Logging

Once the fix is confirmed to work, the debug logging can be removed in a future commit. The debug messages are currently in:

1. `brucelee94/tagger/sources/base.py` - Lines 59-63
2. `brucelee94/tagger/sources/deezer.py` - Lines 69-72, 84-85, 113-116, 129-130

## Files Modified

1. **brucelee94/tagger/sources/base.py**
   - Added debug logging in `scrape_release()`

2. **brucelee94/tagger/sources/deezer.py**
   - Enhanced `parse_release_label()` with nested tuple handling
   - Enhanced `process_label()` with nested tuple handling and error handling
   - Added debug logging throughout

## Status

✅ Fix implemented with debug logging  
✅ Documentation complete  
⏳ Awaiting user testing to confirm fix works

## Next Steps

1. User tests with the problematic URL
2. Review debug output to confirm label conversion
3. Verify scraping succeeds without errors
4. If successful, remove debug logging in follow-up commit
5. If issues remain, debug output will help identify next steps
