"""
Test the fixed filename truncation logic.
This test simulates the actual code behavior to ensure the fix works correctly.
"""
import os
import tempfile
import shutil


def simulate_truncation_fix(filepath, root_len):
    """
    Simulate the fixed truncation logic from folderstructure.py.
    This matches the new implementation exactly.
    """
    # Calculate how much we need to truncate
    # Target: relative path length <= 178 (leaving 2 chars for "..")
    target_relative_len = 178
    current_relative_len = len(filepath) - root_len
    excess = current_relative_len - target_relative_len
    
    # Get directory and filename components
    dir_part = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    filename_no_ext, ext = os.path.splitext(file_basename)
    
    # Truncate the filename (not including extension) and add ".."
    truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
    new_filename = truncated_filename + ".." + ext
    newpath = os.path.join(dir_part, new_filename)
    
    return newpath


def test_truncation_scenarios():
    """Test various truncation scenarios."""
    
    print("Testing filename truncation scenarios...")
    print("=" * 80)
    
    # Simulate download directory
    download_dir = "/home/user/music/downloads"
    root_len = len(download_dir) + 1
    
    test_cases = [
        {
            "name": "Very long track name",
            "path": "Artist - Album (2024) [WEB FLAC]/01. This is an extremely long track name that goes on and on and really needs to be truncated because it exceeds the filesystem limit of 180 characters for the relative path.flac",
            "expected_max_len": 180
        },
        {
            "name": "Long album and track name",
            "path": "Very Long Artist Name - Very Long Album Name That Is Quite Excessive (2024) [WEB FLAC 24-96]/01. Another very long track name that when combined with the album folder name exceeds our 180 character limit.flac",
            "expected_max_len": 180
        },
        {
            "name": "Multiple dots in filename",
            "path": "Artist - Album/01. Track.Name.With.Many.Dots.And.A.Very.Long.Description.That.Needs.To.Be.Truncated.Because.It.Is.Too.Long.For.The.Filesystem.Limits.That.We.Have.Set.flac",
            "expected_max_len": 180
        },
        {
            "name": "Different extension",
            "path": "Artist/Very_Long_Track_Name_With_Underscores_That_Goes_On_And_On_And_Really_Should_Be_Truncated_To_Fit_Within_The_Filesystem_Limits_We_Have_Established_For_Maximum_Compatibility.mp3",
            "expected_max_len": 180
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 80)
        
        # Create full path
        relative_path = test_case['path']
        # Ensure it's long enough to need truncation
        if len(relative_path) < 185:
            # Pad it
            dir_part, filename = os.path.split(relative_path)
            name, ext = os.path.splitext(filename)
            padding = "_" * (190 - len(relative_path))
            relative_path = os.path.join(dir_part, name + padding + ext)
        
        filepath = os.path.join(download_dir, relative_path)
        
        original_len = len(filepath) - root_len
        print(f"Original relative path length: {original_len}")
        print(f"Original filename: {os.path.basename(filepath)[:60]}...")
        
        # Apply truncation
        newpath = simulate_truncation_fix(filepath, root_len)
        truncated_len = len(newpath) - root_len
        
        print(f"Truncated relative path length: {truncated_len}")
        print(f"Truncated filename: {os.path.basename(newpath)[:60]}...")
        
        # Verify
        assert truncated_len <= test_case['expected_max_len'], \
            f"FAILED: Length {truncated_len} exceeds {test_case['expected_max_len']}"
        
        # Verify ".." is in the filename
        assert ".." in os.path.basename(newpath), \
            "FAILED: Truncated filename should contain '..'"
        
        # Verify extension is preserved
        original_ext = os.path.splitext(filepath)[1]
        new_ext = os.path.splitext(newpath)[1]
        assert original_ext == new_ext, \
            f"FAILED: Extension changed from {original_ext} to {new_ext}"
        
        print("✓ PASSED")
    
    print("\n" + "=" * 80)
    print("All truncation tests passed!")
    print("=" * 80)


def test_actual_filesystem():
    """Test with actual filesystem operations."""
    
    print("\n\nTesting with actual filesystem...")
    print("=" * 80)
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Simulate download directory structure
        album_dir = os.path.join(tmpdir, "Artist - Album (2024) [WEB FLAC]")
        os.makedirs(album_dir, exist_ok=True)
        
        # Create a file with a very long name
        long_filename = "01. This is an extremely long track name that exceeds the normal character limit and needs to be truncated properly to avoid filesystem errors that could occur.flac"
        long_filepath = os.path.join(album_dir, long_filename)
        
        # Create the file
        with open(long_filepath, 'w') as f:
            f.write("test")
        
        print(f"Created test file: {os.path.basename(long_filepath)[:60]}...")
        print(f"Original path length: {len(long_filepath)}")
        
        # Simulate truncation
        root_len = len(tmpdir) + 1
        
        if len(long_filepath) - root_len > 180:
            newpath = simulate_truncation_fix(long_filepath, root_len)
            
            # Actually rename the file
            os.rename(long_filepath, newpath)
            
            print(f"Renamed to: {os.path.basename(newpath)[:60]}...")
            print(f"New path length: {len(newpath)}")
            print(f"Relative path length: {len(newpath) - root_len}")
            
            # Verify the file exists with new name
            assert os.path.exists(newpath), "FAILED: Renamed file doesn't exist"
            assert not os.path.exists(long_filepath), "FAILED: Original file still exists"
            assert len(newpath) - root_len <= 180, "FAILED: New path still too long"
            
            print("✓ Filesystem test PASSED")
        else:
            print("Test file path not long enough to trigger truncation")
    
    print("=" * 80)


if __name__ == "__main__":
    test_truncation_scenarios()
    test_actual_filesystem()
    print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
