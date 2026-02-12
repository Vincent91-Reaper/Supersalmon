# Retagging Feature Documentation

## Overview

BruceLee94's retagging feature has been improved to be more intelligent about when to retag files. The new logic preserves file tags that already have the correct main artist, even when additional featured artists are present.

## New Behavior

### When Files Are NOT Retagged

Files will **NOT** be retagged if:
- The main artist(s) from the scraped metadata are already present in the file tags
- This applies even if the file has additional featured/guest artists

**Example Scenarios (NO RETAG):**
```
File has: "Artist A, Artist B"
Metadata says main artist is: "Artist A"
→ NO RETAG (main artist present, keeps Artist B as well)

File has: "Artist A & Artist B feat. Artist C"
Metadata says main artists are: "Artist A & Artist B"
→ NO RETAG (both main artists present, keeps Artist C as well)

File has: "Artist A"
Metadata says main artist is: "Artist A"
→ NO RETAG (exact match)
```

### When Files ARE Retagged

Files will be retagged if:
- The main artist is missing or empty in the file tags
- One or more main artists from the metadata are not present in the file

**Example Scenarios (RETAG):**
```
File has: "Artist B"
Metadata says main artist is: "Artist A"
→ RETAG to "Artist A" (main artist missing)

File has: "" (empty)
Metadata says main artist is: "Artist A"
→ RETAG to "Artist A" (no artist tagged)

File has: "Artist A, Artist C"
Metadata says main artists are: "Artist A & Artist B"
→ RETAG to "Artist A & Artist B" (Artist B is missing)
```

## Technical Details

### Artist Normalization

The system normalizes artist strings by:
1. Recognizing "feat.", "featuring", "ft.", "ft" as separators for featured artists
2. Splitting on common separators: `&`, `,`, `;`
3. Converting to lowercase for case-insensitive comparison
4. Removing extra whitespace

### Main Artist Detection

The `_main_artists_present()` function checks if main artists are a **subset** of the file's artists:
- If main artists ⊆ file artists → No retag needed
- If main artists ⊄ file artists → Retag required

This allows files to keep additional artists (like featured artists) without being overwritten.

## Benefits

1. **Preserves User Customizations**: If users have manually added featured artists to their files, these won't be overwritten
2. **Reduces Unnecessary Changes**: Only files with genuinely missing or incorrect main artists are retagged
3. **Maintains Flexibility**: Files can have more detailed artist information than the basic metadata

## Special Cases

### Various Artists

If the scraped metadata indicates "Various Artists", the retagging is skipped entirely to preserve the original per-track artist information.

### Apple Music / iTunes

For Apple Music sources, artist preservation is enabled by default (via the `preserve_artists` flag), preventing any artist retagging.

### Classical Albums

For classical music, both main artists and composers are considered when determining if retagging is needed.

## Testing

A comprehensive test suite (`test_retagging.py`) validates:
- Artist normalization with various separators
- Main artist presence detection with different scenarios
- Real-world retagging scenarios

Run the tests:
```bash
python test_retagging.py
```

## Configuration

This behavior is automatic and requires no configuration. The retagging logic applies whenever:
- Files are uploaded using BruceLee94
- Metadata is scraped from supported sources
- The `tag_files()` function is called

## Migration Notes

### Previous Behavior

The old logic would retag files if the artist strings didn't match exactly (ignoring order and separators). This meant:
- "Artist A, Artist B" vs "Artist A" → Would retag (removing Artist B)
- Files with additional featured artists would lose that information

### New Behavior

The new logic only checks if main artists are present:
- "Artist A, Artist B" vs "Artist A" → NO retag (Artist A is present)
- Files with additional featured artists keep them

This is a non-breaking change that makes the system more conservative about modifying file tags.
