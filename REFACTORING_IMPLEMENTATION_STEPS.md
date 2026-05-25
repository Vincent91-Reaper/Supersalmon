# Refactoring Implementation Steps - Phases 2-4

## Overview

This document provides exact step-by-step instructions for completing the refactoring from complex special cases to simple unified label handling.

**Current Status:** Phase 1 complete (new functions added at lines 1584-1731)

**Remaining:** Phases 2-4 (integration, removal, testing)

---

## Phase 2: Integration

### Phase 2A: Qobuz/Apple Music Integration

**Location:** Lines 425-1020 (approx 595 lines to replace)

**Current Code:** Complex detection with Special Cases 1, 2, 3

**New Code:** Simple unified check

#### Step 1: Backup and Locate

```bash
# Current complex code starts at line 425
# Ends around line 1020
```

#### Step 2: Replace with Simple Logic

**Find:** Lines 425-1020 (entire try-except block with all special cases)

**Replace with:**
```python
        # Simple unified label handling (replaces Special Cases 1, 2, 3)
        try:
            # Get current album artist from tags
            current_albumartist = None
            for filename, tagset in tags.items():
                if hasattr(tagset, 'albumartist') and tagset.albumartist:
                    current_albumartist = tagset.albumartist
                    break
            
            if current_albumartist:
                # Extract label from metadata or tags
                extracted_label = metadata.get("_original_label") or metadata.get("label")
                
                # If label not in metadata, try to extract from tags (copyright field)
                if not extracted_label:
                    for filename, tagset in tags.items():
                        if hasattr(tagset, 'copyright') and tagset.copyright:
                            extracted_label = tagset.copyright
                            break
                
                # Simple check: Does album artist == label AND label has keywords?
                if extracted_label and current_albumartist.lower().strip() == extracted_label.lower().strip():
                    if _has_label_keywords(extracted_label):
                        click.echo()
                        click.secho(f"Detected label as album artist: {extracted_label}", fg="yellow")
                        click.secho("Processing as Various Artists compilation...", fg="cyan")
                        
                        # Use unified processing function
                        path = _process_label_as_various_artists(path, tags, extracted_label, metadata)
                        
                        # Refresh tags and track_data
                        tags = gather_tags(path)
                        audio_info = gather_audio_info(path)
                        track_data = concat_track_data(tags, audio_info)
        
        except Exception as e:
            click.secho(f"Warning: Label detection error: {e}", fg="yellow")
```

#### Step 3: Test

```bash
# Test with War Child Records (Qobuz)
brucelee94 https://www.qobuz.com/nz-en/album/help2-war-child-records/naszhk00bfnly

# Expected:
# - Album artist → "Various Artists"
# - Track artists → Clean (no "War Child Records")
# - Folder → "Various Artists - HELP(2)..."
```

### Phase 2B: Tidal/Deezer Integration

**Location:** In `_build_metadata_from_files()` function (around line 2100-2200)

#### Step 1: Find Integration Point

Look for the existing label detection code in `_build_metadata_from_files()`.

Current code around lines 2050-2200 has complex Special Case 4 handling.

#### Step 2: Replace with Simple Logic

**Find:** The complex Special Case 4 code block (lines ~2050-2200)

**Replace with:**
```python
    # Simple unified label handling for Tidal/Deezer
    try:
        # Get current album artist from first track
        current_albumartist = None
        for filename, tagset in tags.items():
            if hasattr(tagset, 'albumartist') and tagset.albumartist:
                current_albumartist = tagset.albumartist
                break
        
        if current_albumartist:
            # Extract label from tags (Tidal/Deezer have it in file metadata)
            extracted_label = metadata.get("label")
            
            # If not in metadata, try from tags
            if not extracted_label:
                for filename, tagset in tags.items():
                    if hasattr(tagset, 'copyright') and tagset.copyright:
                        extracted_label = tagset.copyright
                        break
            
            # Simple check: Does album artist == label AND label has keywords?
            if extracted_label and current_albumartist.lower().strip() == extracted_label.lower().strip():
                if _has_label_keywords(extracted_label):
                    click.echo()
                    click.secho(f"Detected label as album artist: {extracted_label}", fg="yellow")
                    click.secho("Processing as Various Artists compilation...", fg="cyan")
                    
                    # Use unified processing function
                    path = _process_label_as_various_artists(path, tags, extracted_label, metadata)
    
    except Exception as e:
        click.secho(f"Warning: Label detection error: {e}", fg="yellow")
```

#### Step 3: Update Function Return

**Important:** `_build_metadata_from_files()` must return both metadata AND path.

**Find:** Around line 2220
```python
return metadata
```

**Replace with:**
```python
return metadata, path
```

**And update caller:** Around line 368
```python
# OLD:
metadata = _build_metadata_from_files(path, tags, rls_data, is_deezer=is_deezer)

# NEW:
metadata, path = _build_metadata_from_files(path, tags, rls_data, is_deezer=is_deezer)
```

#### Step 4: Test

```bash
# Test with War Child Records (Tidal)
brucelee94 https://tidal.com/album/500752104

# Expected:
# - Album artist → "Various Artists"
# - Track artists → Clean (no "War Child Records")
# - Folder → "Various Artists - HELP(2)..."
```

---

## Phase 3: Remove Old Code

### Step 1: Remove Old Detection Functions

**Lines to remove:**

1. `_detect_label_in_albumartist()` - Around lines 1860-1916
2. `_detect_label_in_folder_only()` - Around lines 1792-1858
3. `_is_record_label_album()` - Around lines 1917-2023

**Action:**
```python
# Delete these entire functions - they're replaced by simple check in integration code
```

### Step 2: Remove Apple Music Special Handling

**Location:** In `edit_metadata()` function around lines 1229-1381

**Lines to remove:** The entire Apple Music special case block

**Action:**
Delete lines 1229-1381 (Apple Music label handling - replaced by Phase 2A)

### Step 3: Clean Up Unused Code

**Check for any remaining references to:**
- `_detect_label_in_albumartist`
- `_detect_label_in_folder_only`
- `_is_record_label_album`

**Action:** Remove any found references

---

## Phase 4: Testing

### Test Suite

#### Test 1: War Child Records - Qobuz
```bash
brucelee94 https://www.qobuz.com/nz-en/album/help2-war-child-records/naszhk00bfnly
```

**Expected:**
- ✅ Album artist: "Various Artists"
- ✅ Track 1: "Arctic Monkeys" (no label)
- ✅ Track 2: "Depeche Mode" (no label)
- ✅ All tracks: Clean artists
- ✅ Folder: "Various Artists - HELP(2)..."
- ✅ Upload: Success

#### Test 2: War Child Records - Tidal
```bash
brucelee94 https://tidal.com/album/500752104
```

**Expected:** Same as Qobuz

#### Test 3: Self-Release Album (Should NOT Trigger)
```bash
# Find an album where artist name == label but NO keywords
# Example: "John Smith" with label "John Smith" (no "Records", "Production", etc.)
```

**Expected:**
- ❌ Should NOT retag to Various Artists
- ✅ Should keep original artist
- ✅ Should work normally

#### Test 4: Regular Album (Should NOT Trigger)
```bash
# Any normal album where artist ≠ label
```

**Expected:**
- ✅ Should work normally
- ✅ No label detection
- ✅ No changes to artist tags

### Syntax Validation

After each phase:
```bash
python3 -m py_compile brucelee94/uploader/__init__.py
```

---

## Implementation Order

**Recommended sequence:**

1. ✅ Phase 1: Complete (new functions added)
2. → Phase 2A: Qobuz/Apple integration + test
3. → Phase 2B: Tidal/Deezer integration + test
4. → Phase 3: Remove old code + syntax check
5. → Phase 4: Full testing

**Time Estimate:**
- Phase 2A: 30 min (replace + test)
- Phase 2B: 30 min (replace + test)
- Phase 3: 30 min (remove + verify)
- Phase 4: 30 min (comprehensive testing)
- **Total: 2 hours**

---

## Safety Notes

1. **Backup before each phase:** The code is version controlled, so easy to revert
2. **Test after each phase:** Don't proceed until tests pass
3. **Syntax check:** Always validate Python syntax
4. **Keep _clean_artist_string_with_label():** This helper is still used by new functions

---

## Rollback Plan

If issues arise:

```bash
# Revert to before Phase 2
git reset --hard 39e1f17

# Or revert specific changes
git checkout HEAD -- brucelee94/uploader/__init__.py
```

---

## Success Criteria

✅ **Simplicity:** ~830 lines removed, simple logic remains
✅ **Functionality:** War Child Records works for all sources
✅ **No False Positives:** Self-releases NOT affected
✅ **Maintainability:** Single code path, easy to understand
✅ **Keywords:** Prevents self-release false positives

---

## Final Checklist

- [ ] Phase 2A complete + tested
- [ ] Phase 2B complete + tested
- [ ] Phase 3 complete + syntax validated
- [ ] Phase 4 all tests passing
- [ ] Code review
- [ ] Documentation updated
- [ ] Commit and push

---

## Next Action

**To continue:**
1. Execute Phase 2A (Qobuz/Apple integration)
2. Test with War Child Records (Qobuz)
3. If passes, proceed to Phase 2B
4. Continue through all phases

**Current state:** Ready to execute Phase 2A
