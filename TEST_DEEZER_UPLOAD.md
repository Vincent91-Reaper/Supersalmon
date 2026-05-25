# Test Plan for Deezer Upload Implementation

## Quick Verification Checklist

Use this checklist to verify the Deezer upload implementation is working correctly.

### ✅ Pre-Test Setup

- [ ] Have a Deezer album downloaded (FLAC format)
- [ ] Know the Deezer album URL (e.g., `https://www.deezer.com/en/album/852049722`)
- [ ] Files have genre tags (verify with tag editor if unsure)

### ✅ Test 1: URL Detection

**Run:**
```bash
bl94 up /path/to/deezer/album -s Deezer -su "https://www.deezer.com/en/album/ALBUM_ID"
```

**Expected output:**
```
Deezer URL detected - skipping metadata scraping
Extracting metadata from file tags...
```

**Verify:**
- [ ] Message shows "Deezer URL detected"
- [ ] Message shows "Extracting metadata from file tags"
- [ ] No scraping attempt made

### ✅ Test 2: Metadata Extraction

**After URL detection, check:**

**Expected behavior:**
- Reads metadata from downloaded files
- Shows album info (title, artist, year, label)
- Shows track count

**Verify:**
- [ ] Album title matches your files
- [ ] Artist(s) match your files
- [ ] Year matches your files
- [ ] Label extracted (check file copyright tag)

### ✅ Test 3: Genre Handling (CRITICAL)

**Check genres in the extracted metadata:**

**Expected:**
- Genres come from file tags
- NOT just "electronic" (unless that's the actual genre)

**How to verify:**
1. Check your file tags (use mutagen-inspect or similar):
   ```bash
   mutagen-inspect /path/to/file.flac | grep -i genre
   ```

2. Compare to what brucelee94 extracted:
   ```
   Shows genres from files (e.g., "Pop", "Country", "Electronic")
   ```

**Verify:**
- [ ] Genres match your file tags
- [ ] NOT defaulting to "electronic" only
- [ ] Multiple genres preserved if present

### ✅ Test 4: Artist Classification

**Check artist roles:**

**Expected:**
- Main artists (in albumartist tag) → "main" role
- Guest artists (in artist but not albumartist) → "guest" role

**Verify:**
- [ ] Main artists classified correctly
- [ ] Guest artists classified correctly
- [ ] No "Various Artists" in final list (replaced with actual artists)

### ✅ Test 5: Upload Process

**Continue through upload workflow:**

**Expected:**
- No retagging prompt (files already correct)
- No edit metadata prompt (skipped)
- Folder structure check runs (if needed)
- Generates torrent description
- Uploads to RED

**Verify:**
- [ ] No retagging workflow triggered
- [ ] Torrent description generated
- [ ] Genres in description match file tags
- [ ] Upload succeeds

### ✅ Test 6: Compare to Tidal

**If you have a Tidal album, compare:**

| Feature | Tidal Result | Deezer Result | Match? |
|---------|--------------|---------------|--------|
| Skip scraping | ✅ | ✅ | ☐ |
| Extract from files | ✅ | ✅ | ☐ |
| Has genres | ❌ "electronic" | ✅ Actual | ☐ |
| Skip retagging | ✅ | ✅ | ☐ |
| Artist roles | ✅ | ✅ | ☐ |

**Verify:**
- [ ] Both skip scraping
- [ ] Both extract from files
- [ ] Deezer uses actual genres (different from Tidal)
- [ ] Both skip retagging

## Sample Test Album

**Recommended test:**
```
Album: Taylor Swift - The Life of a Showgirl + Acoustic Collection
URL: https://www.deezer.com/en/album/852049722
```

**Expected results:**
- Artist: Taylor Swift
- Year: 2025
- Label: Republic Records (from copyright)
- Genres: pop,country (from file tags, NOT "electronic")
- Tracks: 16 tracks

## Common Issues and Solutions

### Issue: Still tries to scrape from URL

**Cause:** URL pattern not matching
**Check:** Is the URL format correct?
```
✅ https://www.deezer.com/en/album/852049722
✅ https://www.deezer.com/album/852049722
✅ https://deezer.com/en/album/852049722
❌ https://www.deezer.com/track/123456 (track URL, not album)
```

### Issue: Genres show as "electronic" only

**Cause:** Files don't have genre tags
**Check:**
```bash
mutagen-inspect file.flac | grep -i genre
```
**Solution:** Re-download from Deezer or manually add genre tags

### Issue: All artists are "main" or all are "guest"

**Cause:** albumartist tag missing or incorrect
**Check:**
```bash
mutagen-inspect file.flac | grep -i albumartist
```
**Solution:** Ensure albumartist tag contains main album artists

### Issue: Label incorrect

**Cause:** Copyright tag parsing issue
**Check:**
```bash
mutagen-inspect file.flac | grep -i copyright
```
**Expected:** Copyright should contain label info

## Success Criteria

✅ **All tests pass if:**

1. Deezer URL detected correctly
2. Metadata extracted from files
3. Genres match file tags (not "electronic" fallback)
4. Artists classified correctly
5. Upload succeeds with accurate metadata

## Report Results

If all tests pass: ✅ Implementation successful!

If any test fails:
1. Note which test failed
2. Capture error messages
3. Check file tags with mutagen-inspect
4. Report issue with details

## Additional Verification

### Check Generated Torrent Description

After upload, verify the torrent description on RED:

**Should include:**
- [ ] Correct album title
- [ ] Correct artist(s)
- [ ] Correct year
- [ ] Correct label
- [ ] **Genres from file tags** (not just "electronic")
- [ ] All tracks listed
- [ ] Source URL (Deezer link)

**Should NOT include:**
- [ ] "Various Artists" (replaced with actual artists)
- [ ] Only "electronic" as genre (unless that's the actual genre)

## Code Verification

### Files to Check

**1. metadata.py:**
```python
# Should have Deezer pattern
deezer_pattern = re.compile(r"^https?://.*deezer\.com.*\/(album)\/([0-9]+)")
```

**2. __init__.py:**
```python
# Should handle _is_deezer flag
is_deezer = metadata.get("_is_deezer", False)
# Should pass is_tidal=is_tidal (False for Deezer)
check_folder_structure(path, scene, genres, is_tidal=is_tidal, from_url=True)
```

### Quick Code Check

```bash
# Verify Deezer pattern exists
grep -n "deezer_pattern" brucelee94/tagger/metadata.py

# Verify Deezer handling exists
grep -n "is_deezer" brucelee94/uploader/__init__.py

# Check expected lines exist
grep -n "is_tidal=is_tidal" brucelee94/uploader/__init__.py
```

## Final Checklist

- [ ] URL detection works
- [ ] Metadata extraction works
- [ ] Genres from files (not "electronic")
- [ ] Artists classified correctly
- [ ] No retagging triggered
- [ ] Upload succeeds
- [ ] Torrent description accurate
- [ ] Documentation read (DEEZER_UPLOAD_GUIDE.md)

**If all checked:** ✅ **Implementation verified and working!**
