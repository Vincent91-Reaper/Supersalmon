# Metadata Tracks Update Fix

## Critical Bug Fixed

Fixed critical bug where cleaned artist data was being overwritten because `metadata["tracks"]` wasn't updated after cleaning.

## The Problem

After commit 6aa5856 added `metadata["artists"]` cleaning, user reported the issue still persisted:
> "brucelee94 still passes 'Dj Twi$t II' and 'Former City Records' to its upload manager as main album artists. Also passes 'Former City Records' as track artist."

## Root Cause

The cleaning was being **overwritten** by later code:

```python
# Line 498-648: Clean file tags, refresh track_data
tags = cleaned_tags  # ✓ Clean
track_data = concat_track_data(tags)  # ✓ Clean from cleaned tags

# Line 668: Clean metadata["artists"]
metadata["artists"] = cleaned_artists  # ✓ Clean

# BUT metadata["tracks"] was NEVER updated
# It still contained old data with the label!

# Line 981-984: Later code rebuilds metadata["artists"]
for disc in metadata.get("tracks", {}).values():  # ✗ STALE DATA!
    for track in disc.values():
        all_artists.extend(track["artists"])  # Label included!

# Line 1000: OVERWRITES our cleaning
metadata["artists"] = unique_artists  # ✗ Label back in!
```

## The Solution

**Added ONE line at 651:**
```python
# Update metadata["tracks"] from refreshed track_data
metadata["tracks"] = track_data
```

This ensures `metadata["tracks"]` contains clean data, so when `metadata["artists"]` is rebuilt later, it uses clean data.

## Why This Was Needed

The code flow has multiple stages:
1. **Early stage:** Populate `metadata["tracks"]` from initial track_data
2. **Artist+label cleaning:** Clean file tags, refresh track_data
3. **Later stage:** Rebuild `metadata["artists"]` from `metadata["tracks"]`

Without updating `metadata["tracks"]` at stage 2, stage 3 uses stale data!

## Complete Flow (After Fix)

```
1. Detection: Label "Former City Records" found in album artist
2. Clean file tags: Remove from album artist and track artist tags
3. Save files: Write cleaned tags to disk
4. Refresh track_data: Read clean data from cleaned files
5. Update metadata["tracks"]: Use clean track_data (NEW!)
6. Clean metadata["artists"]: Remove label
7. [Later] Rebuild metadata["artists"]: Uses clean metadata["tracks"]
8. Result: Label stays removed throughout!
```

## Result

**File Tags:**
- Album artist: "Dj Twi$t II" ✓
- Track artists: No "Former City Records" ✓

**Upload Metadata:**
- metadata["artists"]: [("Dj Twi$t II", "main")] ✓
- metadata["tracks"]: Clean data without label ✓

**Torrent Description:**
- Album artist: "Dj Twi$t II" ✓
- Track artists: Real artists only ✓
- Label field: "Former City Records" ✓

## Key Takeaway

**When cleaning metadata that gets rebuilt from track_data later, you MUST update metadata["tracks"] from the refreshed track_data, not just clean the final metadata field.**

This ensures the clean data propagates through the entire processing flow.

## Commits

- **6aa5856:** Added metadata["artists"] cleaning (had overwrite bug)
- **922f82e:** Fixed with metadata["tracks"] update (WORKING!)
