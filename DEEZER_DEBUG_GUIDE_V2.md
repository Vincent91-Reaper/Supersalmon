# Deezer Scraping Debug Guide V2

## Based on Actual User Output

### What We Learned

The user provided this debug output:
```
[DEBUG] scrape_release: soup['label'] = 'Taylor Swift'
[DEBUG] parse_release_label: label type = 
```

**Key Finding:** The label from Deezer API is `'Taylor Swift'` - already a string, NOT a tuple!

This means our original hypothesis about nested tuples was **incorrect**. The label field from Deezer is working fine.

### New Hypothesis

Since the label is already a string, the "expected string or bytes-like object, got 'tuple'" error is likely occurring in the **self-released album detection** logic.

The code that checks for self-released albums iterates through `data["artists"]` which is a list of tuples: `[(artist_name, role), ...]`

The error probably occurs when:
1. Unpacking the artist tuples
2. One of the artist names is itself a tuple
3. The comparison `label.lower().startswith(artist_name.lower())` fails because `artist_name` is a tuple

### Improved Debug Logging

We've added much more robust debug logging that will pinpoint the exact issue:

#### Features:

1. **Output to stderr** (`err=True`)
   - Won't interfere with the program's normal stdout
   - All debug messages go to stderr

2. **Try/except wrapping**
   - Every debug statement wrapped in try/except
   - Won't crash if there's an error in debug code itself

3. **Granular artist checking**
   - Shows each artist being checked individually
   - Shows when self-released detection succeeds
   - Catches errors for specific artists

4. **Color coding**
   - **Cyan**: Initial soup data from API
   - **Yellow**: `parse_release_label()` processing
   - **Magenta**: `process_label()` processing
   - **Green**: Successful results
   - **Red**: Errors

5. **Truncation**
   - Long values truncated to 100 chars
   - Prevents output overflow

### What You'll See Now

When you run brucelee94 with a Deezer URL, you should see output like this:

```
Scraping metadata from Deezer...
[DEBUG] scrape_release: soup keys = ['id', 'title', 'label', ...]
[DEBUG] scrape_release: soup['label'] = Taylor Swift
[DEBUG] scrape_release: soup['label'] type = str

[DEBUG] parse_release_label: raw label type = str
[DEBUG] parse_release_label: raw label value = Taylor Swift
[DEBUG] parse_release_label: final label type = str
[DEBUG] parse_release_label: final label value = Taylor Swift
[DEBUG] parse_release_label: parse_copyright returned = Taylor Swift

[DEBUG] process_label: raw label type = str
[DEBUG] process_label: raw label value = Taylor Swift
[DEBUG] process_label: final label type = str
[DEBUG] process_label: final label value = Taylor Swift
[DEBUG] process_label: Checking 1 artists for self-released
[DEBUG] process_label: Checking artist 'Taylor Swift' with role 'main'
[DEBUG] process_label: Self-released detected! Artist 'Taylor Swift' matches label
[DEBUG] process_label: Returning label = Self-Released
```

Or if there's an error:
```
[DEBUG] process_label: Checking artist '...' with role 'main'
[DEBUG] process_label: Error checking artist (..., ...): expected string or bytes-like object, got 'tuple'
[DEBUG] process_label: Returning label = Taylor Swift
```

### How to Test

1. Run brucelee94 with the problematic Deezer URL:
   ```
   https://www.deezer.com/en/album/852049722
   ```

2. Capture **all output** including stderr (debug messages)

3. Look for:
   - Which artist causes the error (if any)
   - Whether the error is in unpacking or comparison
   - The complete path from raw label to final label

### What to Report Back

Please share:
1. Complete debug output (including all color-coded lines)
2. Whether scraping succeeds or fails
3. If it fails, the exact error message
4. Which artist is being processed when error occurs

### Expected Outcomes

**If scraping succeeds:**
- You'll see the complete trace of label processing
- Self-released detection may or may not trigger
- Album metadata will be scraped successfully

**If scraping fails:**
- You'll see exactly which artist causes the issue
- The error message will show what type the problematic value is
- This will tell us exactly what needs to be fixed

### Technical Details

The improved `process_label()` function now:
1. Safely gets the label from data
2. Converts it to a string if needed
3. Iterates through each artist individually
4. Safely unpacks each artist tuple
5. Converts artist_name to string if needed
6. Catches and logs any errors per artist
7. Returns the label or "Self-Released"

Each step is logged so we can see exactly where any issue occurs.

### Next Steps

Once we see the complete debug output from your test, we'll know:
- If the fix works (scraping succeeds)
- If there's still an error, exactly where it is
- What type the problematic value actually is
- How to fix it permanently

Then we can:
- Remove the debug logging
- Implement a proper fix
- Test again to confirm
- Ship the final version
