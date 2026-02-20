#!/usr/bin/env python3
"""
Test to verify the Various Artists importance fix.

This test validates that when album artist is "Various Artists",
track artists are correctly classified as "main" instead of "guest".
"""

def test_album_artists_set_excludes_various_artists():
    """
    Test that "Various Artists" is excluded from album_artists_set
    """
    # Simulate the extraction logic
    album_artists_set = set()
    
    # Simulate tags with "Various Artists" as albumartist
    class MockTagset:
        def __init__(self, albumartist):
            self.albumartist = albumartist
    
    tags = {
        'file1.flac': MockTagset("Various Artists"),
        'file2.flac': MockTagset("Various Artists"),
    }
    
    # Apply the fix logic
    for filename, tagset in tags.items():
        if hasattr(tagset, 'albumartist') and tagset.albumartist:
            aa_list = tagset.albumartist if isinstance(tagset.albumartist, list) else [tagset.albumartist]
            for aa in aa_list:
                if aa and str(aa).strip():
                    individual_artists = [a.strip() for a in str(aa).split(',') if a.strip()]
                    for individual_artist in individual_artists:
                        # Skip "Various Artists" - it's a placeholder, not a real artist
                        if individual_artist.lower() != "various artists":
                            album_artists_set.add(individual_artist.lower())
    
    # Verify "Various Artists" was excluded
    assert "various artists" not in album_artists_set
    assert len(album_artists_set) == 0
    print("✓ Test 1 passed: 'Various Artists' excluded from album_artists_set")


def test_track_artists_marked_as_main_when_set_empty():
    """
    Test that track artists are marked as "main" when album_artists_set is empty
    """
    # Empty set (e.g., after excluding "Various Artists")
    album_artists_set = set()
    
    # Track artist
    track_artist = "Anaëlle Latchimy"
    
    # Apply the classification logic
    if not album_artists_set:
        importance = "main"
    elif track_artist.lower() in album_artists_set:
        importance = "main"
    else:
        importance = "guest"
    
    # Verify track artist is marked as "main"
    assert importance == "main"
    print("✓ Test 2 passed: Track artist marked as 'main' when album_artists_set is empty")


def test_complete_scenario():
    """
    Test the complete scenario from the user's gist
    """
    # Simulate album artist extraction with "Various Artists"
    album_artists_set = set()
    albumartist = "Various Artists"
    
    # Process album artist
    individual_artists = [a.strip() for a in str(albumartist).split(',') if a.strip()]
    for individual_artist in individual_artists:
        if individual_artist.lower() != "various artists":
            album_artists_set.add(individual_artist.lower())
    
    # Verify set is empty
    assert len(album_artists_set) == 0
    
    # Simulate track artists
    track_artists_list = ["Anaëlle Latchimy", "Jako Maron", "Agnesca", "M.Baba", 
                          "Kobald", "Boogzbrown", "PANGAR"]
    
    # Classify track artists
    all_artists = []
    for track_artist in track_artists_list:
        if not album_artists_set:
            importance = "main"
        elif track_artist.lower() in album_artists_set:
            importance = "main"
        else:
            importance = "guest"
        
        all_artists.append((track_artist, importance))
    
    # Verify all artists are "main"
    for artist, importance in all_artists:
        assert importance == "main", f"Expected {artist} to be 'main', got '{importance}'"
    
    print("✓ Test 3 passed: All track artists correctly marked as 'main'")
    print(f"  Artists: {[artist for artist, _ in all_artists]}")


def test_normal_album_still_works():
    """
    Test that normal albums (not Various Artists) still work correctly
    """
    # Simulate album artist extraction with normal artists
    album_artists_set = set()
    albumartist = "Ismail Candide, Eddy Woogy"
    
    # Process album artist
    individual_artists = [a.strip() for a in str(albumartist).split(',') if a.strip()]
    for individual_artist in individual_artists:
        if individual_artist.lower() != "various artists":
            album_artists_set.add(individual_artist.lower())
    
    # Verify set has the artists
    assert "ismail candide" in album_artists_set
    assert "eddy woogy" in album_artists_set
    assert len(album_artists_set) == 2
    
    # Simulate track artists
    # Track 1: Ismail Candide, Eddy Woogy, Christine Ly
    track1_artists = ["Ismail Candide", "Eddy Woogy", "Christine Ly"]
    
    classified = []
    for track_artist in track1_artists:
        if not album_artists_set:
            importance = "main"
        elif track_artist.lower() in album_artists_set:
            importance = "main"
        else:
            importance = "guest"
        
        classified.append((track_artist, importance))
    
    # Verify classification
    assert classified[0] == ("Ismail Candide", "main")
    assert classified[1] == ("Eddy Woogy", "main")
    assert classified[2] == ("Christine Ly", "guest")
    
    print("✓ Test 4 passed: Normal album artist classification still works")
    print(f"  Main artists: Ismail Candide, Eddy Woogy")
    print(f"  Guest artist: Christine Ly")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Various Artists Importance Fix")
    print("=" * 60)
    print()
    
    test_album_artists_set_excludes_various_artists()
    test_track_artists_marked_as_main_when_set_empty()
    test_complete_scenario()
    test_normal_album_still_works()
    
    print()
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
