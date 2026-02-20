#!/usr/bin/env python3
"""Test the fix for overtruncation."""

import os
import tempfile
import shutil

def test_truncation_to_180():
    """Test that files are truncated to exactly 180 chars, not 178."""
    
    # Create a temp directory to simulate download dir
    with tempfile.TemporaryDirectory() as tmpdir:
        download_dir = tmpdir
        root_len = len(download_dir) + 1
        
        print(f"Download dir: {download_dir}")
        print(f"root_len: {root_len}")
        print()
        
        # Create test files at different lengths
        album_dir = os.path.join(download_dir, "Test Album Name")
        os.makedirs(album_dir, exist_ok=True)
        
        test_cases = [
            (181, "Should truncate 181 → 180 (remove 1 char net)"),
            (185, "Should truncate 185 → 180 (remove 5 chars net)"),
            (200, "Should truncate 200 → 180 (remove 20 chars net)"),
        ]
        
        for target_len, description in test_cases:
            print(f"{'='*70}")
            print(f"Test: {description}")
            print()
            
            # Create filename to reach target length
            prefix = "01. "
            suffix = ".flac"
            # Calculate how many chars we need in the filename
            album_dir_relative = album_dir[root_len:]  # Relative path to album dir
            available_for_filename = target_len - len(album_dir_relative) - 1  # -1 for /
            filename_len = available_for_filename
            padding_needed = filename_len - len(prefix) - len(suffix)
            
            filename = prefix + "A" * padding_needed + suffix
            filepath = os.path.join(album_dir, filename)
            relative_path = filepath[root_len:]
            
            # Create the file
            with open(filepath, 'w') as f:
                f.write("test")
            
            print(f"Original filename: {filename[:50]}...")
            print(f"Original relative path length: {len(relative_path)}")
            assert len(relative_path) == target_len, f"Setup error: expected {target_len}, got {len(relative_path)}"
            print()
            
            # Simulate truncation logic (NEW FIX: target = 180)
            target_relative_len = 180
            current_relative_len = len(filepath) - root_len
            excess = current_relative_len - target_relative_len
            
            print(f"Truncation calculation:")
            print(f"  Current relative len: {current_relative_len}")
            print(f"  Target: {target_relative_len}")
            print(f"  Excess: {excess}")
            print()
            
            # Get components
            dir_part = os.path.dirname(filepath)
            file_basename = os.path.basename(filepath)
            filename_no_ext, ext = os.path.splitext(file_basename)
            
            # Truncate
            truncate_by = excess + 2  # +2 for ".."
            truncated_filename = filename_no_ext[:len(filename_no_ext) - truncate_by]
            new_filename = truncated_filename + ".." + ext
            newpath = os.path.join(dir_part, new_filename)
            new_relative = newpath[root_len:]
            
            print(f"After truncation:")
            print(f"  Truncate filename by: {truncate_by}")
            print(f"  New filename: {new_filename[:50]}...")
            print(f"  New relative path length: {len(new_relative)}")
            
            if len(new_relative) == 180:
                print(f"  ✓ SUCCESS: Exactly 180 chars!")
            else:
                print(f"  ✗ FAIL: Expected 180, got {len(new_relative)}")
            print()
            
            # Clean up
            os.remove(filepath)

if __name__ == "__main__":
    test_truncation_to_180()
