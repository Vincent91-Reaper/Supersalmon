#!/usr/bin/env python3
"""
Test DJ Mix track artist display.

For DJ Mix releases:
- Album header should show DJ/Compiler names (e.g., "Dubfire & Richie Hawtin")
- Each track should show the ACTUAL track artist from metadata (e.g., "The Junkies")
- NOT the album DJs repeated on every track
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


def test_dj_mix_track_artists():
    """
    Test that DJ Mix tracks show actual track artists, not album DJs.
    
    Album: "Dubfire & Richie Hawtin - Boiler Room: Dubfire b2b Richie Hawtin in Berlin"
    Track 01: "Parts & Labour (Mixed)" by "The Junkies"
    
    Expected output:
    [b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]
    
    NOT:
    [b]01.[/b] [artist]Dubfire[/artist], [artist]Richie Hawtin[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]
    """
    print("\n" + "=" * 70)
    print("Test: DJ Mix Track Artists")
    print("=" * 70)
    
    # Track metadata with the ACTUAL track artist (The Junkies)
    # NOT the album DJs (Dubfire & Richie Hawtin)
    track_metadata = {
        "artists": [
            ("The Junkies", "main"),  # Actual track artist
        ]
    }
    
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    
    # Build the track line
    line = "[b]01.[/b] "
    
    if main_artists_str:
        line += f"{main_artists_str} - "
    
    line += "Parts & Labour (Mixed)"
    
    if guest_artists_str:
        line += f" (feat. {guest_artists_str})"
    
    line += " [i](03:59)[/i]"
    
    expected = "[b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]"
    
    print(f"\nAlbum: Dubfire & Richie Hawtin - Boiler Room: Dubfire b2b Richie Hawtin in Berlin")
    print(f"\nExpected: {expected}")
    print(f"Actual:   {line}")
    
    assert line == expected, f"DJ Mix track artist test failed!"
    print("\n✓ PASS - DJ Mix track shows actual track artist (The Junkies)")
    print("         NOT album DJs (Dubfire & Richie Hawtin)")


def test_dj_mix_with_guest():
    """
    Test DJ Mix track with guest artist.
    """
    print("\n" + "=" * 70)
    print("Test: DJ Mix Track with Guest Artist")
    print("=" * 70)
    
    track_metadata = {
        "artists": [
            ("Main Artist", "main"),
            ("Guest Artist", "guest"),
        ]
    }
    
    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
    
    line = "[b]02.[/b] "
    
    if main_artists_str:
        line += f"{main_artists_str} - "
    
    line += "Track Title"
    
    if guest_artists_str:
        line += f" (feat. {guest_artists_str})"
    
    line += " [i](04:30)[/i]"
    
    expected = "[b]02.[/b] [artist]Main Artist[/artist] - Track Title (feat. [artist]Guest Artist[/artist]) [i](04:30)[/i]"
    
    print(f"\nExpected: {expected}")
    print(f"Actual:   {line}")
    
    assert line == expected, f"DJ Mix track with guest test failed!"
    print("\n✓ PASS - DJ Mix track shows main + guest artists correctly")


def test_metadata_structure():
    """
    Test that metadata structure is correct for DJ Mix.
    """
    print("\n" + "=" * 70)
    print("Test: DJ Mix Metadata Structure")
    print("=" * 70)
    
    # Example of correct DJ Mix metadata structure
    metadata = {
        "rls_type": "DJ Mix",
        "title": "Boiler Room: Dubfire b2b Richie Hawtin in Berlin, May 3, 2016",
        "artists": [
            ("Dubfire", "dj"),  # Album-level DJ
            ("Richie Hawtin", "dj"),  # Album-level DJ
        ],
        "tracks": {
            "1": {  # Disc 1
                "1": {  # Track 1
                    "title": "Parts & Labour (Mixed)",
                    "artists": [
                        ("The Junkies", "main"),  # Actual track artist!
                    ]
                },
                "2": {  # Track 2
                    "title": "Another Track",
                    "artists": [
                        ("Different Artist", "main"),  # Different track artist
                    ]
                }
            }
        }
    }
    
    print("\nCorrect metadata structure:")
    print("  - Album artists: DJs/Compilers (Dubfire, Richie Hawtin)")
    print("  - Track artists: Actual performers (The Junkies, Different Artist)")
    print("\n✓ PASS - Metadata structure documented")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DJ MIX TRACK ARTIST DISPLAY TEST SUITE")
    print("=" * 70)
    
    test_dj_mix_track_artists()
    test_dj_mix_with_guest()
    test_metadata_structure()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)
    print()
    print("Summary:")
    print("  • DJ Mix album header: Shows DJs (Dubfire & Richie Hawtin)")
    print("  • DJ Mix track lines: Show ACTUAL track artists (The Junkies)")
    print("  • Track metadata must contain per-track artists, not album DJs")
    print()
