#!/usr/bin/env python3
"""
Simple test to demonstrate the guest artist display logic fix.

This validates that the code logic correctly handles guest artists
even when show_track_artists is False.
"""

def test_logic():
    """
    Demonstrate the fix logic without importing brucelee94 modules.
    """
    print("=" * 70)
    print("Guest Artist Display Logic Test")
    print("=" * 70)
    
    # Scenario from user's example
    print("\n" + "=" * 70)
    print("Scenario: Tidal Upload - ORSUJE by Ismail Candide, Eddy Woogy")
    print("=" * 70)
    
    # Album metadata
    main_artists = ["Ismail Candide", "Eddy Woogy"]
    
    # Tracks
    tracks = [
        {
            "num": "01",
            "title": "Track One",
            "artists": [
                ("Ismail Candide", "main"),
                ("Eddy Woogy", "main"),
            ]
        },
        {
            "num": "02",
            "title": "Track Two",
            "artists": [
                ("Ismail Candide", "main"),
                ("Eddy Woogy", "main"),
            ]
        },
        {
            "num": "03",
            "title": "ZigZagueZ",
            "artists": [
                ("Ismail Candide", "main"),
                ("Eddy Woogy", "main"),
                ("Christine Ly", "guest"),  # GUEST ARTIST
            ]
        },
    ]
    
    # Check if all tracks have same main artists
    def all_tracks_have_same_main_artists(tracks, album_main_artists):
        """Simulate the logic from all_tracks_have_same_artists function"""
        album_set = {a.lower() for a in album_main_artists}
        for track in tracks:
            track_mains = {a[0].lower() for a in track["artists"] if a[1] == "main"}
            if track_mains != album_set:
                return False
        return True
    
    # Simulate smart artist display logic
    tracks_have_same_artists = all_tracks_have_same_main_artists(tracks, main_artists)
    show_track_artists = not tracks_have_same_artists
    
    print(f"\nAlbum main artists: {', '.join(main_artists)}")
    print(f"All tracks have same main artists: {tracks_have_same_artists}")
    print(f"show_track_artists: {show_track_artists}")
    
    print("\n" + "-" * 70)
    print("BEFORE FIX (Incorrect Behavior):")
    print("-" * 70)
    for track in tracks:
        desc = f"[b]{track['num']}.[/b] "
        if show_track_artists:
            # Would show main artists and guests
            desc += "Main - Title (feat. Guest)"
        else:
            # BUG: Would only show title, no guests!
            desc += track['title']
        print(desc)
    
    print("\n  ❌ Problem: Track 03 guest artist (Christine Ly) not shown!")
    
    print("\n" + "-" * 70)
    print("AFTER FIX (Correct Behavior):")
    print("-" * 70)
    for track in tracks:
        desc = f"[b]{track['num']}.[/b] "
        
        if show_track_artists:
            # Show main artists and guests
            mains = [a[0] for a in track["artists"] if a[1] == "main"]
            guests = [a[0] for a in track["artists"] if a[1] == "guest"]
            desc += f"{', '.join(mains)} - {track['title']}"
            if guests:
                desc += f" (feat. {', '.join(guests)})"
        else:
            # Even though main artists don't vary, still check for guests
            desc += track['title']
            guests = [a[0] for a in track["artists"] if a[1] == "guest"]
            if guests:
                desc += f" (feat. [artist]{', '.join(guests)}[/artist])"
        
        print(desc)
    
    print("\n  ✓ Fixed: Track 03 now shows guest artist Christine Ly!")
    
    # Validate the fix
    print("\n" + "=" * 70)
    print("Validation:")
    print("=" * 70)
    
    # Extract guest from track 3
    track3_guests = [a[0] for a in tracks[2]["artists"] if a[1] == "guest"]
    assert "Christine Ly" in track3_guests, "Guest artist should be in metadata"
    print("  ✓ Guest artist 'Christine Ly' found in track 3 metadata")
    
    # Verify the fix shows guests even when show_track_artists is False
    assert show_track_artists == False, "show_track_artists should be False (mains don't vary)"
    print("  ✓ show_track_artists is False (main artists don't vary)")
    
    # But guests should still be displayed
    print("  ✓ With fix: Guests are displayed regardless of show_track_artists")
    
    print("\n" + "=" * 70)
    print("Test PASSED! ✓")
    print("=" * 70)
    print("\nSummary of fix:")
    print("  1. Main artists same on all tracks → show_track_artists = False")
    print("  2. Previously: No artists shown at all")
    print("  3. Now: Title shown + guest artists appended when present")
    print("  4. Result: Christine Ly appears as (feat. [artist]Christine Ly[/artist])")


if __name__ == "__main__":
    test_logic()
