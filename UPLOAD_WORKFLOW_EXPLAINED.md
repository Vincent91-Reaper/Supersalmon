# BruceLee94 Upload Workflow Explained

## Overview

This document explains exactly what happens during the upload process, with a focus on **when and how** metadata (label, catalog number, tags, etc.) is submitted to RED.

## ✅ Key Clarification: Label and Catalog Number

**IMPORTANT:** The label and catalog number are **included in the initial torrent upload**, NOT added afterwards.

### What Gets Uploaded When

#### Phase 1: Initial Torrent Upload (FIRST)
The torrent is uploaded to RED **immediately** with ALL essential metadata:

**Included in initial upload:**
- ✅ **Label** (`record_label` and `remaster_record_label`)
- ✅ **Catalog number** (`catalogue_number` and `remaster_catalogue_number`)
- ✅ Album title
- ✅ Artist information
- ✅ Year and release year
- ✅ Edition title
- ✅ Format (FLAC, MP3, etc.)
- ✅ Encoding (16bit, 24bit, etc.)
- ✅ Source (WEB, CD, Vinyl, etc.)
- ✅ **Tags** (genre tags)
- ✅ Release description (bitrate/bit depth info)
- ✅ .torrent file
- ✅ Log files (for CD rips)

**NOT included in initial upload:**
- ❌ Cover image URL (uploaded to ptpimg later)
- ❌ Album description with tracklist (added later for new groups)

#### Phase 2: Post-Upload Enhancements (AFTER)
After the torrent is successfully uploaded and live on RED:

1. **Cover Image Upload:**
   - Image is uploaded to ptpimg
   - URL is obtained

2. **Description Addition (New Groups Only):**
   - Album description with full tracklist is generated
   - Cover image URL and description are added to the group
   - This only happens if you created a NEW group (not adding to existing)

## Upload Process Step-by-Step

### Detailed Workflow

```
1. User runs: brucelee94 up /path/to/album -s WEB
   ↓
2. BruceLee94 collects file metadata
   ↓
3. User provides source URL (Tidal, Qobuz, etc.)
   ↓
4. Metadata is scraped from source
   - Label extracted
   - Catalog number extracted
   - Tags/genres extracted
   - Artist information extracted
   ↓
5. Files are retagged if needed (artists, label, catalog)
   ↓
6. Folder structure check (if needed)
   ↓
7. Torrent generation
   ↓
8. ⚡ PHASE 1: IMMEDIATE UPLOAD ⚡
   - Upload torrent to RED
   - Include: label, catalog, tags, ALL metadata
   - Exclude: cover URL (not uploaded yet)
   ↓
9. ✅ Torrent is now LIVE on RED
   ↓
10. ⚡ PHASE 2: POST-UPLOAD ENHANCEMENTS ⚡
    - Upload cover to ptpimg
    - Get cover URL
    - Add description + cover to group (new groups only)
    ↓
11. ✅ Upload complete!
```

### Why This Approach?

**Speed Optimization:**
- Uploading the torrent FIRST (without cover) is fastest
- Maximizes chance of being the first uploader
- Cover upload to ptpimg can take time
- RED gets your torrent immediately with all required info

**Compliance:**
- All RED-required fields are in Phase 1
- Label and catalog are never missing
- Cover and description are nice-to-haves added after

## Code References

### Initial Upload with Label and Catalog

From `brucelee94/uploader/upload.py` (lines 100-148):

```python
def compile_data_new_group(...):
    """Compile data for new torrent group upload."""
    data = {
        "submit": True,
        "type": 0,
        "title": metadata["title"],
        "artists[]": [a[0] for a in metadata["artists"]],
        "year": metadata["group_year"],
        "record_label": metadata["label"],              # ← Label included!
        "catalogue_number": generate_catno(metadata),    # ← Catalog included!
        "releasetype": ...,
        "remaster_year": metadata["year"],
        "remaster_record_label": metadata["label"],      # ← Also here!
        "remaster_catalogue_number": generate_catno(...), # ← And here!
        "format": metadata["format"],
        "bitrate": metadata["encoding"],
        "media": metadata["source"],
        "tags": metadata["tags"],                        # ← Tags included!
        "album_desc": generate_description(...),
        "release_desc": generate_t_description(...),
    }
    # Image is NOT included in initial upload (None is passed)
    if cover_url:  # This is None during initial upload
        data["image"] = cover_url
    return data
```

### Post-Upload Cover Addition

From `brucelee94/uploader/__init__.py` (lines 508-553):

```python
# Phase 1: Upload torrent WITHOUT cover URL
torrent_id, group_id, ... = upload_and_report(
    gazelle_site,
    path,
    group_id,
    metadata,
    None,  # ← No cover URL in initial upload
    track_data,
    ...
)

# Torrent is now live on RED!

# Phase 2: Add cover and description (new groups only)
if cover_to_upload_later and is_new_group:
    click.secho("Uploading cover image to ptpimg...", fg="cyan")
    cover_url = upload_cover(cover_to_upload_later)
    
    click.secho("Updating torrent group with cover image and description...", fg="cyan")
    album_desc = generate_description(track_data, metadata)
    
    loop.run_until_complete(
        gazelle_site.update_group_cover_image(group_id, cover_url, album_desc)
    )
    click.secho("Cover image and description added successfully!", fg="green")
```

## Common Questions

### Q: Is the label missing when I upload?
**A: No!** The label is included in the initial upload. It's in the `record_label` and `remaster_record_label` fields.

### Q: Is the catalog number missing when I upload?
**A: No!** The catalog number is included in the initial upload. It's in the `catalogue_number` and `remaster_catalogue_number` fields.

### Q: What about tags/genres?
**A: Also included!** Tags are in the `tags` field of the initial upload.

### Q: Why does the cover come later?
**A: Speed!** Uploading to ptpimg takes time. The torrent uploads faster without waiting for the cover. The cover is added immediately after the torrent is live.

### Q: What if I'm adding to an existing group?
**A: Same process!** Label, catalog, and tags are still in the initial upload. The only difference is that album description and cover are NOT updated (to avoid overwriting existing group info).

### Q: Can I verify this myself?
**A: Yes!** After uploading, check your RED torrent page immediately. You'll see:
- Label is present
- Catalog number is present  
- Tags are present
- Cover appears moments later (if new group)

## Summary

| Field | When Added | Always Present? |
|-------|------------|-----------------|
| Label | Phase 1 (Initial Upload) | ✅ Yes |
| Catalog Number | Phase 1 (Initial Upload) | ✅ Yes |
| Tags/Genres | Phase 1 (Initial Upload) | ✅ Yes |
| Artist Info | Phase 1 (Initial Upload) | ✅ Yes |
| Format/Encoding | Phase 1 (Initial Upload) | ✅ Yes |
| Release Description | Phase 1 (Initial Upload) | ✅ Yes |
| Cover Image | Phase 2 (Post-Upload) | ✅ Yes (new groups) |
| Album Description | Phase 2 (Post-Upload) | ✅ Yes (new groups) |

## Verification

To verify this yourself:

1. Upload an album
2. Check the torrent page on RED immediately after "Successfully uploaded" message
3. You'll see label and catalog are already there
4. A few seconds later, cover and description appear (for new groups)

The two-phase approach ensures:
- ✅ Fastest possible upload
- ✅ All required metadata present from the start
- ✅ Enhanced information (cover/description) added promptly
- ✅ No missing or delayed label/catalog information
