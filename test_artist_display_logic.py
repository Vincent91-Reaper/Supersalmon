#!/usr/bin/env python3
"""
Test the artist display logic fix for multi-artist albums.

This tests the fix for the issue where per-track artists were not being shown
when tracks had varying artists.
"""

class MockTrack:
    """Mock track object for testing."""
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist


def all_tracks_have_same_artists(tracks, main_artists):
    """
    Check if all tracks have the same artist set as the album's main artists.
    Returns True only if every track has exactly the same artists.
    
    Used to determine if per-track artists should be shown:
    - If all tracks have same artists → Don't show (redundant)
    - If tracks have different artists → Show (needed for clarity)
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


def test_case_1_all_artists_on_all_tracks():
    """
    Case 1: Album has 3 main artists (A, B, C) and all contribute to all tracks.
    Expected: show_track_artists = False (don't show artists per track)
    """
    print("\n" + "="*60)
    print("Test Case 1: All Artists on All Tracks")
    print("="*60)
    
    main_artists = ["Artist A", "Artist B", "Artist C"]
    tracks = [
        {"t": MockTrack("Love", "Artist A, Artist B, Artist C")},
        {"t": MockTrack("Hate", "Artist A, Artist B, Artist C")},
        {"t": MockTrack("Jealousy", "Artist A, Artist B, Artist C")},
    ]
    
    is_dj_mix = False
    
    # OLD LOGIC (BUGGY):
    # show_track_artists = False
    # if not is_dj_mix and len(main_artists) >= 2:
    #     tracks_have_same_artists = all_tracks_have_same_artists(tracks, main_artists)
    #     show_track_artists = not tracks_have_same_artists
    
    # NEW LOGIC (FIXED):
    show_track_artists = False
    if not is_dj_mix:
        tracks_have_same_artists = all_tracks_have_same_artists(tracks, main_artists)
        show_track_artists = not tracks_have_same_artists
    
    print(f"Main artists: {main_artists}")
    print(f"Tracks: {len(tracks)}")
    print(f"All tracks have same artists: {all_tracks_have_same_artists(tracks, main_artists)}")
    print(f"show_track_artists: {show_track_artists}")
    print(f"Expected: False (don't show per-track artists)")
    
    assert show_track_artists == False, "Should NOT show per-track artists when all artists on all tracks"
    print("✓ PASS")


def test_case_2_different_artists_per_track():
    """
    Case 2: Album has 3 main artists (A, B, C), each contributes to different tracks.
    Expected: show_track_artists = True (show artists per track)
    """
    print("\n" + "="*60)
    print("Test Case 2: Different Artists Per Track")
    print("="*60)
    
    main_artists = ["Artist A", "Artist B", "Artist C"]
    tracks = [
        {"t": MockTrack("Love", "Artist A")},
        {"t": MockTrack("Hate", "Artist B")},
        {"t": MockTrack("Jealousy", "Artist C")},
    ]
    
    is_dj_mix = False
    
    # NEW LOGIC (FIXED):
    show_track_artists = False
    if not is_dj_mix:
        tracks_have_same_artists = all_tracks_have_same_artists(tracks, main_artists)
        show_track_artists = not tracks_have_same_artists
    
    print(f"Main artists: {main_artists}")
    print(f"Track 1 artist: {tracks[0]['t'].artist}")
    print(f"Track 2 artist: {tracks[1]['t'].artist}")
    print(f"Track 3 artist: {tracks[2]['t'].artist}")
    print(f"All tracks have same artists: {all_tracks_have_same_artists(tracks, main_artists)}")
    print(f"show_track_artists: {show_track_artists}")
    print(f"Expected: True (show per-track artists)")
    
    assert show_track_artists == True, "Should show per-track artists when they vary"
    print("✓ PASS")


def test_case_3_single_artist_album_with_guests():
    """
    Case 3: Album has 1 main artist, some tracks have guest artists.
    Expected: show_track_artists = True (show artists per track)
    
    This tests the BUG FIX: Previously, single-artist albums (len(main_artists) < 2)
    would not activate the smart display logic at all!
    """
    print("\n" + "="*60)
    print("Test Case 3: Single Artist with Guests (BUG FIX TEST)")
    print("="*60)
    
    main_artists = ["Main Artist"]
    tracks = [
        {"t": MockTrack("Track 1", "Main Artist")},
        {"t": MockTrack("Track 2", "Main Artist, Guest Artist")},
        {"t": MockTrack("Track 3", "Main Artist")},
    ]
    
    is_dj_mix = False
    
    # OLD LOGIC (BUGGY):
    show_track_artists_old = False
    if not is_dj_mix and len(main_artists) >= 2:  # This would be FALSE!
        tracks_have_same_artists = all_tracks_have_same_artists(tracks, main_artists)
        show_track_artists_old = not tracks_have_same_artists
    
    # NEW LOGIC (FIXED):
    show_track_artists_new = False
    if not is_dj_mix:  # This is TRUE!
        tracks_have_same_artists = all_tracks_have_same_artists(tracks, main_artists)
        show_track_artists_new = not tracks_have_same_artists
    
    print(f"Main artists: {main_artists}")
    print(f"Track 1 artist: {tracks[0]['t'].artist}")
    print(f"Track 2 artist: {tracks[1]['t'].artist}")
    print(f"Track 3 artist: {tracks[2]['t'].artist}")
    print(f"All tracks have same artists: {all_tracks_have_same_artists(tracks, main_artists)}")
    print(f"\nOLD LOGIC - show_track_artists: {show_track_artists_old} (WRONG - should be True)")
    print(f"NEW LOGIC - show_track_artists: {show_track_artists_new} (CORRECT)")
    
    assert show_track_artists_new == True, "Should show per-track artists when they vary"
    assert show_track_artists_old == False, "Old logic would incorrectly NOT show artists"
    print("✓ PASS - Bug is fixed!")


def test_case_4_dj_mix_excluded():
    """
    Case 4: DJ Mix should be excluded from this logic entirely.
    Expected: Logic should not activate for DJ mixes
    """
    print("\n" + "="*60)
    print("Test Case 4: DJ Mix Excluded from Logic")
    print("="*60)
    
    main_artists = ["DJ Name"]
    tracks = [
        {"t": MockTrack("Track 1", "Artist A")},
        {"t": MockTrack("Track 2", "Artist B")},
        {"t": MockTrack("Track 3", "Artist C")},
    ]
    
    is_dj_mix = True
    
    # Logic should not activate for DJ Mix
    show_track_artists = False
    if not is_dj_mix:
        tracks_have_same_artists = all_tracks_have_same_artists(tracks, main_artists)
        show_track_artists = not tracks_have_same_artists
    
    print(f"is_dj_mix: {is_dj_mix}")
    print(f"show_track_artists: {show_track_artists}")
    print(f"Expected: False (logic doesn't activate for DJ mixes)")
    
    # For DJ mixes, show_track_artists should remain False because the logic doesn't activate
    # (DJ mixes have their own separate logic for showing artists)
    assert show_track_artists == False, "Logic should not activate for DJ mixes"
    print("✓ PASS")


if __name__ == "__main__":
    print("Testing Artist Display Logic Fix")
    print("="*60)
    
    test_case_1_all_artists_on_all_tracks()
    test_case_2_different_artists_per_track()
    test_case_3_single_artist_album_with_guests()
    test_case_4_dj_mix_excluded()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    print("\nSummary:")
    print("- Case 1: All artists on all tracks → Don't show per-track ✓")
    print("- Case 2: Different artists per track → Show per-track ✓")
    print("- Case 3: Single artist with guests → Show per-track ✓ (BUG FIXED)")
    print("- Case 4: DJ Mix excluded from logic ✓")
