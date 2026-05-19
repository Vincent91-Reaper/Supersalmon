from brucelee94 import cfg
from brucelee94.errors import ScrapeError
from brucelee94.search.base import IdentData, SearchMixin
from brucelee94.sources import BeatportBase


class Searcher(BeatportBase, SearchMixin):
    async def search_releases(self, searchstr, limit):
        releases = {}
        response = await self.api_get(
            self.api_search_url,
            params={"q": searchstr, "type": "releases", "per_page": max(limit, 25)},
        )
        try:
            search_results = response["releases"]
            for result in search_results:
                rls_id = result["id"]
                main_artists = [artist["name"] for artist in result.get("artists") or [] if artist.get("name")]
                title = result["name"]
                artists = (
                    ", ".join(main_artists) if len(main_artists) < 4 else cfg.upload.formatting.various_artist_word
                )
                label = (result.get("label") or {}).get("name") or ""

                if label.lower() not in cfg.upload.search.excluded_labels:
                    releases[rls_id] = (
                        IdentData(artists, title, None, result.get("track_count"), "WEB"),
                        self.format_result(artists, title, label),
                    )

                if len(releases) == limit:
                    break

        except (KeyError, TypeError) as e:
            raise ScrapeError("Failed to parse Beatport API search results") from e

        return "Beatport", releases
