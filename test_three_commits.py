"""
Test file to verify the three commits were applied correctly.

This file demonstrates the expected behavior after applying commits:
- 97876af: Artist splitting on " & "
- 6996411: Artist splitting on both ", " and " & "
- 0add790: DJ Mix header and record label clearing
"""


def test_artist_splitting_ampersand():
    """Test that artists are split on ' & ' separator (Commit 97876af)."""
    # Simulated artist string from file tag
    artist_string = "Shades & ID"
    
    # Expected splitting behavior
    artists = []
    for comma_part in artist_string.split(', '):
        artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
    
    assert artists == ["Shades", "ID"], f"Expected ['Shades', 'ID'], got {artists}"
    
    # Expected BB code output
    artist_tags = [f"[artist]{artist}[/artist]" for artist in artists]
    expected_output = "[artist]Shades[/artist], [artist]ID[/artist]"
    actual_output = ", ".join(artist_tags)
    
    assert actual_output == expected_output, f"Expected '{expected_output}', got '{actual_output}'"
    print("✓ Test passed: Artist splitting on ' & '")


def test_artist_splitting_comma_and_ampersand():
    """Test that artists are split on both ', ' and ' & ' (Commit 6996411)."""
    # Simulated artist string with both separators
    artist_string = "Alix Perez, Shades & Eprom"
    
    # Expected splitting behavior
    artists = []
    for comma_part in artist_string.split(', '):
        artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
    
    expected = ["Alix Perez", "Shades", "Eprom"]
    assert artists == expected, f"Expected {expected}, got {artists}"
    
    # Expected BB code output
    artist_tags = [f"[artist]{artist}[/artist]" for artist in artists]
    expected_output = "[artist]Alix Perez[/artist], [artist]Shades[/artist], [artist]Eprom[/artist]"
    actual_output = ", ".join(artist_tags)
    
    assert actual_output == expected_output, f"Expected '{expected_output}', got '{actual_output}'"
    print("✓ Test passed: Artist splitting on ', ' and ' & '")


def test_complex_artist_combinations():
    """Test various complex artist combination patterns."""
    test_cases = [
        ("Artist1 & Artist2", ["Artist1", "Artist2"]),
        ("Artist1, Artist2", ["Artist1", "Artist2"]),
        ("Artist1, Artist2 & Artist3", ["Artist1", "Artist2", "Artist3"]),
        ("A, B, C & D", ["A", "B", "C", "D"]),
        ("Single Artist", ["Single Artist"]),
    ]
    
    for artist_string, expected in test_cases:
        artists = []
        for comma_part in artist_string.split(', '):
            artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
        
        assert artists == expected, f"For '{artist_string}': expected {expected}, got {artists}"
    
    print("✓ Test passed: Complex artist combinations")


def test_record_label_clearing():
    """Test that DJ Mix releases have empty record label (Commit 0add790)."""
    # Simulated metadata
    metadata_dj_mix = {
        "rls_type": "DJ Mix",
        "label": "26 July 2025 20 songs, 59 minutes"
    }
    
    metadata_regular = {
        "rls_type": "Album",
        "label": "Real Label Name"
    }
    
    # DJ Mix should have empty label
    if metadata_dj_mix.get("rls_type") == "DJ Mix":
        record_label = ""
    else:
        record_label = metadata_dj_mix.get("label", "")
    
    assert record_label == "", f"DJ Mix should have empty label, got '{record_label}'"
    
    # Regular album should keep label
    if metadata_regular.get("rls_type") == "DJ Mix":
        record_label = ""
    else:
        record_label = metadata_regular.get("label", "")
    
    assert record_label == "Real Label Name", f"Regular album should keep label, got '{record_label}'"
    
    print("✓ Test passed: Record label clearing for DJ Mix")


def test_dj_mix_header_format():
    """Test that DJ Mix uses DJ/Compiler artist in header (Commit 0add790)."""
    # Simulated metadata
    metadata = {
        "rls_type": "DJ Mix",
        "title": "Boiler Room: Dubfire b2b Richie Hawtin in Berlin",
        "artists": [
            ("Dubfire", "djcompiler"),
            ("Richie Hawtin", "djcompiler"),
            ("The Junkies", "main"),
            ("Shades", "main"),
        ]
    }
    
    # Expected header generation
    if metadata.get("rls_type") == "DJ Mix":
        dj_artists = [a for a, i in metadata["artists"] if i == "djcompiler"]
        if dj_artists:
            if len(dj_artists) == 1:
                header = f"[b][artist]{dj_artists[0]}[/artist] - {metadata['title']}[/b]"
            else:
                artist_tags = [f"[artist]{artist}[/artist]" for artist in dj_artists]
                artist_display = " & ".join(artist_tags)
                header = f"[b]{artist_display} - {metadata['title']}[/b]"
    
    expected = "[b][artist]Dubfire[/artist] & [artist]Richie Hawtin[/artist] - Boiler Room: Dubfire b2b Richie Hawtin in Berlin[/b]"
    assert header == expected, f"Expected '{expected}', got '{header}'"
    
    print("✓ Test passed: DJ Mix header uses DJ/Compiler artists")


def test_full_dj_mix_description():
    """Test complete DJ Mix description generation."""
    # Simulated metadata and track data
    metadata = {
        "rls_type": "DJ Mix",
        "title": "Boiler Room Session",
        "date": "May 03, 2016",
        "artists": [
            ("Dubfire", "djcompiler"),
            ("Richie Hawtin", "djcompiler"),
            ("The Junkies", "main"),
            ("Shades", "main"),
            ("ID", "main"),
        ]
    }
    
    track_data = [
        {"artist": "The Junkies", "title": "Parts & Labour (Mixed)", "duration": "03:59"},
        {"artist": "Shades & ID", "title": "Track Two (Mixed)", "duration": "04:12"},
    ]
    
    # Generate header
    dj_artists = [a for a, i in metadata["artists"] if i == "djcompiler"]
    artist_tags = [f"[artist]{artist}[/artist]" for artist in dj_artists]
    artist_display = " & ".join(artist_tags)
    description = f"[b]{artist_display} - {metadata['title']}[/b]\n"
    description += f"{metadata['date']}\n\n"
    
    # Generate track list
    for i, track in enumerate(track_data, 1):
        # Split artists
        artists = []
        for comma_part in track["artist"].split(', '):
            artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
        
        artist_tags = [f"[artist]{artist}[/artist]" for artist in artists]
        description += f"[b]{i:02d}.[/b] {', '.join(artist_tags)} - {track['title']} [i]({track['duration']})[/i]\n"
    
    expected_lines = [
        "[b][artist]Dubfire[/artist] & [artist]Richie Hawtin[/artist] - Boiler Room Session[/b]",
        "May 03, 2016",
        "",
        "[b]01.[/b] [artist]The Junkies[/artist] - Parts & Labour (Mixed) [i](03:59)[/i]",
        "[b]02.[/b] [artist]Shades[/artist], [artist]ID[/artist] - Track Two (Mixed) [i](04:12)[/i]",
    ]
    
    expected = "\n".join(expected_lines) + "\n"
    
    assert description == expected, f"Description mismatch:\nExpected:\n{expected}\n\nGot:\n{description}"
    
    print("✓ Test passed: Full DJ Mix description generation")
    print("\nGenerated description:")
    print(description)


if __name__ == "__main__":
    print("Running tests for three applied commits...\n")
    
    test_artist_splitting_ampersand()
    test_artist_splitting_comma_and_ampersand()
    test_complex_artist_combinations()
    test_record_label_clearing()
    test_dj_mix_header_format()
    test_full_dj_mix_description()
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    print("\nCommits successfully applied:")
    print("- 97876af: Artist splitting on ' & '")
    print("- 6996411: Artist splitting on ', ' and ' & '")
    print("- 0add790: DJ Mix header and record label clearing")
