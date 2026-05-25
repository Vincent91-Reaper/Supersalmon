from brucelee94.tagger.sources import METASOURCES


def test_complex_source_urls_are_trimmed_to_release_id():
    urls = {
        "Beatport": (
            "https://www.beatport.com/release/fun-2/6395199?utm_source=toneden&amp;utm_medium=bp_affiliate",
            "https://www.beatport.com/release/fun-2/6395199",
        ),
        "Qobuz": (
            "https://www.qobuz.com/us-en/album/fun-2/abc123?utm_source=request",
            "https://www.qobuz.com/us-en/album/fun-2/abc123",
        ),
        "Tidal": (
            "https://listen.tidal.com/album/123456789?u",
            "https://listen.tidal.com/album/123456789",
        ),
        "Deezer": (
            "https://www.deezer.com/us/album/987654321?utm_campaign=request",
            "https://www.deezer.com/us/album/987654321",
        ),
    }

    for source_name, (url, expected) in urls.items():
        assert METASOURCES[source_name].Scraper.regex.match(url)
        assert METASOURCES[source_name].Scraper.normalize_url(url) == expected
