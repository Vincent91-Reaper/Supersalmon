"""
Test to verify DJ Mix track artist display in torrent description.

This test verifies that:
1. Guest artist formatting is removed for DJ Mix uploads
2. Track artists from file tags are displayed correctly
3. Non-DJ Mix uploads still use guest artist formatting
"""

def test_dj_mix_description_format():
    """Test that DJ Mix uses file-based artists without guest separation."""
    from brucelee94.uploader.upload import generate_description
    from brucelee94.common import str_to_int_if_int
    
    # Mock track data with file tags
    class MockTag:
        def __init__(self, artist, title, tracknumber, discnumber=None):
            self.artist = artist
            self.title = title
            self.tracknumber = tracknumber
            self.discnumber = discnumber or "1"
    
    # DJ Mix track data - artists in file tags
    dj_mix_track_data = {
        "track1.flac": {
            "duration": 240,  # 4:00
            "t": MockTag("The Junkies", "Parts & Labour (Mixed)", "1")
        },
        "track2.flac": {
            "duration": 180,  # 3:00
            "t": MockTag("Different Artist", "Another Track (Mixed)", "2")
        }
    }
    
    # DJ Mix metadata
    dj_mix_metadata = {
        "title": "Boiler Room - Dubfire b2b Richie Hawtin",
        "rls_type": "DJ Mix",
        "artists": [
            ("Dubfire", "djcompiler"),
            ("Richie Hawtin", "djcompiler"),
            ("The Junkies", "main"),
            ("Different Artist", "main")
        ],
        "date": "May 03, 2016"
    }
    
    # Generate description for DJ Mix
    dj_mix_desc = generate_description(dj_mix_track_data, dj_mix_metadata)
    
    print("\n=== DJ MIX DESCRIPTION ===")
    print(dj_mix_desc)
    
    # Verify DJ Mix format:
    # - Should have track artists from file tags
    # - Should NOT have (feat. ...) suffixes
    assert "[artist]The Junkies[/artist]" in dj_mix_desc, "DJ Mix should show track artist from file tags"
    assert "[artist]Different Artist[/artist]" in dj_mix_desc, "DJ Mix should show second track artist from file tags"
    assert "(feat." not in dj_mix_desc.lower(), "DJ Mix should NOT have feat. suffixes"
    assert "[artist]Dubfire[/artist]" in dj_mix_desc, "DJ Mix header should show DJ/Compiler"
    assert "[artist]Richie Hawtin[/artist]" in dj_mix_desc, "DJ Mix header should show both DJs"
    
    print("✓ DJ Mix description format is correct!")
    print("  - Uses file-based track artists")
    print("  - No guest artist separation")
    print("  - Shows DJ/Compiler in header")


def test_regular_album_description_format():
    """Test that non-DJ Mix albums still use guest artist formatting."""
    from brucelee94.uploader.upload import generate_description
    
    # Mock track data
    class MockTag:
        def __init__(self, artist, title, tracknumber, discnumber=None):
            self.artist = artist
            self.title = title
            self.tracknumber = tracknumber
            self.discnumber = discnumber or "1"
    
    # Regular Various Artists album track data
    regular_track_data = {
        "track1.flac": {
            "duration": 225,  # 3:45
            "t": MockTag("Jon Hansen", "My love is forever", "1")
        }
    }
    
    # Regular album metadata with guest artists
    regular_metadata = {
        "title": "Various Artists - Compilation",
        "rls_type": "Album",  # NOT DJ Mix
        "artists": [
            ("Jon Hansen", "main"),
            ("Mary Doufle", "main"),
            ("Barbara Lamon", "main")
        ],
        "tracks": {
            "1": {
                "1": {
                    "title": "My love is forever",
                    "artists": [
                        ("Jon Hansen", "main"),
                        ("Mary Doufle", "guest")
                    ]
                }
            }
        },
        "date": "January 01, 2025"
    }
    
    # Generate description for regular album
    regular_desc = generate_description(regular_track_data, regular_metadata)
    
    print("\n=== REGULAR ALBUM DESCRIPTION ===")
    print(regular_desc)
    
    # Verify regular album format:
    # - Should use metadata-based artists
    # - Should have (feat. ...) for guest artists
    assert "[artist]Jon Hansen[/artist]" in regular_desc, "Should show main artist"
    assert "(feat. [artist]Mary Doufle[/artist])" in regular_desc, "Should show guest artist in (feat. ...)"
    assert "Various Artists" in regular_desc, "Should show Various Artists header"
    
    print("✓ Regular album description format is correct!")
    print("  - Uses metadata-based artists")
    print("  - Shows guest artists in (feat. ...)")


if __name__ == "__main__":
    print("Testing DJ Mix and Regular Album Description Formats")
    print("=" * 60)
    
    test_dj_mix_description_format()
    test_regular_album_description_format()
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("\nSummary:")
    print("  1. DJ Mix: File-based artists, no feat. separation")
    print("  2. Regular: Metadata-based artists, with feat. separation")
