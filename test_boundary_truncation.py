#!/usr/bin/env python3
"""Test to verify if files at boundary are being overtruncated."""

def test_boundary_truncation():
    """Test truncation at 178, 179, 180, 181 char boundaries."""
    
    download_dir = "/home/user/downloads"
    root_len = len(download_dir) + 1  # 21
    
    # Test files at different lengths
    test_cases = [
        (178, "Should NOT truncate - already at target"),
        (179, "Should NOT truncate - within limit"),
        (180, "Should NOT truncate - exactly at limit"),
        (181, "SHOULD truncate - exceeds limit"),
        (200, "SHOULD truncate - way over limit"),
    ]
    
    print("Testing truncation logic:\n")
    print(f"root_len = {root_len}")
    print(f"Limit: <= 180 chars relative")
    print(f"Target after truncation: 178 chars")
    print()
    
    for target_len, description in test_cases:
        # Create a relative path of exactly target_len chars
        # Format: "Album/01. " + padding + ".flac"
        prefix = "Album/01. "
        suffix = ".flac"
        padding_needed = target_len - len(prefix) - len(suffix)
        relative_path = prefix + "A" * padding_needed + suffix
        
        filepath = download_dir + "/" + relative_path
        
        print(f"{'='*70}")
        print(f"Relative length: {len(relative_path)} chars - {description}")
        print(f"Relative path: {relative_path[:60]}...")
        print()
        
        # Check if would be added to offending_files
        would_truncate = len(filepath) - root_len > 180
        print(f"  len(filepath) = {len(filepath)}")
        print(f"  len(filepath) - root_len = {len(filepath) - root_len}")
        print(f"  Condition: {len(filepath) - root_len} > 180 = {would_truncate}")
        print()
        
        if would_truncate:
            # Calculate truncation
            target_relative_len = 178
            current_relative_len = len(filepath) - root_len
            excess = current_relative_len - target_relative_len
            
            print(f"  Would truncate:")
            print(f"    Current relative len: {current_relative_len}")
            print(f"    Target: {target_relative_len}")
            print(f"    Excess: {excess}")
            print(f"    Would truncate filename by: {excess + 2}")
        else:
            print(f"  Would NOT truncate (path length {len(filepath) - root_len} <= 180)")
        print()

if __name__ == "__main__":
    test_boundary_truncation()
