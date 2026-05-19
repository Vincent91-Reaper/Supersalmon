import asyncio
import importlib.util
import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).parent


def load_module(monkeypatch, name, path, stubs):
    for module_name, module in stubs.items():
        monkeypatch.setitem(sys.modules, module_name, module)
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def test_tidal_album_items_preserve_track_artists(monkeypatch):
    class ScrapeError(Exception):
        pass

    class BaseScraper:
        def __init__(self):
            pass

    cfg = types.SimpleNamespace(
        metadata=types.SimpleNamespace(tidal=types.SimpleNamespace(token=None, fetch_regions=[]))
    )
    brucelee94 = types.ModuleType("brucelee94")
    brucelee94.cfg = cfg
    errors = types.ModuleType("brucelee94.errors")
    errors.ScrapeError = ScrapeError
    base = types.ModuleType("brucelee94.sources.base")
    base.BaseScraper = BaseScraper

    tidal = load_module(
        monkeypatch,
        "tidal_regression",
        "brucelee94/sources/tidal.py",
        {
            "brucelee94": brucelee94,
            "brucelee94.errors": errors,
            "brucelee94.sources.base": base,
        },
    )
    monkeypatch.setattr(tidal, "get_tidal_regions_to_fetch", lambda: ["US"])
    requested_paths = []

    class Scraper(tidal.TidalBase):
        def _headers(self):
            return {}

        async def get_json(self, url, params=None, headers=None):
            requested_paths.append(url)
            if url.endswith("/items"):
                return {
                    "items": [
                        {
                            "item": {
                                "id": 1,
                                "title": "Freshie",
                                "artists": [{"name": "Fasina", "type": "MAIN"}],
                            }
                        }
                    ]
                }
            return {"title": "FRESHIE"}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(Scraper().create_soup("https://tidal.com/album/326457263"))

    assert requested_paths == ["/albums/326457263", "/albums/326457263/items"]
    assert data["tracklist"][0]["artists"] == [{"name": "Fasina", "type": "MAIN"}]


def test_tidal_album_tracks_fallback_when_items_have_no_artists(monkeypatch):
    class ScrapeError(Exception):
        pass

    class BaseScraper:
        def __init__(self):
            pass

    cfg = types.SimpleNamespace(
        metadata=types.SimpleNamespace(tidal=types.SimpleNamespace(token=None, fetch_regions=[]))
    )
    brucelee94 = types.ModuleType("brucelee94")
    brucelee94.cfg = cfg
    errors = types.ModuleType("brucelee94.errors")
    errors.ScrapeError = ScrapeError
    base = types.ModuleType("brucelee94.sources.base")
    base.BaseScraper = BaseScraper

    tidal = load_module(
        monkeypatch,
        "tidal_tracks_fallback_regression",
        "brucelee94/sources/tidal.py",
        {
            "brucelee94": brucelee94,
            "brucelee94.errors": errors,
            "brucelee94.sources.base": base,
        },
    )
    monkeypatch.setattr(tidal, "get_tidal_regions_to_fetch", lambda: ["US"])
    requested_paths = []

    class Scraper(tidal.TidalBase):
        def _headers(self):
            return {}

        async def get_json(self, url, params=None, headers=None):
            requested_paths.append(url)
            if url.endswith("/items"):
                return {"items": [{"item": {"id": 1, "title": "Track Without Artists"}}]}
            if url.endswith("/tracks"):
                return {
                    "items": [
                        {
                            "id": 1,
                            "title": "Track With Artists",
                            "artists": [{"name": "Tems", "type": "MAIN"}],
                        }
                    ]
                }
            return {"title": "Love Is A Kingdom", "artists": [{"name": "Tems", "type": "MAIN"}]}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(Scraper().create_soup("https://tidal.com/album/474707708"))

    assert requested_paths == [
        "/albums/474707708",
        "/albums/474707708/items",
        "/albums/474707708/tracks",
    ]
    assert data["tracklist"][0]["title"] == "Track With Artists"
    assert data["tracklist"][0]["artists"] == [{"name": "Tems", "type": "MAIN"}]


def test_tidal_album_artist_fills_missing_track_artists(monkeypatch):
    class ScrapeError(Exception):
        pass

    class BaseScraper:
        def __init__(self):
            pass

    cfg = types.SimpleNamespace(
        metadata=types.SimpleNamespace(tidal=types.SimpleNamespace(token=None, fetch_regions=[]))
    )
    brucelee94 = types.ModuleType("brucelee94")
    brucelee94.cfg = cfg
    errors = types.ModuleType("brucelee94.errors")
    errors.ScrapeError = ScrapeError
    base = types.ModuleType("brucelee94.sources.base")
    base.BaseScraper = BaseScraper

    tidal = load_module(
        monkeypatch,
        "tidal_album_artist_fallback_regression",
        "brucelee94/sources/tidal.py",
        {
            "brucelee94": brucelee94,
            "brucelee94.errors": errors,
            "brucelee94.sources.base": base,
        },
    )
    monkeypatch.setattr(tidal, "get_tidal_regions_to_fetch", lambda: ["US"])

    class Scraper(tidal.TidalBase):
        def _headers(self):
            return {}

        async def get_json(self, url, params=None, headers=None):
            if url.endswith("/items"):
                return {"items": [{"item": {"id": 1, "title": "First"}}]}
            if url.endswith("/tracks"):
                return {"items": []}
            return {"title": "Love Is A Kingdom", "artists": [{"name": "Tems", "type": "MAIN"}]}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(Scraper().create_soup("https://tidal.com/album/474707708"))

    assert data["tracklist"][0]["artists"] == [{"name": "Tems", "type": "MAIN"}]


def test_deezer_label_text_accepts_tuple_values(monkeypatch):
    common = types.ModuleType("brucelee94.common")
    common.RE_FEAT = re.compile(r"$^")
    common.parse_copyright = lambda value: value
    common.re_split = lambda value: [value]
    sources = types.ModuleType("brucelee94.sources")
    sources.DeezerBase = type("DeezerBase", (), {})
    tagger_base = types.ModuleType("brucelee94.tagger.sources.base")
    tagger_base.MetadataMixin = type("MetadataMixin", (), {})

    deezer = load_module(
        monkeypatch,
        "deezer_regression",
        "brucelee94/tagger/sources/deezer.py",
        {
            "brucelee94.common": common,
            "brucelee94.sources": sources,
            "brucelee94.tagger.sources.base": tagger_base,
        },
    )

    assert deezer.Scraper().parse_release_label({"label": ("Test Label",)}) == "Test Label"
    assert deezer.Scraper().process_label({"label": ({"name": "Test Label"},), "artists": []}) == "Test Label"


def test_itunes_amp_dict_has_no_html_comment(monkeypatch):
    common = types.ModuleType("brucelee94.common")
    common.RE_FEAT = re.compile(r"$^")
    common.parse_copyright = lambda value: value
    sources = types.ModuleType("brucelee94.sources")
    sources.iTunesBase = type("iTunesBase", (), {})
    tagger_base = types.ModuleType("brucelee94.tagger.sources.base")
    tagger_base.MetadataMixin = type("MetadataMixin", (), {})
    errors = types.ModuleType("brucelee94.errors")
    errors.ScrapeError = type("ScrapeError", (Exception,), {})

    itunes = load_module(
        monkeypatch,
        "itunes_regression",
        "brucelee94/tagger/sources/itunes.py",
        {
            "brucelee94.common": common,
            "brucelee94.errors": errors,
            "brucelee94.sources": sources,
            "brucelee94.tagger.sources.base": tagger_base,
        },
    )

    assert itunes.Scraper().parse_comment({"data": []}) is None
