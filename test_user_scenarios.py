#!/usr/bin/env python3
"""
Test to verify the artist display logic for the user's specific scenarios.

Scenario 1: Album with 2 tracks, 2 artists (A & B) on BOTH tracks
Expected: Don't show artist names next to each track (redundant)

Scenario 2: Album with 2 tracks, 2 artists (A on track 1, B on track 2)
Expected: Show artist names next to each track (needed for clarity)
"""

class MockTrack:
    """Mock track object for testing"""
    def __init__(self, artist):
        self.artist = artist

# Simulate the all_tracks_have_same_artists function logic
def all_tracks_have_same_artists(tracks, main_artists):
    """
    Check if all tracks have the same artist set as the album's main artists.
    """
    if not tracks or not main_artists:
        return True
    
    # Normalize main artists for comparison
    main_artists_normalized = {artist.lower().strip() for artist in main_artists}
    
    for track in tracks:
        # Get track artists
        track_artist = track['t'].artist if hasattr(track['t'], 'artist') else None
        if not track_artist:
            continue
            
        # Split and normalize track artists
        track_artists = set()
        
        # Handle both list and string formats
        if isinstance(track_artist, list):
            for artist in track_artist:
                if artist and artist.strip():
                    track_artists.add(artist.strip().lower())
        else:
            # Artist is a string, needs splitting
            for part in track_artist.split(', '):
                for artist in part.split(' & '):
                    if artist.strip():
                        track_artists.add(artist.strip().lower())
        
        # If this track's artists differ from main artists, tracks vary
        if track_artists != main_artists_normalized:
            return False
    
    return True


def test_scenario_1():
    """
    Scenario 1: Album with 2 tracks, 2 artists (A & B) on BOTH tracks
    Expected: Don't show artist names next to each track (redundant)
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 1: Same artists on all tracks")
    print("="*70)
    
    # Album has 2 main artists: A and B
    main_artists = ['Artist A', 'Artist B']
    
    # Both tracks have both artists A and B
    track_data = [
        {'t': MockTrack('Artist A & Artist B')},  # Track 1
        {'t': MockTrack('Artist A & Artist B')},  # Track 2
    ]
    
    # Check if all tracks have same artists
    tracks_have_same_artists = all_tracks_have_same_artists(track_data, main_artists)
    
    # Determine if we should show per-track artists
    is_dj_mix = False
    show_track_artists = False
    
    if not is_dj_mix:
        if len(main_artists) == 1:
            show_track_artists = False
        else:
            show_track_artists = not tracks_have_same_artists
    
    print(f"Album main artists: {main_artists}")
    print(f"Track 1 artists: Artist A & Artist B")
    print(f"Track 2 artists: Artist A & Artist B")
    print(f"\nAll tracks have same artists? {tracks_have_same_artists}")
    print(f"Show per-track artists? {show_track_artists}")
    
    expected = False  # Should NOT show per-track artists
    if show_track_artists == expected:
        print(f"\n✅ PASS: Correctly set to NOT show per-track artists (redundant)")
        return True
    else:
        print(f"\n❌ FAIL: Expected {expected}, got {show_track_artists}")
        return False


def test_scenario_2():
    """
    Scenario 2: Album with 2 tracks, 2 artists (A on track 1, B on track 2)
    Expected: Show artist names next to each track (needed for clarity)
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 2: Different artists per track")
    print("="*70)
    
    # Album has 2 main artists: A and B
    main_artists = ['Artist A', 'Artist B']
    
    # Track 1 has only Artist A, Track 2 has only Artist B
    track_data = [
        {'t': MockTrack('Artist A')},  # Track 1
        {'t': MockTrack('Artist B')},  # Track 2
    ]
    
    # Check if all tracks have same artists
    tracks_have_same_artists = all_tracks_have_same_artists(track_data, main_artists)
    
    # Determine if we should show per-track artists
    is_dj_mix = False
    show_track_artists = False
    
    if not is_dj_mix:
        if len(main_artists) == 1:
            show_track_artists = False
        else:
            show_track_artists = not tracks_have_same_artists
    
    print(f"Album main artists: {main_artists}")
    print(f"Track 1 artists: Artist A")
    print(f"Track 2 artists: Artist B")
    print(f"\nAll tracks have same artists? {tracks_have_same_artists}")
    print(f"Show per-track artists? {show_track_artists}")
    
    expected = True  # SHOULD show per-track artists
    if show_track_artists == expected:
        print(f"\n✅ PASS: Correctly set to SHOW per-track artists (needed)")
        return True
    else:
        print(f"\n❌ FAIL: Expected {expected}, got {show_track_artists}")
        return False


def test_scenario_3_bonus():
    """
    Bonus: Album with 2 artists, both on track 1, only one on track 2
    Expected: Show artist names (tracks have different artists)
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 3 (BONUS): Partial artist overlap")
    print("="*70)
    
    # Album has 2 main artists: A and B
    main_artists = ['Artist A', 'Artist B']
    
    # Track 1 has both A and B, Track 2 has only A
    track_data = [
        {'t': MockTrack('Artist A & Artist B')},  # Track 1
        {'t': MockTrack('Artist A')},              # Track 2
    ]
    
    # Check if all tracks have same artists
    tracks_have_same_artists = all_tracks_have_same_artists(track_data, main_artists)
    
    # Determine if we should show per-track artists
    is_dj_mix = False
    show_track_artists = False
    
    if not is_dj_mix:
        if len(main_artists) == 1:
            show_track_artists = False
        else:
            show_track_artists = not tracks_have_same_artists
    
    print(f"Album main artists: {main_artists}")
    print(f"Track 1 artists: Artist A & Artist B")
    print(f"Track 2 artists: Artist A")
    print(f"\nAll tracks have same artists? {tracks_have_same_artists}")
    print(f"Show per-track artists? {show_track_artists}")
    
    expected = True  # SHOULD show per-track artists (tracks differ)
    if show_track_artists == expected:
        print(f"\n✅ PASS: Correctly set to SHOW per-track artists (tracks differ)")
        return True
    else:
        print(f"\n❌ FAIL: Expected {expected}, got {show_track_artists}")
        return False


if __name__ == '__main__':
    print("\n" + "="*70)
    print("TESTING ARTIST DISPLAY LOGIC FOR USER'S SCENARIOS")
    print("="*70)
    
    results = []
    
    # Test both user scenarios
    results.append(("Scenario 1: Same artists on all tracks", test_scenario_1()))
    results.append(("Scenario 2: Different artists per track", test_scenario_2()))
    results.append(("Scenario 3: Partial artist overlap", test_scenario_3_bonus()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅✅✅ ALL TESTS PASSED! ✅✅✅")
        print("\nThe logic correctly handles both user scenarios:")
        print("1. Same artists on all tracks → Don't show (redundant)")
        print("2. Different artists per track → Show (needed)")
    else:
        print("❌❌❌ SOME TESTS FAILED ❌❌❌")
    print("="*70 + "\n")
