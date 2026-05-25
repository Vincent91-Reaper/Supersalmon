#!/usr/bin/env python3
"""
Test for user's specific issue with long folder name.

Folder: Dylan & Harry, Party Favor & Baauer - Brownies & Lemonade_ Dylan & Harry (Party Favor & Baauer) in Los Angeles, Apr 19, 2023 [DJ Mix] (2023) [WEB FLAC] [16-44.1]

This folder name is approximately 160 characters long.
With typical filenames of 30-40 characters, the relative paths exceed 180 chars.
"""

import os
import tempfile
import shutil

def test_user_long_folder_scenario():
    """Test the exact scenario from user's issue."""
    
    # User's actual folder name (160 chars)
    folder_name = "Dylan & Harry, Party Favor & Baauer - Brownies & Lemonade_ Dylan & Harry (Party Favor & Baauer) in Los Angeles, Apr 19, 2023 [DJ Mix] (2023) [WEB FLAC] [16-44.1]"
    
    print(f"Folder name: {folder_name}")
    print(f"Folder name length: {len(folder_name)}")
    print()
    
    # Create test directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create the folder
        folder_path = os.path.join(tmpdir, folder_name)
        os.makedirs(folder_path)
        
        # Create some test files with typical DJ Mix track names
        test_files = [
            "01. Intro (Mixed).flac",  # 22 chars
            "02. Track Name Here (Mixed).flac",  # 33 chars
            "35. Thinkin of You (Mixed).flac",  # 32 chars
        ]
        
        for filename in test_files:
            filepath = os.path.join(folder_path, filename)
            # Create empty file
            with open(filepath, 'w') as f:
                f.write('')
            
            # Calculate relative path
            relative_path = folder_name + "/" + filename
            rel_len = len(relative_path)
            
            print(f"File: {filename}")
            print(f"  Filename length: {len(filename)}")
            print(f"  Relative path: {relative_path}")
            print(f"  Relative path length: {rel_len}")
            print(f"  Exceeds 180? {rel_len > 180}")
            print()
        
        # Show what truncation would be needed
        for filename in test_files:
            relative_path = folder_name + "/" + filename
            rel_len = len(relative_path)
            
            if rel_len > 180:
                excess = rel_len - 180
                print(f"File: {filename}")
                print(f"  Current relative path: {rel_len} chars")
                print(f"  Excess: {excess} chars")
                print(f"  Need to truncate filename by: {excess + 2} chars (including '..')")
                
                # Check if truncation is possible
                name_no_ext = os.path.splitext(filename)[0]
                if len(name_no_ext) < excess + 2:
                    print(f"  ERROR: Filename too short to truncate!")
                else:
                    truncated = name_no_ext[:len(name_no_ext) - excess - 2]
                    ext = os.path.splitext(filename)[1]
                    new_name = truncated + ".." + ext
                    new_relative = folder_name + "/" + new_name
                    print(f"  Truncated filename: {new_name}")
                    print(f"  New relative path length: {len(new_relative)}")
                print()

if __name__ == "__main__":
    test_user_long_folder_scenario()
