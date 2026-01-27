# Folder Structure Check Optimization

## Overview
This document describes the optimization of the folder structure check in brucelee94 to reduce unnecessary checks while maintaining full compliance with RED upload rules.

## Problem Statement
1. **Need smart detection**: Run folder structure check only when needed (files >180 chars)
2. **Genre context**: 
   - Qobuz, Deezer, Apple Music, Beatport store genre info
   - Classical albums often have long filenames (>180 chars)
   - Tidal doesn't store genre info in files
3. **Upload priority**: Upload torrent first, then fill in metadata/cover/description

## Implementation

### 1. New Helper Function: `has_long_file_paths()`

Located in `brucelee94/tagger/folderstructure.py`:

```python
def has_long_file_paths(path, max_length=180):
    """
    Check if any file paths in the directory exceed the specified length.
    Returns True if any file path is longer than max_length characters.
    """
```

**What it does:**
- Walks through the entire directory tree
- Checks both folder paths and file paths
- Returns `True` immediately if any path exceeds 180 characters
- Returns `False` if all paths are within limits
- Uses same calculation method as the full structure check
- Efficient: stops on first long path found

### 2. Updated `check_folder_structure()` Logic

The function now implements smart detection:

#### For Tidal URLs (`is_tidal=True`)
- **Always runs the check**
- Reason: Tidal files don't contain genre information
- Can't determine if album is classical (which often has long filenames)

#### For Other URL Sources (`from_url=True`)
Sources: Qobuz, Deezer, Apple Music, Beatport
- **First checks if files have long paths** using `has_long_file_paths()`
- **Only runs full check if long paths detected**
- **Skips check entirely** if all filenames are normal length
- Reason: These sources include genre info, so we know context

#### For Non-URL Uploads (`from_url=False`)
- **Checks if classical genre OR has long paths**
- Runs check if either condition is true
- Skips check if neither condition is true
- Reason: Classical albums need checking, others only if they have long paths

### 3. Upload Workflow (Already Optimized)

The upload workflow in `brucelee94/uploader/__init__.py` already implements the requested priority:

1. **Upload torrent FIRST** (line 508-524)
   - No cover URL included
   - Fastest possible upload
   - Maximizes chance of being first uploader

2. **Upload cover AFTER** (line 544-545)
   - Cover uploaded to ptpimg after torrent is live

3. **Add description** (line 546-553)
   - Group description added with cover
   - Only for new groups (prevents overwriting existing descriptions)

## Benefits

### Performance
- Significantly reduces unnecessary folder structure checks
- Most albums with normal filenames skip the check entirely
- Only checks when actually needed

### Compliance
- Maintains full compliance with RED upload rules
- Still catches all problematic file path lengths
- No risk of uploading non-compliant torrents

### User Experience
- Faster upload workflow
- Less waiting for checks on normal albums
- Still validates when necessary (Tidal, classical, long paths)

## Testing Scenarios

### Scenario 1: Qobuz URL - Short Filenames
- **Expected**: Skip folder structure check
- **Why**: Has genre info, files are normal length

### Scenario 2: Qobuz URL - Long Filenames (>180 chars)
- **Expected**: Run folder structure check
- **Why**: Long paths detected by `has_long_file_paths()`

### Scenario 3: Tidal URL - Any Filenames
- **Expected**: Always run folder structure check
- **Why**: No genre info available, can't determine if classical

### Scenario 4: Classical Album (Non-URL)
- **Expected**: Run folder structure check
- **Why**: Classical albums often have long filenames

### Scenario 5: Non-Classical Album (Non-URL) - Short Filenames
- **Expected**: Skip folder structure check
- **Why**: Not classical, no long paths detected

### Scenario 6: Non-Classical Album (Non-URL) - Long Filenames
- **Expected**: Run folder structure check
- **Why**: Long paths detected by `has_long_file_paths()`

## Code Locations

### Modified Files
- `brucelee94/tagger/folderstructure.py`
  - Added `has_long_file_paths()` function (lines 11-27)
  - Updated `check_folder_structure()` logic (lines 30-56)

### Call Sites (No Changes Needed)
1. `brucelee94/uploader/__init__.py` line 373 (Tidal)
   - Passes `is_tidal=True, from_url=True` ✓
2. `brucelee94/uploader/__init__.py` line 691 (Other URLs)
   - Passes `from_url=bool(source_url)` ✓
3. `brucelee94/tagger/__init__.py` line 93 (Non-URL)
   - No `from_url` parameter (defaults to False) ✓

## Technical Details

### Path Length Calculation
Both `has_long_file_paths()` and `_check_path_lengths()` use the same calculation:
```python
root_len = len(cfg.directory.download_directory) + 1
filepathlen = len(filepath) - root_len
if filepathlen > 180:
    # Path is too long
```

This ensures consistency between the detection and the actual check.

### Early Exit Optimization
The `has_long_file_paths()` function returns `True` as soon as it finds a single path >180 chars, avoiding unnecessary filesystem traversal.

## Conclusion

This optimization significantly improves the upload workflow while maintaining full compliance with RED's upload rules. The smart detection approach balances performance with safety, checking only when necessary based on file characteristics and source context.
