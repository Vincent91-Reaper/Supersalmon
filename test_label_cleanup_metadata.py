#!/usr/bin/env python3
"""
Tests for label cleanup in metadata["artists"] and metadata["tracks"].

These tests cover the 2nd special case scenario:
- "Dj Twi$t II - Inner City Pressure (2025)" where "Former City Records" is included
  as an artist by the scraper, but should only be the label, not an artist.

Two scenarios are tested:
1. SPECIAL CASE 1 path: albumartist = "Dj Twi$t II, Former City Records"
   → detection fires, both metadata["artists"] AND metadata["tracks"] are cleaned
2. FALLBACK CLEANUP path: albumartist = "Dj Twi$t II" (clean), but scraper
   included "Former City Records" as an artist in metadata
   → fallback cleanup removes label from metadata["artists"] and metadata["tracks"]
"""


def _remove_label_from_metadata_artists(metadata_artists, label_to_remove):
    """
    Simulate the SPECIAL CASE 1 metadata["artists"] cleanup logic.
    Case-insensitive comparison (as fixed in the new code).
    """
    label_lower = label_to_remove.lower().strip()
    cleaned = []
    for artist, importance in metadata_artists:
        if artist.lower().strip() != label_lower:
            if ',' in artist:
                parts = [p.strip() for p in artist.split(',') if p.strip()]
                parts = [p for p in parts if p.lower().strip() != label_lower]
                if parts:
                    cleaned_artist = ', '.join(parts) if len(parts) > 1 else parts[0]
                    cleaned.append((cleaned_artist, importance))
            else:
                cleaned.append((artist, importance))
    return cleaned


def _remove_label_from_metadata_tracks(metadata_tracks, label_to_remove):
    """
    Simulate the new metadata["tracks"] cleanup logic (added in this fix).
    """
    label_lower = label_to_remove.lower().strip()
    for disc_tracks in metadata_tracks.values():
        for track_meta in disc_tracks.values():
            if "artists" in track_meta:
                track_meta["artists"] = [
                    (artist, imp) for artist, imp in track_meta["artists"]
                    if artist.lower().strip() != label_lower
                ]
    return metadata_tracks


def _fallback_cleanup(metadata, extracted_label):
    """
    Simulate the FALLBACK CLEANUP logic (added in this fix).
    Removes label from metadata["artists"] and metadata["tracks"] when
    the label has label keywords and appears in metadata["artists"].
    """
    if not extracted_label or extracted_label.lower() == "self-released":
        return metadata, False

    fallback_label_keywords = [
        "records", "music", "entertainment", "label", "recordings",
        "productions", "media", "group", "collective", "imprint"
    ]
    label_has_keyword = any(kw in extracted_label.lower() for kw in fallback_label_keywords)
    if not label_has_keyword:
        return metadata, False

    extracted_label_lower = extracted_label.lower().strip()
    label_in_artists = any(
        artist.lower().strip() == extracted_label_lower
        for artist, importance in metadata.get("artists", [])
    )
    if not label_in_artists:
        return metadata, False

    # Clean metadata["artists"]
    metadata["artists"] = [
        (artist, imp) for artist, imp in metadata.get("artists", [])
        if artist.lower().strip() != extracted_label_lower
    ]

    # Clean metadata["tracks"]
    if metadata.get("tracks"):
        for disc_tracks in metadata["tracks"].values():
            for track_meta in disc_tracks.values():
                if "artists" in track_meta:
                    track_meta["artists"] = [
                        (artist, imp) for artist, imp in track_meta["artists"]
                        if artist.lower().strip() != extracted_label_lower
                    ]

    return metadata, True


# ─────────────────────────────────────────────────────────────────────────────
# SPECIAL CASE 1: metadata["artists"] cleaning (case-insensitive)
# ─────────────────────────────────────────────────────────────────────────────

def test_special_case1_metadata_artists_cleaned_exact_case():
    """
    SPECIAL CASE 1: Label is removed from metadata["artists"] when cases match.
    """
    metadata_artists = [
        ("Dj Twi$t II", "main"),
        ("Former City Records", "main"),
    ]
    cleaned = _remove_label_from_metadata_artists(metadata_artists, "Former City Records")
    assert cleaned == [("Dj Twi$t II", "main")], f"Expected only Dj Twi$t II, got {cleaned}"
    print("✓ SPECIAL CASE 1 - metadata artists cleaned (exact case)")


def test_special_case1_metadata_artists_cleaned_different_case():
    """
    SPECIAL CASE 1: Label is removed from metadata["artists"] even with case mismatch.
    This tests the case-insensitive fix.
    """
    # artist stored as lowercase (from scraper), label from albumartist tag (title case)
    metadata_artists = [
        ("Dj Twi$t II", "main"),
        ("former city records", "main"),   # lowercase from scraper
    ]
    cleaned = _remove_label_from_metadata_artists(metadata_artists, "Former City Records")
    assert cleaned == [("Dj Twi$t II", "main")], f"Expected only Dj Twi$t II, got {cleaned}"
    print("✓ SPECIAL CASE 1 - metadata artists cleaned (different case)")


def test_special_case1_metadata_artists_cleaned_comma_string():
    """
    SPECIAL CASE 1: Label is removed from metadata["artists"] when stored as comma-separated string.
    """
    metadata_artists = [
        ("Dj Twi$t II, Former City Records", "main"),
    ]
    cleaned = _remove_label_from_metadata_artists(metadata_artists, "Former City Records")
    assert cleaned == [("Dj Twi$t II", "main")], f"Expected only Dj Twi$t II, got {cleaned}"
    print("✓ SPECIAL CASE 1 - metadata artists cleaned (comma-separated string)")


# ─────────────────────────────────────────────────────────────────────────────
# SPECIAL CASE 1: metadata["tracks"] cleaning (NEW)
# ─────────────────────────────────────────────────────────────────────────────

def test_special_case1_metadata_tracks_cleaned():
    """
    SPECIAL CASE 1: Label is removed from metadata["tracks"] per-track artists.
    This is the primary new fix - metadata["tracks"] was not previously cleaned.
    """
    metadata_tracks = {
        1: {
            1: {"title": "Track 1", "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main")]},
            2: {"title": "Track 2", "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main")]},
        }
    }
    cleaned_tracks = _remove_label_from_metadata_tracks(metadata_tracks, "Former City Records")

    for disc_tracks in cleaned_tracks.values():
        for track_meta in disc_tracks.values():
            for artist, imp in track_meta["artists"]:
                assert artist != "Former City Records", \
                    f"Former City Records should have been removed from track artists, but found: {track_meta['artists']}"
    print("✓ SPECIAL CASE 1 - metadata tracks cleaned")


def test_special_case1_metadata_tracks_cleaned_case_insensitive():
    """
    SPECIAL CASE 1: Label is removed from metadata["tracks"] case-insensitively.
    """
    metadata_tracks = {
        1: {
            1: {"title": "Track 1", "artists": [("Dj Twi$t II", "main"), ("former city records", "main")]},
        }
    }
    cleaned_tracks = _remove_label_from_metadata_tracks(metadata_tracks, "Former City Records")

    track_artists = cleaned_tracks[1][1]["artists"]
    assert len(track_artists) == 1, f"Expected 1 artist, got {track_artists}"
    assert track_artists[0][0] == "Dj Twi$t II", f"Expected Dj Twi$t II, got {track_artists}"
    print("✓ SPECIAL CASE 1 - metadata tracks cleaned (case-insensitive)")


def test_special_case1_metadata_tracks_preserves_other_artists():
    """
    SPECIAL CASE 1: Other artists are preserved when removing label from metadata["tracks"].
    """
    metadata_tracks = {
        1: {
            1: {"title": "Track 1", "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main"), ("Some Guest", "guest")]},
        }
    }
    cleaned_tracks = _remove_label_from_metadata_tracks(metadata_tracks, "Former City Records")

    track_artists = cleaned_tracks[1][1]["artists"]
    artist_names = [a for a, _ in track_artists]
    assert "Dj Twi$t II" in artist_names, "Dj Twi$t II should be preserved"
    assert "Some Guest" in artist_names, "Some Guest should be preserved"
    assert "Former City Records" not in artist_names, "Former City Records should be removed"
    print("✓ SPECIAL CASE 1 - metadata tracks preserves other artists")


# ─────────────────────────────────────────────────────────────────────────────
# FALLBACK CLEANUP: label in metadata but not in albumartist (Qobuz/scraper path)
# ─────────────────────────────────────────────────────────────────────────────

def test_fallback_cleanup_removes_label_from_artists():
    """
    FALLBACK CLEANUP: Label is removed from metadata["artists"] when scraper included it.
    This handles the case where albumartist tag is clean but scraper added label as artist.
    """
    metadata = {
        "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main")],
        "tracks": {
            1: {
                1: {"title": "Inner City Pressure", "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main")]},
            }
        }
    }
    metadata, cleaned = _fallback_cleanup(metadata, "Former City Records")

    assert cleaned is True, "Fallback cleanup should have fired"
    assert metadata["artists"] == [("Dj Twi$t II", "main")], \
        f"Expected only Dj Twi$t II in metadata artists, got {metadata['artists']}"
    print("✓ FALLBACK CLEANUP - label removed from metadata artists")


def test_fallback_cleanup_removes_label_from_tracks():
    """
    FALLBACK CLEANUP: Label is also removed from metadata["tracks"] per-track artists.
    """
    metadata = {
        "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main")],
        "tracks": {
            1: {
                1: {"title": "Inner City Pressure", "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main")]},
                2: {"title": "Another Track", "artists": [("Dj Twi$t II", "main"), ("Former City Records", "main")]},
            }
        }
    }
    metadata, cleaned = _fallback_cleanup(metadata, "Former City Records")

    assert cleaned is True
    for disc_tracks in metadata["tracks"].values():
        for track_meta in disc_tracks.values():
            for artist, imp in track_meta["artists"]:
                assert artist != "Former City Records", \
                    f"Former City Records should be removed from track artists, but found: {track_meta['artists']}"
    print("✓ FALLBACK CLEANUP - label removed from track-level metadata")


def test_fallback_cleanup_no_trigger_without_label_keywords():
    """
    FALLBACK CLEANUP: Should NOT trigger when extracted_label has no label keywords.
    This prevents false positives.
    """
    metadata = {
        "artists": [("Dj Twi$t II", "main"), ("Some Artist", "main")],
        "tracks": {}
    }
    # "Some Artist" has no label keywords
    metadata, cleaned = _fallback_cleanup(metadata, "Some Artist")

    assert cleaned is False, "Fallback cleanup should NOT fire for non-label artist names"
    assert ("Some Artist", "main") in metadata["artists"], "Some Artist should be preserved"
    print("✓ FALLBACK CLEANUP - no trigger without label keywords")


def test_fallback_cleanup_no_trigger_for_self_released():
    """
    FALLBACK CLEANUP: Should NOT trigger for 'Self-Released' label.
    """
    metadata = {
        "artists": [("Dj Twi$t II", "main")],
        "tracks": {}
    }
    metadata, cleaned = _fallback_cleanup(metadata, "Self-Released")

    assert cleaned is False, "Fallback cleanup should NOT fire for Self-Released"
    print("✓ FALLBACK CLEANUP - no trigger for Self-Released")


def test_fallback_cleanup_no_trigger_when_label_not_in_artists():
    """
    FALLBACK CLEANUP: Should NOT trigger when label is not in metadata["artists"].
    """
    metadata = {
        "artists": [("Dj Twi$t II", "main")],
        "tracks": {}
    }
    metadata, cleaned = _fallback_cleanup(metadata, "Former City Records")

    assert cleaned is False, "Fallback cleanup should NOT fire when label not in artists"
    assert metadata["artists"] == [("Dj Twi$t II", "main")], "Artists should be unchanged"
    print("✓ FALLBACK CLEANUP - no trigger when label not in artists")


def test_fallback_cleanup_case_insensitive():
    """
    FALLBACK CLEANUP: Should handle case-insensitive matching.
    """
    metadata = {
        "artists": [("Dj Twi$t II", "main"), ("FORMER CITY RECORDS", "main")],
        "tracks": {
            1: {
                1: {"title": "Track 1", "artists": [("Dj Twi$t II", "main"), ("FORMER CITY RECORDS", "main")]},
            }
        }
    }
    metadata, cleaned = _fallback_cleanup(metadata, "Former City Records")

    assert cleaned is True, "Fallback cleanup should fire (case-insensitive)"
    assert metadata["artists"] == [("Dj Twi$t II", "main")], \
        f"Expected only Dj Twi$t II, got {metadata['artists']}"
    print("✓ FALLBACK CLEANUP - case-insensitive matching")


def test_fallback_cleanup_guest_label_also_removed():
    """
    FALLBACK CLEANUP: Label appearing as guest importance is also removed.
    This handles the Qobuz case where label appears with 'guest' importance.
    """
    metadata = {
        "artists": [("Dj Twi$t II", "main"), ("Former City Records", "guest")],
        "tracks": {
            1: {
                1: {"title": "Track 1", "artists": [("Dj Twi$t II", "main"), ("Former City Records", "guest")]},
            }
        }
    }
    metadata, cleaned = _fallback_cleanup(metadata, "Former City Records")

    assert cleaned is True, "Fallback cleanup should fire for guest-importance label too"
    assert metadata["artists"] == [("Dj Twi$t II", "main")], \
        f"Expected only Dj Twi$t II, got {metadata['artists']}"
    print("✓ FALLBACK CLEANUP - guest-importance label removed")


# ─────────────────────────────────────────────────────────────────────────────
# Combined scenario: the full "Dj Twi$t II - Inner City Pressure" use case
# ─────────────────────────────────────────────────────────────────────────────

def test_full_dj_twist_scenario_special_case1():
    """
    Full scenario for 'Dj Twi$t II - Inner City Pressure' when SPECIAL CASE 1 fires.
    albumartist = "Dj Twi$t II, Former City Records" (triggers SPECIAL CASE 1)
    After fix: metadata["artists"] = [("Dj Twi$t II", "main")],
               metadata["tracks"] per-track artists have "Former City Records" removed.
    """
    label = "Former City Records"
    metadata_artists = [("Dj Twi$t II", "main"), (label, "main")]
    metadata_tracks = {
        1: {
            i: {"title": f"Track {i}", "artists": [("Dj Twi$t II", "main"), (label, "main")]}
            for i in range(1, 6)
        }
    }

    # Simulate SPECIAL CASE 1 cleanup
    cleaned_artists = _remove_label_from_metadata_artists(metadata_artists, label)
    cleaned_tracks = _remove_label_from_metadata_tracks(metadata_tracks, label)

    # Verify metadata["artists"]
    assert cleaned_artists == [("Dj Twi$t II", "main")], \
        f"metadata['artists'] should only have Dj Twi$t II, got {cleaned_artists}"

    # Verify metadata["tracks"]
    for disc_tracks in cleaned_tracks.values():
        for track_meta in disc_tracks.values():
            artist_names = [a for a, _ in track_meta["artists"]]
            assert "Dj Twi$t II" in artist_names, "Dj Twi$t II should remain"
            assert label not in artist_names, f"{label} should be removed from track artists"

    print("✓ Full Dj Twi$t II scenario (SPECIAL CASE 1 path)")


def test_full_dj_twist_scenario_fallback():
    """
    Full scenario for 'Dj Twi$t II - Inner City Pressure' with FALLBACK CLEANUP.
    albumartist = "Dj Twi$t II" (clean), but Qobuz scraper included label as artist.
    After fix: metadata["artists"] = [("Dj Twi$t II", "main")],
               metadata["tracks"] per-track artists have "Former City Records" removed.
    """
    label = "Former City Records"
    metadata = {
        "artists": [("Dj Twi$t II", "main"), (label, "main")],
        "tracks": {
            1: {
                i: {"title": f"Track {i}", "artists": [("Dj Twi$t II", "main"), (label, "main")]}
                for i in range(1, 6)
            }
        },
        "label": label,
    }

    # Simulate FALLBACK CLEANUP
    metadata, cleaned = _fallback_cleanup(metadata, label)

    assert cleaned is True, "Fallback cleanup should have fired"
    assert metadata["artists"] == [("Dj Twi$t II", "main")], \
        f"metadata['artists'] should only have Dj Twi$t II, got {metadata['artists']}"

    for disc_tracks in metadata["tracks"].values():
        for track_meta in disc_tracks.values():
            artist_names = [a for a, _ in track_meta["artists"]]
            assert "Dj Twi$t II" in artist_names, "Dj Twi$t II should remain"
            assert label not in artist_names, f"{label} should be removed from track artists"

    print("✓ Full Dj Twi$t II scenario (FALLBACK CLEANUP path)")


if __name__ == "__main__":
    test_special_case1_metadata_artists_cleaned_exact_case()
    test_special_case1_metadata_artists_cleaned_different_case()
    test_special_case1_metadata_artists_cleaned_comma_string()
    test_special_case1_metadata_tracks_cleaned()
    test_special_case1_metadata_tracks_cleaned_case_insensitive()
    test_special_case1_metadata_tracks_preserves_other_artists()
    test_fallback_cleanup_removes_label_from_artists()
    test_fallback_cleanup_removes_label_from_tracks()
    test_fallback_cleanup_no_trigger_without_label_keywords()
    test_fallback_cleanup_no_trigger_for_self_released()
    test_fallback_cleanup_no_trigger_when_label_not_in_artists()
    test_fallback_cleanup_case_insensitive()
    test_fallback_cleanup_guest_label_also_removed()
    test_full_dj_twist_scenario_special_case1()
    test_full_dj_twist_scenario_fallback()
    print("\n✓ All label cleanup metadata tests passed!")
