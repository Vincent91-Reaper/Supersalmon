"""Test filename truncation logic."""
import os


def test_truncation_logic():
    """Test that the truncation logic correctly handles long filenames."""
    
    # Simulate the scenario
    root_len = len("/home/user/downloads") + 1  # 20
    
    # Example: A very long filename
    download_dir = "/home/user/downloads"
    relative_path = "Artist - Album (2024) [WEB FLAC]/01. This is an extremely long track name that exceeds the normal character limit and needs to be truncated properly to avoid filesystem errors.flac"
    
    # Full path
    filepath = os.path.join(download_dir, relative_path)
    print(f"Original filepath length (relative): {len(relative_path)}")
    print(f"Original filepath: {filepath}")
    
    # Current (buggy) logic from line 145
    filename, ext = os.path.splitext(filepath)
    buggy_newpath = filepath[: 178 - len(filename) - len(ext) * 2 + root_len] + ".." + ext
    print(f"\nBuggy logic result length (relative): {len(buggy_newpath) - root_len}")
    print(f"Buggy newpath: {buggy_newpath}")
    
    # Correct logic
    # We want: relative_path_length <= 180
    # Strategy: Truncate the filename part (without extension)
    target_relative_len = 178  # Leave 2 chars for ".."
    
    # Get directory part and filename
    dir_part = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    filename_no_ext, ext = os.path.splitext(file_basename)
    
    # Calculate current relative path length
    current_relative_len = len(filepath) - root_len
    
    # Calculate how much we need to remove
    excess = current_relative_len - target_relative_len
    
    # Truncate the filename (not including extension)
    # We add 2 for ".." that will be inserted
    truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
    
    # Construct new path
    new_filename = truncated_filename + ".." + ext
    correct_newpath = os.path.join(dir_part, new_filename)
    
    print(f"\nCorrect logic result length (relative): {len(correct_newpath) - root_len}")
    print(f"Correct newpath: {correct_newpath}")
    
    assert len(correct_newpath) - root_len <= 180, f"Length {len(correct_newpath) - root_len} exceeds 180"
    print("\n✓ Test passed!")


def test_edge_cases():
    """Test edge cases for filename truncation."""
    
    print("\n" + "="*80)
    print("Testing edge cases...")
    print("="*80)
    
    root_len = 20
    download_dir = "/home/user/downloads"
    
    # Case 1: Filename with multiple dots
    test_cases = [
        "A/01. Track.with.dots.in.name.flac",
        "A/track_with_underscores_and_very_long_name.flac",
        "Very Long Album Name (2024) [WEB FLAC 24-96]/01. Track.flac",
    ]
    
    for relative_path in test_cases:
        filepath = os.path.join(download_dir, relative_path)
        
        # Make it long enough to need truncation
        if len(relative_path) < 190:
            # Pad the filename to make it long
            dir_part, filename = os.path.split(filepath)
            name, ext = os.path.splitext(filename)
            padded_name = name + "_" * (200 - len(relative_path))
            filepath = os.path.join(dir_part, padded_name + ext)
        
        print(f"\nTest case: {os.path.basename(filepath)[:50]}...")
        print(f"Original length (relative): {len(filepath) - root_len}")
        
        # Apply correct logic
        target_relative_len = 178
        dir_part = os.path.dirname(filepath)
        file_basename = os.path.basename(filepath)
        filename_no_ext, ext = os.path.splitext(file_basename)
        
        current_relative_len = len(filepath) - root_len
        excess = current_relative_len - target_relative_len
        
        truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
        new_filename = truncated_filename + ".." + ext
        correct_newpath = os.path.join(dir_part, new_filename)
        
        result_len = len(correct_newpath) - root_len
        print(f"Truncated length (relative): {result_len}")
        print(f"New filename: {new_filename[:60]}...")
        
        assert result_len <= 180, f"Length {result_len} exceeds 180"
        print("✓ Passed")


if __name__ == "__main__":
    test_truncation_logic()
    test_edge_cases()
    print("\n" + "="*80)
    print("All tests passed!")
    print("="*80)
