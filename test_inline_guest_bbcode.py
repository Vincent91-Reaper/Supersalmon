"""
Test inline guest artist BBCode feature
"""

import re

def add_artist_bbcode_to_feat(title):
    """
    Add [artist] BBCode tags to guest artists in (feat. ...) mentions within track title.
    
    Detects patterns like:
    - (feat. Name)
    - (ft. Name)
    - (featuring Name)
    
    And transforms them to:
    - (feat. [artist]Name[/artist])
    
    Handles multiple guests separated by ", " and " & "
    """
    # Pattern to match (feat. ...), (ft. ...), or (featuring ...)
    pattern = r'\((feat\.|ft\.|featuring)\s+([^)]+)\)'
    
    def add_bbcode_to_match(match):
        feat_keyword = match.group(1)  # "feat.", "ft.", or "featuring"
        guests_text = match.group(2)  # The guest names
        
        # Split guests on ", " and then on " & "
        guest_list = []
        for comma_part in guests_text.split(', '):
            for guest in comma_part.split(' & '):
                guest = guest.strip()
                if guest:
                    guest_list.append(guest)
        
        # Create BBCode version
        if len(guest_list) == 1:
            bbcode_guests = f"[artist]{guest_list[0]}[/artist]"
        elif len(guest_list) == 2:
            bbcode_guests = f"[artist]{guest_list[0]}[/artist] & [artist]{guest_list[1]}[/artist]"
        else:
            # Multiple guests: use ", " for all but last, " & " for last
            bbcode_guests = ', '.join([f"[artist]{g}[/artist]" for g in guest_list[:-1]])
            bbcode_guests += f" & [artist]{guest_list[-1]}[/artist]"
        
        return f"({feat_keyword} {bbcode_guests})"
    
    # Replace all feat. mentions with BBCode version
    return re.sub(pattern, add_bbcode_to_match, title, flags=re.IGNORECASE)

def test_single_guest_feat():
    """Test (feat. Single Guest)"""
    title = "My love is forever (feat. Jay Heson)"
    result = add_artist_bbcode_to_feat(title)
    expected = "My love is forever (feat. [artist]Jay Heson[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Single guest with feat. - PASSED")

def test_single_guest_ft():
    """Test (ft. Single Guest)"""
    title = "Track Title (ft. Artist Name)"
    result = add_artist_bbcode_to_feat(title)
    expected = "Track Title (ft. [artist]Artist Name[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Single guest with ft. - PASSED")

def test_single_guest_featuring():
    """Test (featuring Single Guest)"""
    title = "Song (featuring Guest Artist)"
    result = add_artist_bbcode_to_feat(title)
    expected = "Song (featuring [artist]Guest Artist[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Single guest with featuring - PASSED")

def test_multiple_guests_comma():
    """Test (feat. A, B, C)"""
    title = "Track (feat. Artist A, Artist B, Artist C)"
    result = add_artist_bbcode_to_feat(title)
    expected = "Track (feat. [artist]Artist A[/artist], [artist]Artist B[/artist] & [artist]Artist C[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Multiple guests with comma - PASSED")

def test_multiple_guests_ampersand():
    """Test (feat. A & B)"""
    title = "Track (feat. Artist A & Artist B)"
    result = add_artist_bbcode_to_feat(title)
    expected = "Track (feat. [artist]Artist A[/artist] & [artist]Artist B[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Multiple guests with ampersand - PASSED")

def test_multiple_guests_mixed():
    """Test (feat. A, B & C)"""
    title = "Track (feat. Artist A, Artist B & Artist C)"
    result = add_artist_bbcode_to_feat(title)
    expected = "Track (feat. [artist]Artist A[/artist], [artist]Artist B[/artist] & [artist]Artist C[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Multiple guests with mixed separators - PASSED")

def test_no_feat_in_title():
    """Test title without feat."""
    title = "Regular Track Title"
    result = add_artist_bbcode_to_feat(title)
    expected = "Regular Track Title"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ No feat. in title - PASSED")

def test_case_insensitive():
    """Test case insensitive matching"""
    title1 = "Track (FEAT. Artist)"
    result1 = add_artist_bbcode_to_feat(title1)
    expected1 = "Track (FEAT. [artist]Artist[/artist])"
    assert result1 == expected1, f"Expected: {expected1}, Got: {result1}"
    
    title2 = "Track (Ft. Artist)"
    result2 = add_artist_bbcode_to_feat(title2)
    expected2 = "Track (Ft. [artist]Artist[/artist])"
    assert result2 == expected2, f"Expected: {expected2}, Got: {result2}"
    
    title3 = "Track (Featuring Artist)"
    result3 = add_artist_bbcode_to_feat(title3)
    expected3 = "Track (Featuring [artist]Artist[/artist])"
    assert result3 == expected3, f"Expected: {expected3}, Got: {result3}"
    
    print("✓ Case insensitive matching - PASSED")

def test_multiple_feat_in_title():
    """Test multiple feat. mentions in one title"""
    title = "Track (feat. Artist A) Remix (feat. Artist B)"
    result = add_artist_bbcode_to_feat(title)
    expected = "Track (feat. [artist]Artist A[/artist]) Remix (feat. [artist]Artist B[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Multiple feat. mentions - PASSED")

def test_real_world_example():
    """Test real-world example from problem statement"""
    title = "My love is forever (feat. Jay Heson)"
    result = add_artist_bbcode_to_feat(title)
    expected = "My love is forever (feat. [artist]Jay Heson[/artist])"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Real-world example - PASSED")

if __name__ == "__main__":
    print("\nTesting inline guest artist BBCode feature...\n")
    
    test_single_guest_feat()
    test_single_guest_ft()
    test_single_guest_featuring()
    test_multiple_guests_comma()
    test_multiple_guests_ampersand()
    test_multiple_guests_mixed()
    test_no_feat_in_title()
    test_case_insensitive()
    test_multiple_feat_in_title()
    test_real_world_example()
    
    print("\nAll tests passed! ✓\n")
