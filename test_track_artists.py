#!/usr/bin/env python3
"""
Test script for the track artist formatting in torrent group description.
"""

def format_track_artists(track_metadata):
    """
    Format track artists by separating main artists from guest/featured artists.
    Returns tuple: (main_artists_str, guest_artists_str)
    
    Example:
        If track has Jon Hansen (main) and Mary Doufle (guest):
        Returns: ("[artist]Jon Hansen[/artist]", "[artist]Mary Doufle[/artist]")
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


def test_format_track_artists():
    """Test the format_track_artists function."""
    
    print("Testing format_track_artists...")
    
    # Test 1: Track with main and guest artists
    track_meta = {
        "artists": [
            ("Jon Hansen", "main"),
            ("Mary Doufle", "guest")
        ]
    }
    main, guest = format_track_artists(track_meta)
    print(f"Test 1 - Main and guest:")
    print(f"  Main: {main}")
    print(f"  Guest: {guest}")
    assert main == "[artist]Jon Hansen[/artist]", f"Expected '[artist]Jon Hansen[/artist]', got '{main}'"
    assert guest == "[artist]Mary Doufle[/artist]", f"Expected '[artist]Mary Doufle[/artist]', got '{guest}'"
    print("  ✓ PASS\n")
    
    # Test 2: Track with multiple main artists
    track_meta = {
        "artists": [
            ("Artist A", "main"),
            ("Artist B", "main")
        ]
    }
    main, guest = format_track_artists(track_meta)
    print(f"Test 2 - Multiple main artists:")
    print(f"  Main: {main}")
    print(f"  Guest: {guest}")
    assert main == "[artist]Artist A[/artist], [artist]Artist B[/artist]", f"Unexpected main: {main}"
    assert guest == "", f"Expected empty guest, got '{guest}'"
    print("  ✓ PASS\n")
    
    # Test 3: Track with multiple guest artists
    track_meta = {
        "artists": [
            ("Main Artist", "main"),
            ("Guest 1", "guest"),
            ("Guest 2", "guest")
        ]
    }
    main, guest = format_track_artists(track_meta)
    print(f"Test 3 - Multiple guest artists:")
    print(f"  Main: {main}")
    print(f"  Guest: {guest}")
    assert main == "[artist]Main Artist[/artist]", f"Unexpected main: {main}"
    assert guest == "[artist]Guest 1[/artist], [artist]Guest 2[/artist]", f"Unexpected guest: {guest}"
    print("  ✓ PASS\n")
    
    # Test 4: Track with only main artist (no guests)
    track_meta = {
        "artists": [
            ("Solo Artist", "main")
        ]
    }
    main, guest = format_track_artists(track_meta)
    print(f"Test 4 - Main artist only:")
    print(f"  Main: {main}")
    print(f"  Guest: {guest}")
    assert main == "[artist]Solo Artist[/artist]", f"Unexpected main: {main}"
    assert guest == "", f"Expected empty guest, got '{guest}'"
    print("  ✓ PASS\n")
    
    # Test 5: No artists
    track_meta = {"artists": []}
    main, guest = format_track_artists(track_meta)
    print(f"Test 5 - No artists:")
    print(f"  Main: {main}")
    print(f"  Guest: {guest}")
    assert main == "", f"Expected empty main, got '{main}'"
    assert guest == "", f"Expected empty guest, got '{guest}'"
    print("  ✓ PASS\n")
    
    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print()
    print("Expected output format:")
    print("[b]01.[/b] [artist]Jon Hansen[/artist] - My love is forever (feat. [artist]Mary Doufle[/artist]) [i](03:45)[/i]")
    print()

if __name__ == "__main__":
    test_format_track_artists()
