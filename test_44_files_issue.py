#!/usr/bin/env python3
"""Test to reproduce the issue where all 44 files are truncated instead of just 8"""

import os
import tempfile

def test_selective_truncation():
    """Simulate the scenario from the user's gist"""
    
    # Create test scenario similar to user's issue
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Test directory: {tmpdir}\n")
        
        # Create album directory
        album_dir = os.path.join(tmpdir, "Artist - Album Name")
        os.makedirs(album_dir)
        
        # Calculate root_len (simulating line 108)
        root_len = len(tmpdir) + 1
        print(f"root_len = {root_len}\n")
        
        # Create 44 test files
        # 36 files under 180 chars (should NOT be truncated)
        # 8 files over 180 chars (SHOULD be truncated)
        
        files_created = []
        offending_files = []
        
        # Create 36 short files (under 180 chars relative)
        for i in range(1, 37):
            filename = f"{i:02d}. Short Track Name.flac"
            filepath = os.path.join(album_dir, filename)
            with open(filepath, 'w') as f:
                f.write("test")
            
            abs_path = os.path.abspath(filepath)
            rel_len = len(abs_path) - root_len
            files_created.append((abs_path, rel_len, False))  # False = should not truncate
            
            # Simulate line 115 condition
            if rel_len > 180:
                offending_files.append(abs_path)
                print(f"ERROR: Short file {i} added to offending_files! Rel len: {rel_len}")
        
        # Create 8 long files (over 180 chars relative)
        for i in range(37, 45):
            # Make filename long enough to exceed 180 total
            # We need: total_len > 180 + root_len
            # total_len = dir_len + filename_len
            # So: filename_len > 180 + root_len - dir_len
            
            dir_path_len = len(os.path.abspath(album_dir)) + 1  # +1 for separator
            needed_filename_len = 180 + root_len - dir_path_len + 10  # +10 to be well over
            
            long_name = "X" * (needed_filename_len - 5)  # -5 for ".flac"
            filename = f"{i:02d}. {long_name}.flac"
            filepath = os.path.join(album_dir, filename)
            with open(filepath, 'w') as f:
                f.write("test")
            
            abs_path = os.path.abspath(filepath)
            rel_len = len(abs_path) - root_len
            files_created.append((abs_path, rel_len, True))  # True = should truncate
            
            # Simulate line 115 condition
            if rel_len > 180:
                offending_files.append(abs_path)
        
        # Report results
        print(f"Total files created: {len(files_created)}")
        print(f"Files in offending_files: {len(offending_files)}")
        print(f"Expected in offending_files: 8\n")
        
        # Check each file
        should_truncate_count = sum(1 for _, _, should_trunc in files_created if should_trunc)
        print(f"Files that SHOULD be truncated: {should_truncate_count}")
        
        short_files_in_offending = []
        for path, rel_len, should_trunc in files_created:
            if rel_len > 180 and not should_trunc:
                short_files_in_offending.append((path, rel_len))
        
        if short_files_in_offending:
            print(f"\nERROR: {len(short_files_in_offending)} short files incorrectly added to offending_files:")
            for path, rel_len in short_files_in_offending:
                print(f"  - {os.path.basename(path)} (rel_len: {rel_len})")
        else:
            print("\n✓ Condition is working correctly!")
            print(f"  - {len(offending_files)} files in offending_files")
            print(f"  - All are correctly identified as > 180 chars")

if __name__ == "__main__":
    test_selective_truncation()
