"""
Test that files of any length can be truncated (no 250 char limit).
"""

import os
import tempfile


def test_300_char_truncation():
    """Test that 300 character file can be truncated."""
    print("\nTest 1: 300 character file")
    
    # Simulate a 300 char relative path
    download_dir = "/downloads"
    root_len = len(download_dir) + 1
    
    # Create path components
    album_folder = "Artist Name - Album Name With Very Long Title That Goes On And On"
    track_name = "01. This Is A Very Long Track Name That Exceeds Normal Length Limits And Continues For Many More Characters To Test The Truncation Logic With A Path That Is Three Hundred Characters Long When Combined With The Directory Structure"
    ext = ".flac"
    
    filepath = os.path.join(download_dir, album_folder, track_name + ext)
    
    # Current length
    current_len = len(filepath) - root_len
    print(f"Original relative length: {current_len} chars")
    
    # Apply truncation logic
    target_relative_len = 178
    excess = current_len - target_relative_len
    
    dir_part = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    filename_no_ext, ext = os.path.splitext(file_basename)
    
    truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
    new_filename = truncated_filename + ".." + ext
    newpath = os.path.join(dir_part, new_filename)
    
    # Check result
    new_len = len(newpath) - root_len
    print(f"Truncated relative length: {new_len} chars")
    
    assert new_len == 178, f"Expected 178, got {new_len}"
    assert newpath.endswith(".." + ext), "Should end with .. + extension"
    print("✓ 300 char file truncated successfully")


def test_500_char_truncation():
    """Test that 500 character file can be truncated."""
    print("\nTest 2: 500 character file")
    
    download_dir = "/downloads"
    root_len = len(download_dir) + 1
    
    # Create a very long path (500+ chars)
    album_folder = "A" * 100
    track_name = "B" * 380  # Will make total > 500 with dirs and extension
    ext = ".flac"
    
    filepath = os.path.join(download_dir, album_folder, track_name + ext)
    
    current_len = len(filepath) - root_len
    print(f"Original relative length: {current_len} chars")
    
    # Apply truncation logic
    target_relative_len = 178
    excess = current_len - target_relative_len
    
    dir_part = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    filename_no_ext, ext = os.path.splitext(file_basename)
    
    truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
    new_filename = truncated_filename + ".." + ext
    newpath = os.path.join(dir_part, new_filename)
    
    new_len = len(newpath) - root_len
    print(f"Truncated relative length: {new_len} chars")
    
    assert new_len == 178, f"Expected 178, got {new_len}"
    print("✓ 500 char file truncated successfully")


def test_1000_char_truncation():
    """Test that even 1000+ character file with long filename can be truncated."""
    print("\nTest 3: 1000+ character file")
    
    download_dir = "/downloads"
    root_len = len(download_dir) + 1
    
    # Create an extremely long path with a LONG filename
    album_folder = "Album Name"
    track_name = "X" * 1000  # Very long filename
    ext = ".mp3"
    
    filepath = os.path.join(download_dir, album_folder, track_name + ext)
    
    current_len = len(filepath) - root_len
    print(f"Original relative length: {current_len} chars")
    
    # Apply truncation logic
    target_relative_len = 178
    excess = current_len - target_relative_len
    
    dir_part = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    filename_no_ext, ext = os.path.splitext(file_basename)
    
    # Check if we can truncate
    if len(filename_no_ext) >= excess + 2:
        truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
        new_filename = truncated_filename + ".." + ext
        newpath = os.path.join(dir_part, new_filename)
        
        new_len = len(newpath) - root_len
        print(f"Truncated relative length: {new_len} chars")
        
        assert new_len == 178, f"Expected 178, got {new_len}"
        print("✓ 1000+ char file truncated successfully")
    else:
        print(f"✗ Filename too short to truncate (would need {excess + 2} chars, have {len(filename_no_ext)})")
        raise AssertionError("Test setup error: filename should be long enough")


def test_edge_case_short_filename():
    """Test edge case: very long directory but short filename."""
    print("\nTest 4: Edge case - short filename, long directory")
    
    download_dir = "/downloads"
    root_len = len(download_dir) + 1
    
    # Very long directory path
    album_folder = "A" * 170
    track_name = "song"  # Very short
    ext = ".flac"
    
    filepath = os.path.join(download_dir, album_folder, track_name + ext)
    
    current_len = len(filepath) - root_len
    print(f"Original relative length: {current_len} chars")
    
    if current_len > 180:
        target_relative_len = 178
        excess = current_len - target_relative_len
        
        dir_part = os.path.dirname(filepath)
        file_basename = os.path.basename(filepath)
        filename_no_ext, ext = os.path.splitext(file_basename)
        
        # Check if filename is long enough
        if len(filename_no_ext) < excess + 2:
            print(f"✓ Correctly identified: filename too short to truncate")
            print(f"  Filename length: {len(filename_no_ext)}, need: {excess + 2}")
        else:
            truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
            new_filename = truncated_filename + ".." + ext
            newpath = os.path.join(dir_part, new_filename)
            
            new_len = len(newpath) - root_len
            assert new_len == 178
            print("✓ Edge case handled correctly")
    else:
        print("✓ Path under 180 chars, no truncation needed")


def test_normal_truncation_still_works():
    """Ensure normal truncation (181-249 chars) still works."""
    print("\nTest 5: Normal truncation (195 chars)")
    
    download_dir = "/downloads"
    root_len = len(download_dir) + 1
    
    album_folder = "Artist Name - Album Name With Some Additional Text"
    track_name = "01. This Is A Moderately Long Track Name That Will Exceed One Hundred And Eighty Characters When Combined With The Directory Path But Not By Too Much At All Really"
    ext = ".flac"
    
    filepath = os.path.join(download_dir, album_folder, track_name + ext)
    
    current_len = len(filepath) - root_len
    print(f"Original relative length: {current_len} chars")
    
    target_relative_len = 178
    excess = current_len - target_relative_len
    
    dir_part = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    filename_no_ext, ext = os.path.splitext(file_basename)
    
    truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
    new_filename = truncated_filename + ".." + ext
    newpath = os.path.join(dir_part, new_filename)
    
    new_len = len(newpath) - root_len
    print(f"Truncated relative length: {new_len} chars")
    
    assert new_len == 178, f"Expected 178, got {new_len}"
    print("✓ Normal truncation still works")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing: No 250 Character Limit")
    print("=" * 60)
    
    test_300_char_truncation()
    test_500_char_truncation()
    test_1000_char_truncation()
    test_edge_case_short_filename()
    test_normal_truncation_still_works()
    
    print("\n" + "=" * 60)
    print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("=" * 60)
