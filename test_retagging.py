#!/usr/bin/env python3
"""
Test script for the retagging feature improvements.

Tests the new logic:
- If main artist is present in file tags (even with featured artists), don't retag
- Only retag if main artist is missing
"""


def _normalize_artists(artist_str):
    """
    Normalize an artist string to a set of individual artist names.
    Handles various separators and returns lowercase artist names for comparison.
    Also handles 'feat.' and 'featuring' as separators.
    """
    # First, handle feat/featuring patterns - replace with delimiter
    import re
    # Match variations: feat., feat, featuring, ft., ft
    artist_str = re.sub(r'\s+(feat\.?|featuring|ft\.?)\s+', '|', artist_str, flags=re.IGNORECASE)
    
    # Replace common separators with a single delimiter
    normalized = artist_str.replace(" & ", "|").replace(", ", "|").replace(",", "|").replace(";", "|")
    # Split and strip whitespace, convert to lowercase for case-insensitive comparison
    artists = {name.strip().lower() for name in normalized.split("|") if name.strip()}
    return artists


def _main_artists_present(old_artist_str, main_artist_str):
    """
    Check if all main artists are present in the file tags, even if additional artists exist.
    This allows files to keep additional featured/guest artists without retagging.
    
    Example: If main artist is "Artist A" and file has "Artist A, Artist B", 
             main artists are present (returns True), so don't retag.
    """
    old_artists = _normalize_artists(old_artist_str)
    main_artists = _normalize_artists(main_artist_str)
    
    # Main artists are present if they are a subset of the file's artists
    return main_artists.issubset(old_artists)


def test_normalize_artists():
    """Test the artist normalization function."""
    print("Testing _normalize_artists...")
    
    # Test 1: Simple artist
    result = _normalize_artists("Artist A")
    assert result == {"artist a"}, f"Expected {{'artist a'}}, got {result}"
    print("  ✓ Simple artist normalization")
    
    # Test 2: Multiple artists with &
    result = _normalize_artists("Artist A & Artist B")
    assert result == {"artist a", "artist b"}, f"Expected {{'artist a', 'artist b'}}, got {result}"
    print("  ✓ Multiple artists with & separator")
    
    # Test 3: Multiple artists with comma
    result = _normalize_artists("Artist A, Artist B")
    assert result == {"artist a", "artist b"}, f"Expected {{'artist a', 'artist b'}}, got {result}"
    print("  ✓ Multiple artists with comma separator")
    
    # Test 4: Mixed separators
    result = _normalize_artists("Artist A, Artist B & Artist C")
    assert result == {"artist a", "artist b", "artist c"}, f"Expected {{'artist a', 'artist b', 'artist c'}}, got {result}"
    print("  ✓ Multiple artists with mixed separators")
    
    print("All _normalize_artists tests passed!\n")


def test_main_artists_present():
    """Test the main artist presence checking function."""
    print("Testing _main_artists_present...")
    
    # Test 1: Main artist present alone in file
    result = _main_artists_present("Artist A", "Artist A")
    assert result == True, f"Expected True when main artist matches exactly, got {result}"
    print("  ✓ Main artist present alone (exact match)")
    
    # Test 2: Main artist present with additional artists in file
    result = _main_artists_present("Artist A, Artist B", "Artist A")
    assert result == True, f"Expected True when main artist present with others, got {result}"
    print("  ✓ Main artist present with featured artist (should NOT retag)")
    
    # Test 3: Main artist missing from file
    result = _main_artists_present("Artist B", "Artist A")
    assert result == False, f"Expected False when main artist missing, got {result}"
    print("  ✓ Main artist missing (should retag)")
    
    # Test 4: Multiple main artists, all present with additional artists
    result = _main_artists_present("Artist A, Artist B, Artist C", "Artist A & Artist B")
    assert result == True, f"Expected True when all main artists present with others, got {result}"
    print("  ✓ Multiple main artists present with additional artist")
    
    # Test 5: Multiple main artists, one missing
    result = _main_artists_present("Artist A, Artist C", "Artist A & Artist B")
    assert result == False, f"Expected False when one main artist missing, got {result}"
    print("  ✓ Multiple main artists, one missing (should retag)")
    
    # Test 6: Case insensitive matching
    result = _main_artists_present("ARTIST A, artist b", "Artist A")
    assert result == True, f"Expected True with case-insensitive matching, got {result}"
    print("  ✓ Case-insensitive matching works")
    
    # Test 7: Different separators
    result = _main_artists_present("Artist A & Artist B, Artist C", "Artist A, Artist B")
    assert result == True, f"Expected True with different separators, got {result}"
    print("  ✓ Different separators (& vs ,) work correctly")
    
    print("All _main_artists_present tests passed!\n")


def test_retagging_scenarios():
    """Test real-world retagging scenarios."""
    print("Testing real-world retagging scenarios...")
    
    scenarios = [
        {
            "name": "Main artist present with featured artist - NO RETAG",
            "file_artist": "Artist A, Artist B (feat.)",
            "main_artist": "Artist A",
            "should_retag": False
        },
        {
            "name": "Main artist missing - RETAG",
            "file_artist": "Artist B",
            "main_artist": "Artist A",
            "should_retag": True
        },
        {
            "name": "Both main artists present with featured - NO RETAG",
            "file_artist": "Artist A & Artist B feat. Artist C",
            "main_artist": "Artist A & Artist B",
            "should_retag": False
        },
        {
            "name": "Empty file artist - RETAG",
            "file_artist": "",
            "main_artist": "Artist A",
            "should_retag": True
        },
        {
            "name": "Exact match - NO RETAG",
            "file_artist": "Artist A",
            "main_artist": "Artist A",
            "should_retag": False
        }
    ]
    
    for scenario in scenarios:
        file_artist = scenario["file_artist"]
        main_artist = scenario["main_artist"]
        should_retag = scenario["should_retag"]
        
        # Empty string check
        if not file_artist or file_artist == "None":
            needs_retag = True
        else:
            needs_retag = not _main_artists_present(file_artist, main_artist)
        
        expected = "RETAG" if should_retag else "NO RETAG"
        actual = "RETAG" if needs_retag else "NO RETAG"
        
        if needs_retag == should_retag:
            print(f"  ✓ {scenario['name']}")
            print(f"    File: '{file_artist}' | Main: '{main_artist}' → {actual}")
        else:
            print(f"  ✗ {scenario['name']}")
            print(f"    File: '{file_artist}' | Main: '{main_artist}'")
            print(f"    Expected: {expected}, Got: {actual}")
            raise AssertionError(f"Scenario failed: {scenario['name']}")
    
    print("All retagging scenarios passed!\n")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("RETAGGING FEATURE TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_normalize_artists()
        test_main_artists_present()
        test_retagging_scenarios()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print()
        print("Summary of new behavior:")
        print("- Main artist present + featured artists → NO RETAG (preserves file tags)")
        print("- Main artist missing → RETAG (updates to correct main artist)")
        print("- This prevents overwriting files that have correct main artist + features")
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"TEST FAILED: {e}")
        print("=" * 60)
        sys.exit(1)
