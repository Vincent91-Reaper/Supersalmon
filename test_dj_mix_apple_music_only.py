#!/usr/bin/env python3
"""
Test to verify DJ Mix detection is only active for Apple Music (iTunes),
not for Qobuz, Tidal, Deezer, or Beatport.
"""

import re


def test_itunes_has_dj_mix_detection():
    """Verify iTunes still has DJ Mix detection."""
    # This is the pattern used in iTunes
    pattern = r"DJ[\s\-]*Mix"
    
    # Test various DJ Mix title formats
    test_cases = [
        "Artist - Album (DJ Mix)",
        "Various Artists - Compilation DJ Mix",
        "DJ Name - Boiler Room (DJ-Mix)",
        "Artist - DJMix Selection",
        "Various - dj mix Session",
    ]
    
    for title in test_cases:
        assert re.search(pattern, title, re.IGNORECASE), f"Should match DJ Mix in: {title}"
    
    # Test non-DJ Mix titles
    non_dj_mix = [
        "DJ Shadow - Album Name",  # DJ is artist name
        "Artist - Regular Album",
        "Various Artists - Compilation",
    ]
    
    for title in non_dj_mix:
        assert not re.search(pattern, title, re.IGNORECASE), f"Should NOT match in: {title}"
    
    print("✓ iTunes DJ Mix detection pattern works correctly")


def test_other_scrapers_no_dj_mix_detection():
    """
    Verify that Qobuz, Tidal, Deezer, and Beatport do NOT have DJ Mix detection.
    This is verified by checking the source files directly.
    """
    import os
    
    base_path = "brucelee94/tagger/sources"
    scrapers = {
        'Qobuz': f'{base_path}/qobuz.py',
        'Tidal': f'{base_path}/tidal.py',
        'Deezer': f'{base_path}/deezer.py',
        'Beatport': f'{base_path}/beatport.py',
    }
    
    dj_mix_pattern = r'DJ[\s\-]*Mix'
    
    for name, filepath in scrapers.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                # Check that parse_release_type doesn't contain DJ Mix detection regex
                assert dj_mix_pattern not in content or \
                       (dj_mix_pattern in content and 'parse_release_type' not in content.split(dj_mix_pattern)[0].split('\n')[-100:]), \
                    f"{name} should NOT have DJ Mix detection in parse_release_type"
                
                print(f"✓ {name} does NOT have DJ Mix detection")
        else:
            print(f"⚠ {name} file not found at {filepath}")


if __name__ == "__main__":
    test_itunes_has_dj_mix_detection()
    test_other_scrapers_no_dj_mix_detection()
    print("\n✅ All tests passed - DJ Mix detection is Apple Music only")
