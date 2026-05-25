#!/usr/bin/env python3
"""
Test to verify that Beatport track number correction works properly.

This tests the fix for the issue where Beatport downloads sometimes have
all files labeled as track "01" in both filename and metadata.
"""

from collections import namedtuple
from collections import defaultdict


# Mock TagFile structure
MockTag = namedtuple('MockTag', [
    'tracknumber', 'discnumber', 'tracktotal', 'disctotal',
    'artist', 'title', 'replay_gain', 'peak', 'isrc'
])


def create_track_list_original(tags, overwrite=False):
    """Original implementation that has the bug."""
    tracks = defaultdict(dict)
    for trackindex, (_, track) in enumerate(sorted(tags.items(), key=lambda k: k[0]), 1):
        discnumber = track.discnumber or "1"
        tracknumber = (
            str(track.tracknumber).split("/")[0]
            if (
                track.tracknumber
                and str(track.tracknumber).split("/")[0].isdigit()
                and int(str(track.tracknumber).split("/")[0]) > 0
            )
            else str(trackindex)
        )
        tracks[discnumber][tracknumber] = {
            "track#": tracknumber,
            "disc#": discnumber,
            "title": track.title,
        }
    return dict(tracks)


def create_track_list_fixed(tags, overwrite=False):
    """Fixed implementation that detects and handles duplicate track numbers."""
    tracks = defaultdict(dict)
    # First pass: collect track numbers to detect duplicates
    track_numbers = []
    for _, track in sorted(tags.items(), key=lambda k: k[0]):
        tracknumber = (
            str(track.tracknumber).split("/")[0]
            if (
                track.tracknumber
                and str(track.tracknumber).split("/")[0].isdigit()
                and int(str(track.tracknumber).split("/")[0]) > 0
            )
            else None
        )
        track_numbers.append(tracknumber)
    
    # Check if track numbers are duplicated (e.g., all files have "01")
    # If duplicates exist, use sequential numbering instead
    has_duplicates = len(track_numbers) != len(set(track_numbers))
    
    for trackindex, (_, track) in enumerate(sorted(tags.items(), key=lambda k: k[0]), 1):
        discnumber = track.discnumber or "1"
        # Use file-based track number unless duplicates detected
        if has_duplicates:
            # Use sequential position when duplicates exist
            tracknumber = str(trackindex)
        else:
            tracknumber = (
                str(track.tracknumber).split("/")[0]
                if (
                    track.tracknumber
                    and str(track.tracknumber).split("/")[0].isdigit()
                    and int(str(track.tracknumber).split("/")[0]) > 0
                )
                else str(trackindex)
            )
        tracks[discnumber][tracknumber] = {
            "track#": tracknumber,
            "disc#": discnumber,
            "title": track.title,
        }
    return dict(tracks)


def test_beatport_duplicate_track_numbers():
    """Test the scenario from user's bug report."""
    print("\n" + "="*70)
    print("TEST: Beatport Duplicate Track Numbers (All tracks labeled as '01')")
    print("="*70)
    
    # Create mock tags for 3 files all with track number "01"
    tags = {
        "01. All About Cuts (Original Mix).flac": MockTag(
            tracknumber="01", discnumber="1", tracktotal=None, disctotal=None,
            artist=["Frank Martiniq"], title="All About Cuts (Original Mix)",
            replay_gain=None, peak=None, isrc=None
        ),
        "01. Elastic Plastic (Original Mix).flac": MockTag(
            tracknumber="01", discnumber="1", tracktotal=None, disctotal=None,
            artist=["Frank Martiniq"], title="Elastic Plastic (Original Mix)",
            replay_gain=None, peak=None, isrc=None
        ),
        "01. Snoop Troop (Original Mix).flac": MockTag(
            tracknumber="01", discnumber="1", tracktotal=None, disctotal=None,
            artist=["Frank Martiniq"], title="Snoop Troop (Original Mix)",
            replay_gain=None, peak=None, isrc=None
        ),
    }
    
    print("\nInput: 3 files all with track number '01' in metadata")
    for filename in sorted(tags.keys()):
        print(f"  - {filename} (track #{tags[filename].tracknumber})")
    
    # Test original (buggy) implementation
    print("\n--- Original Implementation (BUGGY) ---")
    tracks_original = create_track_list_original(tags)
    print(f"Number of tracks created: {sum(len(disc) for disc in tracks_original.values())}")
    print("Tracks:")
    for disc, disc_tracks in tracks_original.items():
        for trackno, track in sorted(disc_tracks.items()):
            print(f"  Disc {disc}, Track {trackno}: {track['title']}")
    
    # Test fixed implementation
    print("\n--- Fixed Implementation (CORRECT) ---")
    tracks_fixed = create_track_list_fixed(tags)
    print(f"Number of tracks created: {sum(len(disc) for disc in tracks_fixed.values())}")
    print("Tracks:")
    for disc, disc_tracks in tracks_fixed.items():
        for trackno, track in sorted(disc_tracks.items(), key=lambda x: int(x[0])):
            print(f"  Disc {disc}, Track {trackno}: {track['title']}")
    
    # Verify the fix
    assert sum(len(disc) for disc in tracks_original.values()) == 1, "Original should only have 1 track (bug!)"
    assert sum(len(disc) for disc in tracks_fixed.values()) == 3, "Fixed should have all 3 tracks"
    assert "1" in tracks_fixed["1"], "Track 1 should exist"
    assert "2" in tracks_fixed["1"], "Track 2 should exist"
    assert "3" in tracks_fixed["1"], "Track 3 should exist"
    assert tracks_fixed["1"]["1"]["title"] == "All About Cuts (Original Mix)"
    assert tracks_fixed["1"]["2"]["title"] == "Elastic Plastic (Original Mix)"
    assert tracks_fixed["1"]["3"]["title"] == "Snoop Troop (Original Mix)"
    
    print("\n✓✓✓ TEST PASSED ✓✓✓")
    print("Fixed implementation correctly creates 3 tracks with sequential numbers!")


def test_normal_track_numbers():
    """Test that normal (non-duplicate) track numbers still work correctly."""
    print("\n" + "="*70)
    print("TEST: Normal Track Numbers (Should not be affected)")
    print("="*70)
    
    # Create mock tags for 3 files with correct track numbers
    tags = {
        "01. Track One.flac": MockTag(
            tracknumber="1", discnumber="1", tracktotal=None, disctotal=None,
            artist=["Artist"], title="Track One",
            replay_gain=None, peak=None, isrc=None
        ),
        "02. Track Two.flac": MockTag(
            tracknumber="2", discnumber="1", tracktotal=None, disctotal=None,
            artist=["Artist"], title="Track Two",
            replay_gain=None, peak=None, isrc=None
        ),
        "03. Track Three.flac": MockTag(
            tracknumber="3", discnumber="1", tracktotal=None, disctotal=None,
            artist=["Artist"], title="Track Three",
            replay_gain=None, peak=None, isrc=None
        ),
    }
    
    print("\nInput: 3 files with correct track numbers (1, 2, 3)")
    
    # Test fixed implementation
    tracks = create_track_list_fixed(tags)
    print(f"Number of tracks created: {sum(len(disc) for disc in tracks.values())}")
    print("Tracks:")
    for disc, disc_tracks in tracks.items():
        for trackno, track in sorted(disc_tracks.items(), key=lambda x: int(x[0])):
            print(f"  Disc {disc}, Track {trackno}: {track['title']}")
    
    # Verify
    assert sum(len(disc) for disc in tracks.values()) == 3
    assert tracks["1"]["1"]["title"] == "Track One"
    assert tracks["1"]["2"]["title"] == "Track Two"
    assert tracks["1"]["3"]["title"] == "Track Three"
    
    print("\n✓✓✓ TEST PASSED ✓✓✓")
    print("Normal track numbers work correctly!")


if __name__ == "__main__":
    test_beatport_duplicate_track_numbers()
    test_normal_track_numbers()
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED!")
    print("="*70)
    print("\nThe fix correctly handles:")
    print("  1. Beatport files with duplicate track numbers (all '01')")
    print("  2. Normal files with correct sequential track numbers")
    print("\nBoth scenarios work as expected!")
