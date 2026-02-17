"""
Test DJ Mix detection across all scrapers.
Tests that all scrapers correctly detect DJ Mix from release title.
"""
import re


def test_dj_mix_pattern():
    """Test the DJ Mix regex pattern matches various formats."""
    pattern = r"DJ[\s\-]*Mix"
    
    # Should match
    assert re.search(pattern, "Various Artists - DJ Mix Compilation", re.IGNORECASE)
    assert re.search(pattern, "DJ Dubfire - Boiler Room (DJ Mix)", re.IGNORECASE)
    assert re.search(pattern, "Various - Live DJ-Mix from Berlin", re.IGNORECASE)
    assert re.search(pattern, "Artist - Album (DJMix)", re.IGNORECASE)
    assert re.search(pattern, "Artist - dj mix", re.IGNORECASE)
    
    # Should not match
    assert not re.search(pattern, "Artist Name - Regular Album", re.IGNORECASE)
    assert not re.search(pattern, "DJ Shadow - Endtroducing", re.IGNORECASE)
    assert not re.search(pattern, "Mixer Selection", re.IGNORECASE)


def test_itunes_dj_mix_detection():
    """Test iTunes DJ Mix detection in parse_release_type."""
    from brucelee94.tagger.sources.itunes import Scraper
    
    scraper = Scraper()
    
    # Create mock soup with DJ Mix in title
    class MockSoup:
        def find(self, *args, **kwargs):
            class MockMeta:
                def __getitem__(self, key):
                    return "Various Artists - Boiler Room (DJ Mix)"
            return MockMeta()
    
    result = scraper.parse_release_type(MockSoup())
    assert result == "DJ Mix", f"Expected 'DJ Mix', got '{result}'"
    
    # Create mock soup without DJ Mix
    class MockSoup2:
        def find(self, *args, **kwargs):
            class MockMeta:
                def __getitem__(self, key):
                    return "Artist Name - Regular Album"
            return MockMeta()
    
    result = scraper.parse_release_type(MockSoup2())
    assert result != "DJ Mix", f"Expected not 'DJ Mix', got '{result}'"


def test_qobuz_dj_mix_detection():
    """Test Qobuz DJ Mix detection in parse_release_type."""
    from brucelee94.tagger.sources.qobuz import Scraper
    
    scraper = Scraper()
    
    # Test with DJ Mix in title
    soup = {"title": "Various Artists - Boiler Room (DJ Mix)", "tracks_count": 20}
    result = scraper.parse_release_type(soup)
    assert result == "DJ Mix", f"Expected 'DJ Mix', got '{result}'"
    
    # Test without DJ Mix
    soup = {"title": "Artist Name - Regular Album", "tracks_count": 10}
    result = scraper.parse_release_type(soup)
    assert result != "DJ Mix", f"Expected not 'DJ Mix', got '{result}'"


def test_tidal_dj_mix_detection():
    """Test Tidal DJ Mix detection in parse_release_type."""
    from brucelee94.tagger.sources.tidal import Scraper
    
    scraper = Scraper()
    
    # Test with DJ Mix in title
    soup = {"title": "Various Artists - Boiler Room (DJ Mix)", "type": "ALBUM"}
    result = scraper.parse_release_type(soup)
    assert result == "DJ Mix", f"Expected 'DJ Mix', got '{result}'"
    
    # Test without DJ Mix
    soup = {"title": "Artist Name - Regular Album", "type": "ALBUM"}
    result = scraper.parse_release_type(soup)
    assert result == "Album", f"Expected 'Album', got '{result}'"


def test_deezer_dj_mix_detection():
    """Test Deezer DJ Mix detection in parse_release_type."""
    from brucelee94.tagger.sources.deezer import Scraper
    
    scraper = Scraper()
    
    # Test with DJ Mix in title
    soup = {"title": "Various Artists - Boiler Room (DJ Mix)", "record_type": "album"}
    result = scraper.parse_release_type(soup)
    assert result == "DJ Mix", f"Expected 'DJ Mix', got '{result}'"
    
    # Test without DJ Mix
    soup = {"title": "Artist Name - Regular Album", "record_type": "album"}
    result = scraper.parse_release_type(soup)
    assert result == "Album", f"Expected 'Album', got '{result}'"


def test_beatport_dj_mix_detection():
    """Test Beatport DJ Mix detection in parse_release_type."""
    from brucelee94.tagger.sources.beatport import Scraper
    
    scraper = Scraper()
    
    # Test with DJ Mix in title
    soup = {
        "state": {
            "data": {
                "results": [
                    {"release": {"name": "Various Artists - Boiler Room (DJ Mix)"}}
                ]
            }
        }
    }
    result = scraper.parse_release_type(soup)
    assert result == "DJ Mix", f"Expected 'DJ Mix', got '{result}'"
    
    # Test without DJ Mix
    soup = {
        "state": {
            "data": {
                "results": [
                    {"release": {"name": "Artist Name - Regular Release"}}
                ]
            }
        }
    }
    result = scraper.parse_release_type(soup)
    assert result == "EP", f"Expected 'EP', got '{result}'"


if __name__ == "__main__":
    print("Testing DJ Mix pattern...")
    test_dj_mix_pattern()
    print("✓ DJ Mix pattern tests passed")
    
    print("\nTesting iTunes DJ Mix detection...")
    test_itunes_dj_mix_detection()
    print("✓ iTunes DJ Mix detection tests passed")
    
    print("\nTesting Qobuz DJ Mix detection...")
    test_qobuz_dj_mix_detection()
    print("✓ Qobuz DJ Mix detection tests passed")
    
    print("\nTesting Tidal DJ Mix detection...")
    test_tidal_dj_mix_detection()
    print("✓ Tidal DJ Mix detection tests passed")
    
    print("\nTesting Deezer DJ Mix detection...")
    test_deezer_dj_mix_detection()
    print("✓ Deezer DJ Mix detection tests passed")
    
    print("\nTesting Beatport DJ Mix detection...")
    test_beatport_dj_mix_detection()
    print("✓ Beatport DJ Mix detection tests passed")
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED!")
    print("="*50)
