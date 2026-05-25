#!/usr/bin/env python3
"""
Test for Beatport upload fix - handle artist as list or string.

Tests the all_tracks_have_same_artists function with both formats.
"""

# Mock track object
class MockTrack:
    def __init__(self, artist):
        self.artist = artist

class MockTrackData:
    def __init__(self, artist):
        self.t = MockTrack(artist)

def all_tracks_have_same_artists(tracks, main_artists):
    """
    Check if all tracks have the same artist set as the album's main artists.
    Returns True only if every track has exactly the same artists.
    """
    if not tracks or not main_artists:
        return True
    
    # Normalize main artists for comparison (lowercase, strip whitespace)
    main_artists_normalized = {artist.lower().strip() for artist in main_artists}
    
    for track in tracks:
        # Get track artists from file tags
        track_artist = track['t'].artist if hasattr(track['t'], 'artist') else None
        if not track_artist:
            continue
            
        # Split and normalize track artists
        track_artists = set()
        
        # Handle both list and string formats
        if isinstance(track_artist, list):
            # Artist is already a list (e.g., from Beatport)
            for artist in track_artist:
                if artist and artist.strip():
                    track_artists.add(artist.strip().lower())
        else:
            # Artist is a string, needs splitting (e.g., from iTunes)
            for part in track_artist.split(', '):
                for artist in part.split(' & '):
                    if artist.strip():
                        track_artists.add(artist.strip().lower())
        
        # If this track's artists differ from main artists, tracks vary
        if track_artists != main_artists_normalized:
            return False
    
    return True


def test_beatport_list_format():
    """Test with artist as list (Beatport format)"""
    print("Test 1: Artist as list (Beatport format)")
    
    # All tracks have same artists
    main_artists = ["Artist A", "Artist B"]
    tracks = [
        {'t': MockTrack(["Artist A", "Artist B"])},
        {'t': MockTrack(["Artist A", "Artist B"])},
    ]
    result = all_tracks_have_same_artists(tracks, main_artists)
    print(f"  Same artists test: {result} (expected: True)")
    assert result == True, "Should return True when all tracks have same artists"
    
    # Tracks have different artists
    tracks_different = [
        {'t': MockTrack(["Artist A"])},
        {'t': MockTrack(["Artist B"])},
    ]
    result = all_tracks_have_same_artists(tracks_different, main_artists)
    print(f"  Different artists test: {result} (expected: False)")
    assert result == False, "Should return False when tracks have different artists"
    
    print("  ✓ List format tests passed")


def test_itunes_string_format():
    """Test with artist as string (iTunes format)"""
    print("\nTest 2: Artist as string (iTunes format)")
    
    # All tracks have same artists (string with &)
    main_artists = ["Artist A", "Artist B"]
    tracks = [
        {'t': MockTrack("Artist A & Artist B")},
        {'t': MockTrack("Artist A & Artist B")},
    ]
    result = all_tracks_have_same_artists(tracks, main_artists)
    print(f"  Same artists test: {result} (expected: True)")
    assert result == True, "Should return True when all tracks have same artists"
    
    # Tracks have different artists (string format)
    tracks_different = [
        {'t': MockTrack("Artist A")},
        {'t': MockTrack("Artist B")},
    ]
    result = all_tracks_have_same_artists(tracks_different, main_artists)
    print(f"  Different artists test: {result} (expected: False)")
    assert result == False, "Should return False when tracks have different artists"
    
    print("  ✓ String format tests passed")


def test_mixed_separators():
    """Test with comma and ampersand separators"""
    print("\nTest 3: Mixed separators in string format")
    
    main_artists = ["Artist A", "Artist B", "Artist C"]
    tracks = [
        {'t': MockTrack("Artist A, Artist B & Artist C")},
        {'t': MockTrack("Artist A, Artist B & Artist C")},
    ]
    result = all_tracks_have_same_artists(tracks, main_artists)
    print(f"  Mixed separators test: {result} (expected: True)")
    assert result == True, "Should handle comma and ampersand separators"
    
    print("  ✓ Mixed separator tests passed")


def test_case_insensitive():
    """Test that comparison is case insensitive"""
    print("\nTest 4: Case insensitive comparison")
    
    main_artists = ["Artist A", "Artist B"]
    tracks = [
        {'t': MockTrack(["ARTIST A", "artist b"])},  # Different case
        {'t': MockTrack(["Artist A", "Artist B"])},
    ]
    result = all_tracks_have_same_artists(tracks, main_artists)
    print(f"  Case insensitive test: {result} (expected: True)")
    assert result == True, "Should be case insensitive"
    
    print("  ✓ Case insensitive tests passed")


def test_whitespace_handling():
    """Test that whitespace is properly handled"""
    print("\nTest 5: Whitespace handling")
    
    main_artists = ["Artist A", "Artist B"]
    tracks = [
        {'t': MockTrack(["  Artist A  ", " Artist B "])},  # Extra whitespace
        {'t': MockTrack(["Artist A", "Artist B"])},
    ]
    result = all_tracks_have_same_artists(tracks, main_artists)
    print(f"  Whitespace test: {result} (expected: True)")
    assert result == True, "Should strip whitespace"
    
    print("  ✓ Whitespace handling tests passed")


def test_empty_and_none():
    """Test edge cases with empty and None values"""
    print("\nTest 6: Empty and None handling")
    
    main_artists = ["Artist A"]
    
    # Empty track artist
    tracks_empty = [
        {'t': MockTrack([])},  # Empty list
    ]
    result = all_tracks_have_same_artists(tracks_empty, main_artists)
    print(f"  Empty list test: {result} (expected: True)")
    assert result == True, "Should handle empty artist list"
    
    # None track artist
    tracks_none = [
        {'t': MockTrack(None)},
    ]
    result = all_tracks_have_same_artists(tracks_none, main_artists)
    print(f"  None test: {result} (expected: True)")
    assert result == True, "Should handle None artist"
    
    print("  ✓ Edge case tests passed")


if __name__ == "__main__":
    print("Testing all_tracks_have_same_artists function fix...\n")
    
    test_beatport_list_format()
    test_itunes_string_format()
    test_mixed_separators()
    test_case_insensitive()
    test_whitespace_handling()
    test_empty_and_none()
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50)
    print("\nThe fix handles both list and string formats correctly.")
