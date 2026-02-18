# Inline Guest Artist BBCode Feature

## Overview

This feature adds BBCode `[artist]` tags to guest artists that are already mentioned in track titles, preventing duplication in torrent group descriptions.

## Problem Solved

**Before this feature:**
```
[b]01.[/b] My love is forever (feat. Jay Heson) (feat. [artist]Jay Heson[/artist])
```
The guest artist appeared twice - once in the original title and once appended.

**After this feature:**
```
[b]01.[/b] My love is forever (feat. [artist]Jay Heson[/artist])
```
The guest artist appears once with BBCode tags added inline.

## Features

### 1. Pattern Detection
Detects various featuring patterns:
- `(feat. Name)`
- `(ft. Name)`
- `(featuring Name)`

All patterns are case-insensitive.

### 2. Multiple Guest Handling
Properly splits and tags multiple guests:
- `(feat. A, B & C)` → `(feat. [artist]A[/artist], [artist]B[/artist] & [artist]C[/artist])`
- `(feat. A & B)` → `(feat. [artist]A[/artist] & [artist]B[/artist])`
- `(feat. A, B, C)` → `(feat. [artist]A[/artist], [artist]B[/artist] & [artist]C[/artist])`

### 3. Separator Preservation
Maintains original separator formatting:
- Commas (`, `) between most guests
- Ampersand (` & `) before the last guest

### 4. Backwards Compatibility
- If title has inline guests: Add BBCode inline only
- If title has no inline guests: Append guest suffix as before

## Implementation

### Core Function

```python
def add_artist_bbcode_to_feat(title):
    """
    Add [artist] BBCode tags to guest artists in (feat. ...) mentions.
    
    Args:
        title: Track title string
        
    Returns:
        Title with BBCode tags added to guest artists
    """
```

### Integration Points

#### Non-DJ Mix Albums

**Multi-disc section:**
```python
# Check if title already has inline guest artists
title_has_inline_guests = re.search(r'\((feat\.|ft\.|featuring)', title, re.IGNORECASE)

if title_has_inline_guests:
    # Add BBCode to inline guests, don't append separate guest suffix
    description += add_artist_bbcode_to_feat(title)
else:
    # No inline guests in title
    description += title
    # Add guest/featured artists after title in (feat. ...)
    if guest_artists_str:
        description += f" (feat. {guest_artists_str})"
```

**Single-disc section:** Same logic as multi-disc

#### DJ Mix Uploads

Both multi-disc and single-disc:
```python
# Add inline BBCode to guest artists in title (if present)
title_with_bbcode = add_artist_bbcode_to_feat(track['t'].title)
description += f"{title_with_bbcode} [i]({length})[/i]\n"
```

No other changes to DJ Mix behavior.

## Examples

### Example 1: Single Guest (feat.)
```
Input:  "My love is forever (feat. Jay Heson)"
Output: "My love is forever (feat. [artist]Jay Heson[/artist])"
```

### Example 2: Single Guest (ft.)
```
Input:  "Track Title (ft. Artist Name)"
Output: "Track Title (ft. [artist]Artist Name[/artist])"
```

### Example 3: Single Guest (featuring)
```
Input:  "Song (featuring Guest Artist)"
Output: "Song (featuring [artist]Guest Artist[/artist])"
```

### Example 4: Multiple Guests with Comma
```
Input:  "Track (feat. Artist A, Artist B, Artist C)"
Output: "Track (feat. [artist]Artist A[/artist], [artist]Artist B[/artist] & [artist]Artist C[/artist])"
```

### Example 5: Multiple Guests with Ampersand
```
Input:  "Track (feat. Artist A & Artist B)"
Output: "Track (feat. [artist]Artist A[/artist] & [artist]Artist B[/artist])"
```

### Example 6: Mixed Separators
```
Input:  "Track (feat. A, B & C)"
Output: "Track (feat. [artist]A[/artist], [artist]B[/artist] & [artist]C[/artist])"
```

### Example 7: DJ Mix with Inline Guest
```
Input track artist: "The Junkies"
Input track title:  "Parts & Labour (feat. Mary Doufle)"

Output: [b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (feat. [artist]Mary Doufle[/artist]) [i](03:59)[/i]
```

### Example 8: Non-DJ Mix Without Inline Guests
```
Input title: "My love is forever"
Guest metadata: "Jay Heson"

Output: [b]01.[/b] My love is forever (feat. [artist]Jay Heson[/artist])
```
(Appends as before - backwards compatible)

## Technical Details

### Pattern Matching
```regex
r'\((feat\.|ft\.|featuring)\s+([^)]+)\)'
```

**Breakdown:**
- `\(` - Opening parenthesis
- `(feat\.|ft\.|featuring)` - Capture group 1: The keyword
- `\s+` - One or more whitespace characters
- `([^)]+)` - Capture group 2: Guest names (everything until closing paren)
- `\)` - Closing parenthesis
- `re.IGNORECASE` flag - Case insensitive matching

### Guest Splitting Algorithm

```python
guest_list = []
for comma_part in guests_text.split(', '):
    for guest in comma_part.split(' & '):
        guest = guest.strip()
        if guest:
            guest_list.append(guest)
```

**Process:**
1. Split on ", " (comma space) to get comma-separated parts
2. For each part, split on " & " (space ampersand space)
3. Strip whitespace from each guest name
4. Skip empty strings
5. Add to guest list

**Example:** `"A, B & C"`
- Split on ", ": `["A", "B & C"]`
- Split each on " & ": `["A"]`, `["B", "C"]`
- Result: `["A", "B", "C"]`

### BBCode Generation

```python
if len(guest_list) == 1:
    bbcode_guests = f"[artist]{guest_list[0]}[/artist]"
elif len(guest_list) == 2:
    bbcode_guests = f"[artist]{guest_list[0]}[/artist] & [artist]{guest_list[1]}[/artist]"
else:
    # Multiple guests: use ", " for all but last, " & " for last
    bbcode_guests = ', '.join([f"[artist]{g}[/artist]" for g in guest_list[:-1]])
    bbcode_guests += f" & [artist]{guest_list[-1]}[/artist]"
```

**Formatting Rules:**
- 1 guest: `[artist]Name[/artist]`
- 2 guests: `[artist]Name1[/artist] & [artist]Name2[/artist]`
- 3+ guests: `[artist]A[/artist], [artist]B[/artist] & [artist]C[/artist]`

## Benefits

1. **No Duplication** - Guest names appear once with BBCode
2. **Cleaner Descriptions** - No redundant (feat. ...) suffix
3. **Consistent** - Works for both DJ Mix and non-DJ Mix
4. **Flexible** - Handles various feat. formats
5. **Smart** - Splits multiple guests correctly
6. **Preserves Context** - Keeps feat. in original position
7. **Backwards Compatible** - Appends when not in title

## Testing

All 10 tests pass:

1. ✓ Single guest with feat.
2. ✓ Single guest with ft.
3. ✓ Single guest with featuring
4. ✓ Multiple guests with comma
5. ✓ Multiple guests with ampersand
6. ✓ Multiple guests with mixed separators
7. ✓ No feat. in title
8. ✓ Case insensitive matching
9. ✓ Multiple feat. mentions
10. ✓ Real-world example

Test file: `test_inline_guest_bbcode.py`

## Files Modified

**brucelee94/uploader/upload.py:**
- Lines 298-347: New `add_artist_bbcode_to_feat()` function
- Lines 536-538: DJ Mix multi-disc inline BBCode
- Lines 554-568: Non-DJ Mix multi-disc inline BBCode logic
- Lines 621-623: DJ Mix single-disc inline BBCode
- Lines 634-648: Non-DJ Mix single-disc inline BBCode logic

## Impact

**Changed:**
- Inline guest artist display (no duplication)
- BBCode added to existing feat. mentions

**Unchanged:**
- DJ Mix overall behavior (only inline BBCode added)
- Non-DJ Mix overall behavior (only inline BBCode added)
- Guest artist appending when not in title (backwards compatible)
- All other torrent description formatting

## Edge Cases Handled

1. **No feat. in title** - Returns title unchanged
2. **Multiple feat. mentions** - Adds BBCode to all of them
3. **Case variations** - FEAT., Feat., feat., FT., Ft., ft., etc.
4. **Empty guest names** - Skipped (stripped and filtered)
5. **Whitespace variations** - Normalized with strip()
6. **Mixed separators** - Handles both ", " and " & " correctly

## Future Considerations

Possible enhancements:
- Support for additional patterns: `(w/ Name)`, `(with Name)`
- Support for non-parenthesized feat.: `Title feat. Name`
- Configurable separator formatting
- Language-specific featuring keywords

## Compatibility

- ✅ Works with existing guest artist metadata extraction
- ✅ Works with smart artist display logic
- ✅ Works with DJ Mix file-based artists
- ✅ Works with multi-disc and single-disc albums
- ✅ No breaking changes to existing features
