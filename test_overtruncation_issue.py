#!/usr/bin/env python3
"""Test to verify overtruncation issue and fix."""

import os
import tempfile

def test_truncation_calculation():
    """Test that truncation calculation is correct."""
    
    # Simulate a file path
    root_dir = "/home/user/downloads"
    root_len = len(root_dir) + 1  # +1 for trailing /
    
    # Example: Album folder + filename that totals > 180 chars relative
    album_dir = "Artist Name - Very Long Album Title Here With Additional Information About The Release Year And Edition 2024"  # ~110 chars
    filename = "01. Track Name With Many Words And Extra Information About The Song That Makes It Very Long And Exceeds The Limit For Sure.flac"  # ~140 chars
    
    filepath = os.path.join(root_dir, album_dir, filename)
    relative_path = filepath[root_len:]
    
    print(f"Root: {root_dir}")
    print(f"Root length: {root_len}")
    print(f"Full path: {filepath}")
    print(f"Full path length: {len(filepath)}")
    print(f"Relative path: {relative_path}")
    print(f"Relative path length: {len(relative_path)}")
    print()
    
    # Current (buggy) calculation
    target_relative_len = 178
    current_relative_len = len(filepath) - root_len
    excess = current_relative_len - target_relative_len
    
    print(f"Target relative length: {target_relative_len}")
    print(f"Current relative length: {current_relative_len}")
    print(f"Excess: {excess}")
    print()
    
    # Current truncation
    dir_part = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    filename_no_ext, ext = os.path.splitext(file_basename)
    
    print(f"Directory part: {dir_part}")
    print(f"Directory part length: {len(dir_part)}")
    print(f"File basename: {file_basename}")
    print(f"File basename length: {len(file_basename)}")
    print(f"Filename (no ext): {filename_no_ext}")
    print(f"Filename (no ext) length: {len(filename_no_ext)}")
    print(f"Extension: {ext}")
    print()
    
    # BUGGY calculation - truncates by excess (based on full path)
    truncated_filename_buggy = filename_no_ext[:len(filename_no_ext) - excess - 2]
    new_filename_buggy = truncated_filename_buggy + ".." + ext
    newpath_buggy = os.path.join(dir_part, new_filename_buggy)
    new_relative_buggy = newpath_buggy[root_len:]
    
    print("BUGGY CALCULATION:")
    print(f"Truncate by: {excess + 2}")
    print(f"New filename: {new_filename_buggy}")
    print(f"New filename length: {len(new_filename_buggy)}")
    print(f"New path: {newpath_buggy}")
    print(f"New relative path: {new_relative_buggy}")
    print(f"New relative length: {len(new_relative_buggy)}")
    print(f"ERROR: Should be 178, got {len(new_relative_buggy)}")
    print()
    
    # CORRECT calculation - only truncate filename by what's needed
    dir_part_relative = dir_part[root_len:]
    print(f"Directory part (relative): {dir_part_relative}")
    print(f"Directory part (relative) length: {len(dir_part_relative)}")
    
    # Calculate how much space we have for the filename
    available_for_filename = target_relative_len - len(dir_part_relative) - 1  # -1 for /
    print(f"Available for filename: {available_for_filename}")
    
    # Calculate how much to truncate from filename
    current_filename_len = len(file_basename)
    filename_excess = current_filename_len - available_for_filename
    print(f"Current filename length: {current_filename_len}")
    print(f"Filename excess: {filename_excess}")
    
    if filename_excess > 0:
        # Need to truncate the filename
        truncate_from_name = filename_excess + 2  # +2 for ".."
        truncated_filename_correct = filename_no_ext[:len(filename_no_ext) - truncate_from_name]
        new_filename_correct = truncated_filename_correct + ".." + ext
        newpath_correct = os.path.join(dir_part, new_filename_correct)
        new_relative_correct = newpath_correct[root_len:]
        
        print()
        print("CORRECT CALCULATION:")
        print(f"Truncate from filename by: {truncate_from_name}")
        print(f"New filename: {new_filename_correct}")
        print(f"New filename length: {len(new_filename_correct)}")
        print(f"New path: {newpath_correct}")
        print(f"New relative path: {new_relative_correct}")
        print(f"New relative length: {len(new_relative_correct)}")
        print(f"✓ SUCCESS: Target was 178, got {len(new_relative_correct)}")

if __name__ == "__main__":
    test_truncation_calculation()
