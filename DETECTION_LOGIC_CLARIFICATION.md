# Detection Logic Clarification

## User's Question

You asked:
> I just want to double check about the detection logic. It has 2 conditions correct?
> 1. The artist name is the same as the record label
> 2. The artist name contains certain keywords such as "Records", "Productions", etc.. that implies it's a record label

## Answer: NO - Only Condition #1 is Used

**The current detection logic uses ONLY label comparison (condition #1), NOT keywords (condition #2).**

The keyword-based approach was initially tried but proved unreliable and was completely replaced with label comparison.

---

## Current Detection Logic (3 Conditions)

From `_is_record_label_album()` function in `brucelee94/uploader/__init__.py` (lines 954-1018):

### Condition 1: Album Artist Matches Label ✓

The album artist must match or be very similar to the record label:

**Exact Match:**
```
Album artist: "Ed Banger Records"
Label:        "Ed Banger Records"
→ Match! ✓
```

**Contains Match (60%+ overlap):**
```
Album artist: "Ed Banger"
Label:        "Ed Banger Records"
→ "Ed Banger" in "Ed Banger Records" with 100% overlap ✓
```

### Condition 2: Multiple Track Artists ✓

The album must have at least 3 different track artists:

```
Track artists: ['Mr Oizo', 'Breakbot', 'Busy P', 'Justice', ...]
Count: 10 artists
→ Has 3+ track artists ✓
```

This confirms it's a compilation with various artists, not a single artist album.

### Condition 3: No Track Artist Matches Album Artist ✓

None of the track artists should match the album artist name:

```
Album artist: "Ed Banger Records"
Track artists: ['Mr Oizo', 'Breakbot', ...]
→ No track artist named "Ed Banger Records" ✓
```

This confirms the album artist is a label name, not an actual performing artist.

---

## What About Keywords? (NOT USED)

**Keywords like "Records", "Music", "Productions", "Entertainment" are NOT checked.**

### Why Keywords Were Removed

The initial implementation (first commit) tried using keywords, but this approach was:

❌ **Not Reliable**
- Many labels don't have these keywords (e.g., "XL", "Warp", "Ninja Tune")
- Some artist names contain these keywords (e.g., "Atlantic Records Band")
- Too many false positives and false negatives

❌ **Failed Testing**
- Didn't work for Ed Banger Records (no "Records" detection was triggered)
- User's test showed it failed to detect properly

❌ **Too Arbitrary**
- Requires maintaining a keyword list
- Different languages have different words
- Not based on actual metadata

### Why Label Comparison is Better

✅ **More Accurate**
- Compares to actual label data from metadata
- Uses real information, not guesswork

✅ **More Reliable**
- Works for all label names regardless of keywords
- No need to maintain keyword lists

✅ **More Specific**
- Requires actual match between artist and label
- Reduces false positives

---

## Code Reference

```python
def _is_record_label_album(albumartist, label, track_artists_list):
    """
    Detect if the album artist is a record label for a various artists album.
    
    NEW detection logic: Compare album artist to record label.
    NOT using keywords anymore!
    """
    
    # Condition 1: Album artist matches label
    if albumartist.lower() == label.lower():
        match_found = True
    elif albumartist.lower() in label.lower() or label.lower() in albumartist.lower():
        # Check for 60%+ overlap
        if overlap / shorter >= 0.6:
            match_found = True
    
    if not match_found:
        return False
    
    # Condition 2: Multiple track artists (3+)
    if len(track_artists_list) < 3:
        return False
    
    # Condition 3: No track artist matches album artist
    for track_artist in track_artists_list:
        if track_artist matches albumartist:
            return False
    
    return True
```

**NO keyword checking in this logic!**

---

## Examples

### Will Detect (All 3 Conditions Met)

**Example 1: Ed Banger Records**
```
Album artist: "Ed Banger Records"
Label:        "Ed Banger Records"
Track artists: ['Mr Oizo', 'Breakbot', 'Busy P', ...]

✓ Artist matches label exactly
✓ Has 10 track artists (3+)
✓ No track artist named "Ed Banger Records"
→ DETECTED as label album!
```

**Example 2: War Child Records**
```
Album artist: "War Child Records"
Label:        "War Child Records"
Track artists: ['Arctic Monkeys', 'Coldplay', 'Damon Albarn', ...]

✓ Artist matches label exactly
✓ Has multiple track artists
✓ No track matches "War Child Records"
→ DETECTED as label album!
```

**Example 3: XL Recordings**
```
Album artist: "XL Recordings"
Label:        "XL Recordings"
Track artists: ['Artist 1', 'Artist 2', 'Artist 3', ...]

✓ Artist matches label exactly
✓ Has 3+ track artists
✓ No track named "XL Recordings"
→ DETECTED as label album!

Note: NO keywords like "Recordings" are checked!
The match is based on comparing the artist name to the label name.
```

### Won't Detect (Conditions Not Met)

**Example 1: Real Artist with Label**
```
Album artist: "Taylor Swift"
Label:        "Republic Records"
Track artists: ['Taylor Swift']

✗ Artist doesn't match label
→ NOT detected (correct - real artist album)
```

**Example 2: Track Artist Matches Album Artist**
```
Album artist: "Atlantic Records"
Label:        "Atlantic Records"
Track artists: ['Atlantic Records Band', 'Artist 2', 'Artist 3']

✓ Artist matches label
✓ Has 3+ track artists
✗ Track artist "Atlantic Records Band" contains "Atlantic Records"
→ NOT detected (correct - probably a band named after label)
```

**Example 3: Not Enough Track Artists**
```
Album artist: "Some Label"
Label:        "Some Label"
Track artists: ['Artist 1', 'Artist 2']

✓ Artist matches label
✗ Only has 2 track artists (need 3+)
→ NOT detected (not enough variety for "Various Artists")
```

---

## History of Detection Logic

### Phase 1: Keyword Approach (Removed)
- Checked for words like "Records", "Music", "Entertainment"
- Failed to detect Ed Banger Records properly
- Too unreliable

### Phase 2: Label Comparison (Current)
- Compare album artist to actual record label
- Much more accurate and reliable
- Successfully detected Ed Banger Records
- Working in production

### Phase 3: Original Label Preservation (Enhancement)
- Fixed issue where Qobuz changed label to "Self-Released"
- Now saves original label for detection
- Upload still uses "Self-Released" (RED compliance)

---

## Summary

**To Clarify:**

✅ **YES:** Detection compares album artist to record label
✅ **YES:** Requires 3+ track artists
✅ **YES:** Checks that no track artist matches album artist

❌ **NO:** Does NOT check for keywords like "Records", "Productions", etc.
❌ **NO:** Keywords are not part of the detection logic

The detection is based entirely on **comparing the album artist name to the actual record label extracted from metadata**, not on keyword pattern matching.

---

## Questions?

If you have any questions about how the detection works or want to understand why certain albums are or aren't detected, feel free to ask!

The key point: **It's all about comparing the artist name to the label name, not checking for keywords.**
