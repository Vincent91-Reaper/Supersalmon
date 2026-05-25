#!/usr/bin/env python3
"""Test to debug why ALL files are being truncated instead of just those > 180 chars"""

import os
import tempfile
import shutil

def test_path_length_calculation():
    """Test the path length calculation logic"""
    
    # Simulate the code from folderstructure.py
    download_directory = "/tmp/test_download"
    root_len = len(download_directory) + 1  # Line 108
    
    print(f"Download directory: '{download_directory}'")
    print(f"Download directory length: {len(download_directory)}")
    print(f"root_len = {root_len}\n")
    
    # Test case 1: File under 180 chars
    test_file_1 = "/tmp/test_download/Artist - Album/01. Track Name.flac"
    relative_len_1 = len(test_file_1) - root_len
    
    print(f"Test 1: File under 180 chars")
    print(f"  Absolute path: '{test_file_1}'")
    print(f"  Absolute path length: {len(test_file_1)}")
    print(f"  Relative path length: {relative_len_1}")
    print(f"  Should be truncated? {relative_len_1 > 180}")
    print()
    
    # Test case 2: File over 180 chars
    long_name = "A" * 160
    test_file_2 = f"/tmp/test_download/Artist - Album/{long_name}.flac"
    relative_len_2 = len(test_file_2) - root_len
    
    print(f"Test 2: File over 180 chars")
    print(f"  Absolute path length: {len(test_file_2)}")
    print(f"  Relative path length: {relative_len_2}")
    print(f"  Should be truncated? {relative_len_2 > 180}")
    print()
    
    # Test case 3: Exactly at 180 chars
    # We need: relative_len = 180
    # relative_len = total_len - root_len
    # 180 = total_len - root_len
    # total_len = 180 + root_len = 180 + 20 = 200
    target_total = 180 + root_len
    padding_needed = target_total - len("/tmp/test_download/Artist - Album/") - len(".flac")
    filename_3 = "B" * padding_needed
    test_file_3 = f"/tmp/test_download/Artist - Album/{filename_3}.flac"
    relative_len_3 = len(test_file_3) - root_len
    
    print(f"Test 3: File exactly at 180 chars")
    print(f"  Absolute path length: {len(test_file_3)}")
    print(f"  Relative path length: {relative_len_3}")
    print(f"  Should be truncated? {relative_len_3 > 180}")
    print()
    
    # Now let's test with actual file operations
    print("="*60)
    print("Testing with actual file creation...")
    print("="*60)
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\nTemp directory: {tmpdir}")
        
        # Create subdirectory
        album_dir = os.path.join(tmpdir, "Artist - Album")
        os.makedirs(album_dir)
        
        # Calculate root_len for this temp dir
        actual_root_len = len(tmpdir) + 1
        print(f"Actual root_len: {actual_root_len}\n")
        
        # Create a file under 180 chars
        short_file = os.path.join(album_dir, "01. Short Name.flac")
        with open(short_file, 'w') as f:
            f.write("test")
        
        abs_path_short = os.path.abspath(short_file)
        rel_len_short = len(abs_path_short) - actual_root_len
        
        print(f"Short file created:")
        print(f"  Path: {abs_path_short}")
        print(f"  Total length: {len(abs_path_short)}")
        print(f"  Relative length: {rel_len_short}")
        print(f"  Would be truncated? {rel_len_short > 180}")
        print()
        
        # Create a file over 180 chars
        # Need: relative_len > 180
        # relative_len = total_len - actual_root_len
        # 181 = total_len - actual_root_len
        # total_len = 181 + actual_root_len
        
        dir_prefix = os.path.join(album_dir, "")
        dir_len = len(os.path.abspath(dir_prefix))
        ext = ".flac"
        
        # We want: total_len = 181 + actual_root_len
        # total_len = dir_len + len(filename) + len(ext)
        # 181 + actual_root_len = dir_len + len(filename) + len(ext)
        # len(filename) = 181 + actual_root_len - dir_len - len(ext)
        
        filename_len_needed = 181 + actual_root_len - dir_len - len(ext)
        long_filename = "C" * filename_len_needed
        long_file = os.path.join(album_dir, long_filename + ext)
        
        with open(long_file, 'w') as f:
            f.write("test")
        
        abs_path_long = os.path.abspath(long_file)
        rel_len_long = len(abs_path_long) - actual_root_len
        
        print(f"Long file created:")
        print(f"  Path: {abs_path_long}")
        print(f"  Total length: {len(abs_path_long)}")
        print(f"  Relative length: {rel_len_long}")
        print(f"  Would be truncated? {rel_len_long > 180}")

if __name__ == "__main__":
    test_path_length_calculation()
