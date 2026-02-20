"""
Test for Various Artists special case handling.

Tests the fix for when album artist is "Various Artists" and should be
replaced with actual track artists to prevent upload errors.
"""

def replace_various_artists_with_track_artists(artists, metadata):
    """
    Replace "Various Artists" with actual track artists when it's the only album artist.
    
    This handles special cases where files from Tidal (or scraped from Qobuz/Deezer/Apple)
    have "Various Artists" as the album artist, which causes upload failures.
    
    Args:
        artists: List of (artist_name, importance) tuples
        metadata: Metadata dict containing tracks information
    
    Returns:
        List of (artist_name, importance) tuples with "Various Artists" replaced if needed
    """
    # Check if "Various Artists" is the only album artist
    if len(artists) == 1 and artists[0][0].lower() == "various artists":
        # Extract all unique track artists (main importance only)
        track_artists = set()
        
        if "tracks" in metadata and metadata["tracks"]:
            for disc_tracks in metadata["tracks"].values():
                for track_info in disc_tracks.values():
                    if "artists" in track_info:
                        for artist_name, importance in track_info["artists"]:
                            if importance == "main":
                                track_artists.add(artist_name)
        
        # Replace "Various Artists" with track artists if we found any
        if track_artists:
            return [(artist, "main") for artist in sorted(track_artists)]
    
    # Keep original artists if:
    # - Not "Various Artists"
    # - "Various Artists" plus other artists (intentional)
    # - No track artists found (fallback)
    return artists


def test_replace_various_artists_with_track_artists():
    """Test the replace_various_artists_with_track_artists function."""
    
    print("\n" + "="*50)
    print("Testing Various Artists Replacement Logic")
    print("="*50)
    
    # Test 1: Various Artists only - should be replaced
    print("\nTest 1: Various Artists only (should be replaced)")
    artists = [("Various Artists", "main")]
    metadata = {
        "tracks": {
            1: {
                1: {"artists": [("Anaëlle Latchimy", "main")]},
                2: {"artists": [("Artist B", "main")]},
            }
        }
    }
    result = replace_various_artists_with_track_artists(artists, metadata)
    print(f"  Input: {artists}")
    print(f"  Output: {result}")
    assert result != artists, "Various Artists should have been replaced"
    assert ("Anaëlle Latchimy", "main") in result, "Track artist should be in result"
    assert ("Artist B", "main") in result, "Track artist should be in result"
    assert ("Various Artists", "main") not in result, "Various Artists should be removed"
    print("  ✓ Various Artists replaced with track artists")
    
    # Test 2: Various Artists with other artists - should NOT be replaced
    print("\nTest 2: Various Artists with other artists (should NOT be replaced)")
    artists = [("Various Artists", "main"), ("Producer", "main")]
    result = replace_various_artists_with_track_artists(artists, metadata)
    print(f"  Input: {artists}")
    print(f"  Output: {result}")
    assert result == artists, "Should keep original when Various Artists is not alone"
    print("  ✓ Kept original (Various Artists + other artists)")
    
    # Test 3: No Various Artists - should remain unchanged
    print("\nTest 3: No Various Artists (should remain unchanged)")
    artists = [("Normal Artist", "main")]
    result = replace_various_artists_with_track_artists(artists, metadata)
    print(f"  Input: {artists}")
    print(f"  Output: {result}")
    assert result == artists, "Should remain unchanged when no Various Artists"
    print("  ✓ Unchanged (no Various Artists)")
    
    # Test 4: Various Artists with multiple unique track artists
    print("\nTest 4: Various Artists with multiple unique track artists")
    artists = [("Various Artists", "main")]
    metadata = {
        "tracks": {
            1: {
                1: {"artists": [("Artist A", "main")]},
                2: {"artists": [("Artist B", "main")]},
                3: {"artists": [("Artist A", "main")]},  # Duplicate
                4: {"artists": [("Artist C", "main")]},
            }
        }
    }
    result = replace_various_artists_with_track_artists(artists, metadata)
    print(f"  Input: {artists}")
    print(f"  Output: {result}")
    # Should have 3 unique artists (A, B, C), sorted
    assert len(result) == 3, f"Should have 3 unique artists, got {len(result)}"
    artist_names = [a for a, i in result]
    assert "Artist A" in artist_names
    assert "Artist B" in artist_names
    assert "Artist C" in artist_names
    assert ("Various Artists", "main") not in result
    print("  ✓ All unique track artists collected and sorted")
    
    # Test 5: Various Artists with guest artists (should only use main)
    print("\nTest 5: Various Artists with guest artists (should only use main)")
    artists = [("Various Artists", "main")]
    metadata = {
        "tracks": {
            1: {
                1: {"artists": [("Main Artist", "main"), ("Guest", "guest")]},
                2: {"artists": [("Main Artist", "main"), ("Another Guest", "guest")]},
            }
        }
    }
    result = replace_various_artists_with_track_artists(artists, metadata)
    print(f"  Input: {artists}")
    print(f"  Output: {result}")
    # Should only have Main Artist (importance main), not guests
    assert len(result) == 1, f"Should have 1 main artist, got {len(result)}"
    assert result[0] == ("Main Artist", "main"), "Should only include main importance"
    print("  ✓ Only main importance artists included")
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_replace_various_artists_with_track_artists()
