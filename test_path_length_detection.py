#!/usr/bin/env python3
"""Test to understand path length detection issue."""

import os

def test_path_calculations():
    """Test path length calculations with different scenarios."""
    
    # Simulate different download_directory formats
    scenarios = [
        ("/home/user/downloads", "No trailing slash"),
        ("/home/user/downloads/", "With trailing slash"),
    ]
    
    for download_dir, desc in scenarios:
        print(f"\n{'='*60}")
        print(f"Scenario: {desc}")
        print(f"Download directory: '{download_dir}'")
        
        # Current calculation
        root_len = len(download_dir) + 1
        print(f"root_len (current calc): {root_len}")
        
        # Test file paths
        test_files = [
            "Album/01. Track.flac",  # 21 chars relative
            "A" * 180 + ".flac",  # Exactly 180 chars relative (filename only)
            "Album/" + "A" * 175 + ".flac",  # 181 chars relative
        ]
        
        for rel_path in test_files:
            if download_dir.endswith('/'):
                filepath = download_dir + rel_path
            else:
                filepath = download_dir + '/' + rel_path
            
            print(f"\n  Relative path: {rel_path[:50]}{'...' if len(rel_path) > 50 else ''}")
            print(f"  Relative path length: {len(rel_path)}")
            print(f"  Full path: {filepath[:60]}{'...' if len(filepath) > 60 else ''}")
            print(f"  Full path length: {len(filepath)}")
            
            # Current calculation (what the code does)
            calc_relative_len = len(filepath) - root_len
            print(f"  Calculated relative len (current): {calc_relative_len}")
            print(f"  Would truncate? {calc_relative_len > 180}")
            
            # What it SHOULD be
            if download_dir.endswith('/'):
                correct_relative = filepath[len(download_dir):]
            else:
                correct_relative = filepath[len(download_dir) + 1:]
            
            print(f"  Correct relative path: {correct_relative[:50]}{'...' if len(correct_relative) > 50 else ''}")
            print(f"  Correct relative len: {len(correct_relative)}")
            print(f"  SHOULD truncate? {len(correct_relative) > 180}")
            
            if calc_relative_len != len(correct_relative):
                print(f"  ⚠️  ERROR: Calculation mismatch! {calc_relative_len} vs {len(correct_relative)}")

if __name__ == "__main__":
    test_path_calculations()
