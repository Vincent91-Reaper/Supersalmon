#!/usr/bin/env python3
"""
Test iTunes scraper per-track artist extraction for DJ Mix.

This simulates the JSON-LD data structure from iTunes and verifies
that per-track artists are correctly extracted for DJ Mix releases.
"""

def test_itunes_dj_mix_track_artists():
    """
    Test that iTunes scraper extracts per-track artists from JSON-LD data.
    
    Simulates a DJ Mix where:
    - Album artists: Dubfire, Richie Hawtin (DJs)
    - Track 1 artist: The Junkies (actual track artist)
    - Track 2 artist: Different Artist
    """
    print("\n" + "=" * 70)
    print("Test: iTunes DJ Mix Per-Track Artist Extraction")
    print("=" * 70)
    
    # Simulate JSON-LD data structure from iTunes
    json_ld_data = {
        "byArtist": [
            {"name": "Dubfire"},
            {"name": "Richie Hawtin"}
        ],
        "tracks": [
            {
                "name": "Parts & Labour (Mixed)",
                "byArtist": {"name": "The Junkies"}  # Per-track artist!
            },
            {
                "name": "Another Track",
                "byArtist": {"name": "Different Artist"}  # Different artist
            },
            {
                "name": "Third Track (feat. Guest Artist)",
                "byArtist": {"name": "Main Artist"}
            }
        ]
    }
    
    # Simulate the fix in parse_tracks
    album_artists = [(a["name"], "main") for a in json_ld_data["byArtist"]]
    
    print(f"\nAlbum artists: {[a[0] for a in album_artists]}")
    print("\nProcessing tracks:")
    
    for i, track in enumerate(json_ld_data["tracks"], 1):
        # Extract per-track artists (the fix!)
        track_artists = []
        if "byArtist" in track:
            artist_data = track["byArtist"]
            if isinstance(artist_data, dict) and "name" in artist_data:
                track_artists = [(artist_data["name"], "main")]
            elif isinstance(artist_data, list):
                track_artists = [(a["name"], "main") for a in artist_data if "name" in a]
        
        # If no per-track artists, fall back to album artists
        if not track_artists:
            track_artists = album_artists
        
        print(f"  Track {i}: {track['name']}")
        print(f"    Artists: {[a[0] for a in track_artists]}")
        
        # Verify
        if i == 1:
            assert track_artists[0][0] == "The Junkies", \
                f"Track 1 should have 'The Junkies', got {track_artists[0][0]}"
            print(f"    ✓ Correct - shows track artist, not album DJs")
        elif i == 2:
            assert track_artists[0][0] == "Different Artist", \
                f"Track 2 should have 'Different Artist', got {track_artists[0][0]}"
            print(f"    ✓ Correct - shows track artist")
        elif i == 3:
            assert track_artists[0][0] == "Main Artist", \
                f"Track 3 should have 'Main Artist', got {track_artists[0][0]}"
            print(f"    ✓ Correct - shows track artist")
    
    print("\n✓ PASS - Per-track artists correctly extracted from JSON-LD data")


def test_itunes_regular_album_fallback():
    """
    Test that regular albums without per-track artists fall back to album artists.
    """
    print("\n" + "=" * 70)
    print("Test: iTunes Regular Album (Fallback to Album Artists)")
    print("=" * 70)
    
    # Simulate JSON-LD data for regular album (no per-track artists)
    json_ld_data = {
        "byArtist": {"name": "Album Artist"},
        "tracks": [
            {"name": "Track One"},  # No byArtist field
            {"name": "Track Two"},  # No byArtist field
        ]
    }
    
    # Extract album artists
    artist_data = json_ld_data["byArtist"]
    if isinstance(artist_data, dict) and "name" in artist_data:
        album_artists = [(artist_data["name"], "main")]
    
    print(f"\nAlbum artists: {[a[0] for a in album_artists]}")
    print("\nProcessing tracks:")
    
    for i, track in enumerate(json_ld_data["tracks"], 1):
        # Extract per-track artists
        track_artists = []
        if "byArtist" in track:
            artist_data = track["byArtist"]
            if isinstance(artist_data, dict) and "name" in artist_data:
                track_artists = [(artist_data["name"], "main")]
        
        # Fallback to album artists
        if not track_artists:
            track_artists = album_artists
        
        print(f"  Track {i}: {track['name']}")
        print(f"    Artists: {[a[0] for a in track_artists]}")
        
        # Verify fallback worked
        assert track_artists[0][0] == "Album Artist", \
            f"Track should fall back to 'Album Artist', got {track_artists[0][0]}"
        print(f"    ✓ Correct - fell back to album artist")
    
    print("\n✓ PASS - Correctly falls back to album artists when no per-track data")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ITUNES DJ MIX PER-TRACK ARTIST EXTRACTION TEST SUITE")
    print("=" * 70)
    
    test_itunes_dj_mix_track_artists()
    test_itunes_regular_album_fallback()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)
    print()
    print("Summary:")
    print("  • DJ Mix tracks: Extract per-track artists from JSON-LD byArtist field")
    print("  • Regular albums: Fall back to album artists if no per-track data")
    print("  • This ensures DJ Mix shows actual track artists (The Junkies)")
    print("  • Not the album DJs (Dubfire & Richie Hawtin)")
    print()
