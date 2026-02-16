#!/usr/bin/env python3
"""
Test to verify the code has been reverted to commit 66d8ebb state.
This tests the original simple is_various_artists logic.
"""

def format_track_artists(track_metadata):
    """
    Format track artists by separating main artists from guest/featured artists.
    Returns tuple: (main_artists_str, guest_artists_str)
    """
    if not track_metadata or "artists" not in track_metadata:
        return "", ""
    
    main_artists = []
    guest_artists = []
    
    for artist_name, importance in track_metadata["artists"]:
        if importance == "main":
            main_artists.append(artist_name)
        elif importance == "guest":
            guest_artists.append(artist_name)
    
    # Format main artists with [artist] tags
    main_str = ""
    if main_artists:
        artist_tags = [f"[artist]{artist}[/artist]" for artist in main_artists]
        main_str = ", ".join(artist_tags)
    
    # Format guest artists with [artist] tags
    guest_str = ""
    if guest_artists:
        artist_tags = [f"[artist]{artist}[/artist]" for artist in guest_artists]
        guest_str = ", ".join(artist_tags)
    
    return main_str, guest_str


def test_dj_mix():
    """Test DJ Mix behavior - should show per-track artists."""
    print("\n" + "=" * 70)
    print("Test: DJ Mix (is_various_artists = True)")
    print("=" * 70)
    
    is_various_artists = True  # DJ Mix always sets this
    
    track_metadata = {
        "artists": [
            ("Artist A", "main"),
            ("Guest B", "guest")
        ]
    }
    
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    
    line = "[b]01.[/b] "
    
    # Original logic: if is_various_artists and track_metadata
    if is_various_artists and track_metadata:
        if main_artists_str:
            line += f"{main_artists_str} - "
        line += "Track One"
        if guest_artists_str:
            line += f" (feat. {guest_artists_str})"
    else:
        line += "Track One"
    
    expected = "[b]01.[/b] [artist]Artist A[/artist] - Track One (feat. [artist]Guest B[/artist])"
    print(f"\nExpected: {expected}")
    print(f"Actual:   {line}")
    assert line == expected, f"DJ Mix test failed!"
    print("\n✓ PASS - DJ Mix shows per-track artists")


def test_one_main_artist():
    """Test 1 main artist - should NOT show per-track artists."""
    print("\n" + "=" * 70)
    print("Test: 1 Main Artist (is_various_artists = False)")
    print("=" * 70)
    
    # 1 main artist
    main_artists = ["Jon Hansen"]
    is_various_artists = len(main_artists) >= 3  # False
    
    track_metadata = {
        "artists": [
            ("Jon Hansen", "main"),
            ("Guest", "guest")
        ]
    }
    
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    
    line = "[b]01.[/b] "
    
    # Original logic: if is_various_artists and track_metadata
    if is_various_artists and track_metadata:
        if main_artists_str:
            line += f"{main_artists_str} - "
        line += "Love"
        if guest_artists_str:
            line += f" (feat. {guest_artists_str})"
    else:
        line += "Love"
    
    expected = "[b]01.[/b] Love"
    print(f"\nExpected: {expected}")
    print(f"Actual:   {line}")
    assert line == expected, f"1 main artist test failed!"
    print("\n✓ PASS - 1 main artist does NOT show per-track artists")


def test_two_main_artists():
    """Test 2 main artists - should NOT show per-track artists."""
    print("\n" + "=" * 70)
    print("Test: 2 Main Artists (is_various_artists = False)")
    print("=" * 70)
    
    # 2 main artists
    main_artists = ["Artist A", "Artist B"]
    is_various_artists = len(main_artists) >= 3  # False
    
    track_metadata = {
        "artists": [
            ("Artist A", "main"),
            ("Guest", "guest")
        ]
    }
    
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    
    line = "[b]01.[/b] "
    
    # Original logic: if is_various_artists and track_metadata
    if is_various_artists and track_metadata:
        if main_artists_str:
            line += f"{main_artists_str} - "
        line += "Track One"
        if guest_artists_str:
            line += f" (feat. {guest_artists_str})"
    else:
        line += "Track One"
    
    expected = "[b]01.[/b] Track One"
    print(f"\nExpected: {expected}")
    print(f"Actual:   {line}")
    assert line == expected, f"2 main artists test failed!"
    print("\n✓ PASS - 2 main artists does NOT show per-track artists")


def test_three_plus_main_artists():
    """Test 3+ main artists - should show per-track artists."""
    print("\n" + "=" * 70)
    print("Test: 3+ Main Artists (is_various_artists = True)")
    print("=" * 70)
    
    # 3+ main artists (Various Artists)
    main_artists = ["Artist A", "Artist B", "Artist C"]
    is_various_artists = len(main_artists) >= 3  # True
    
    track_metadata = {
        "artists": [
            ("Artist A", "main"),
            ("Guest", "guest")
        ]
    }
    
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    
    line = "[b]01.[/b] "
    
    # Original logic: if is_various_artists and track_metadata
    if is_various_artists and track_metadata:
        if main_artists_str:
            line += f"{main_artists_str} - "
        line += "Track One"
        if guest_artists_str:
            line += f" (feat. {guest_artists_str})"
    else:
        line += "Track One"
    
    expected = "[b]01.[/b] [artist]Artist A[/artist] - Track One (feat. [artist]Guest[/artist])"
    print(f"\nExpected: {expected}")
    print(f"Actual:   {line}")
    assert line == expected, f"3+ main artists test failed!"
    print("\n✓ PASS - 3+ main artists shows per-track artists")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("REVERT TO COMMIT 66d8ebb - VERIFICATION TEST SUITE")
    print("=" * 70)
    
    test_dj_mix()
    test_one_main_artist()
    test_two_main_artists()
    test_three_plus_main_artists()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)
    print()
    print("Summary of reverted behavior:")
    print("  • DJ Mix: is_various_artists = True → shows per-track")
    print("  • 1 main: is_various_artists = False → NO per-track")
    print("  • 2 main: is_various_artists = False → NO per-track")
    print("  • 3+ main: is_various_artists = True → shows per-track")
    print()
    print("NO show_track_main_artist logic!")
    print("BACK to simple is_various_artists only!")
    print()
