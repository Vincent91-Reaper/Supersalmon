import re
from collections import defaultdict
from html import unescape

from brucelee94.common import RE_FEAT, parse_copyright, re_split
from brucelee94.errors import ScrapeError
from brucelee94.sources import TidalBase
from brucelee94.tagger.sources.base import MetadataMixin

ROLES = {
    "MAIN": "main",
    "FEATURED": "guest",
}

RECORD_TYPES = {
    "ALBUM": "Album",
    "EP": "EP",
    "SINGLE": "Single",
}
DEFAULT_DISC_NUMBER = 1
DEFAULT_TRACK_NUMBER = 1


class Scraper(TidalBase, MetadataMixin):
    regex = re.compile(r"^https?://.*(?:tidal|wimpmusic)\.com.*\/(album)\/([0-9]+)")

    def parse_release_title(self, soup):
        return RE_FEAT.sub("", soup["title"])

    def parse_cover_url(self, soup):
        if not soup["cover"]:
            return None
        return self.image_url.format(album_id=soup["cover"].replace("-", "/"))

    def parse_release_year(self, soup):
        try:
            return int(re.search(r"(\d{4})", soup["releaseDate"])[1])
        except TypeError:
            return None

    def parse_release_date(self, soup):
        date = soup["releaseDate"]
        if not date or date.endswith("01-01") and int(date[:4]) < 2013:
            return None
        return date

    def parse_release_type(self, soup):
        if re.search(r"DJ[\s\-]*Mix", soup.get("title", ""), re.IGNORECASE):
            return "DJ Mix"
        # Try to get from Tidal's type mapping
        try:
            return RECORD_TYPES[soup["type"]]
        except KeyError:
            return None

    def parse_release_label(self, soup):
        return parse_copyright(soup.get("copyright", ""))

    def parse_genres(self, soup):
        genres = set()
        for key in ("genre", "genres"):
            value = soup.get(key)
            if isinstance(value, str):
                genres.add(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        genres.add(item)
                    elif isinstance(item, dict) and item.get("name"):
                        genres.add(item["name"])
        return genres

    def parse_upc(self, soup):
        return soup["upc"]

    def parse_tracks(self, soup):
        tracks = defaultdict(dict)
        for track in soup["tracklist"]:
            parsed_artists = self.parse_artists(track.get("artists", []), track.get("title", ""), track.get("id"))
            discno = track.get("volumeNumber") or track.get("volume") or DEFAULT_DISC_NUMBER
            trackno = track.get("trackNumber") or track.get("number") or DEFAULT_TRACK_NUMBER

            tracks[str(discno)][str(trackno)] = self.generate_track(
                trackno=trackno,
                discno=discno,
                artists=parsed_artists,
                title=self.parse_title(track.get("title", ""), track.get("version")),
                replay_gain=track.get("replayGain"),
                peak=track.get("peak"),
                isrc=track.get("isrc"),
                explicit=track.get("explicit"),
                format_=track.get("audioQuality"),
                stream_id=track.get("id"),
                streamable=track.get("allowStreaming", True),
            )
        return dict(tracks)

    def process_label(self, data):
        if isinstance(data["label"], str) and any(
            data["label"].lower().startswith(a.lower()) and i == "main" for a, i in data["artists"]
        ):
            return "Self-Released"
        return data["label"]

    def parse_artists(self, artists, title, track_id):  # noqa: C901
        """
        Iterate over all artists and roles, returning a compliant list of
        artist tuples.
        """
        result = []
        artist_set = set()

        feat = RE_FEAT.search(title)
        if feat:
            for artist in re_split(feat[1]):
                result.append((unescape(artist), "guest"))
                artist_set.add(unescape(artist).lower())

        remix_str = ""
        remixer_str = re.search(r" \((.*) [Rr]emix\)", title)
        if remixer_str:
            remix_str = unescape(remixer_str[1]).lower()

        all_guests = all(a.get("type", "MAIN") == "FEATURED" for a in artists)
        for artist in artists:
            artist_without_feat = artist.get("name", "")
            feat = RE_FEAT.search(artist_without_feat)
            if feat:
                for artist_ in re_split(feat[1]):
                    result.append((unescape(artist_), "guest"))
                    artist_set.add(unescape(artist_).lower())
                artist_without_feat = re.sub(re.escape(feat[0]) + "$", "", artist_without_feat).rstrip()
            for a in re_split(artist_without_feat):
                artist_type = artist.get("type", "MAIN")
                if artist_type in ROLES and unescape(a).lower() not in artist_set:
                    if unescape(a).lower() in remix_str:
                        result.append((unescape(a), "remixer"))
                    elif all_guests:
                        result.append((unescape(a), "main"))
                    else:
                        result.append((unescape(a), ROLES[artist_type]))
                    artist_set.add(unescape(a).lower())

        if "mix" in title.lower():  # Get contributors for (re)mixes.
            attempts = 0
            while True:
                try:
                    artists = self.get_json_sync(
                        f"/tracks/{track_id}/contributors",
                        params={"countryCode": self.country_code, "limit": 25},
                    )["items"]
                    break
                except ScrapeError:
                    attempts += 1
                    if attempts > 3:
                        break
            for artist in artists:
                if artist["role"] == "Remixer" and artist["name"].lower() not in artist_set:
                    result.append((unescape(artist["name"]), "remixer"))
                    artist_set.add(artist["name"].lower())

        # In case something is fucked, have a failsafe of returning all artists.
        return result if result else [(unescape(a["name"]), "main") for a in artists if a.get("name")]
