import re
from collections import defaultdict
from html import unescape

from brucelee94.common import RE_FEAT, parse_copyright, re_split
from brucelee94.sources import DeezerBase
from brucelee94.tagger.sources.base import MetadataMixin

RECORD_TYPES = {
    "album": "Album",
    "ep": "EP",
    "single": "Single",
}


class Scraper(DeezerBase, MetadataMixin):
    def parse_release_title(self, soup):
        return RE_FEAT.sub("", soup["title"])

    def parse_cover_url(self, soup):
        cover_xl = soup["cover_xl"]
        # Enhance cover quality: Replace standard resolution with high-resolution version
        # Standard: 1000x1000-000000-80-0-0.jpg (80 quality)
        # High-res: 1400x1400-000000-100-0-0.jpg (100 quality, larger size)
        # Based on YADG userscript optimization
        if cover_xl and '1000x1000-000000-80-0-0.jpg' in cover_xl:
            return cover_xl.replace('1000x1000-000000-80-0-0.jpg', '1400x1400-000000-100-0-0.jpg')
        return cover_xl

    def parse_release_year(self, soup):
        try:
            return int(re.search(r"(\d{4})", soup["release_date"])[1])
        except TypeError:
            return None
            # raise ScrapeError('Could not parse release year.') from e

    def parse_release_date(self, soup):
        """
        Parse the release date from the API response.
        Formats the date to "Month Day, Year" format (e.g., "December 31, 2025").
        """
        try:
            raw_date = soup["release_date"]
            # Format date to "Month Day, Year" format (e.g., "December 31, 2025")
            # Deezer typically returns dates in YYYY-MM-DD format
            if raw_date:
                from datetime import datetime
                import platform
                try:
                    # Parse the date string
                    parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
                    # Format as "Month Day, Year"
                    try:
                        formatted_date = parsed_date.strftime("%B %-d, %Y") if platform.system() != "Windows" else parsed_date.strftime("%B %#d, %Y")
                    except (ValueError, TypeError):
                        # Fallback for platforms that don't support %- or %#
                        formatted_date = parsed_date.strftime("%B %d, %Y").replace(' 0', ' ')
                    return formatted_date
                except (ValueError, TypeError):
                    # If parsing fails, return the raw date
                    return raw_date
            return raw_date
        except (KeyError, IndexError):
            return None

    def parse_release_label(self, soup):
        label = soup.get("label")
        # Debug logging
        import click
        click.secho(f"[DEBUG] parse_release_label: label type = {type(label)}, value = {repr(label)}", fg="yellow")
        
        # Handle different label formats from Deezer API
        # Label can be a string, dict with "name" field, tuple/list, or other types
        if isinstance(label, dict):
            label = label.get("name", "")
        elif isinstance(label, (tuple, list)):
            # If tuple/list, take first element (usually the name)
            label = label[0] if label else ""
        elif not isinstance(label, str):
            label = str(label) if label else ""
        
        # Debug logging after conversion
        click.secho(f"[DEBUG] parse_release_label: converted label type = {type(label)}, value = {repr(label)}", fg="yellow")
        return parse_copyright(label)

    def parse_genres(self, soup):
        return {g["name"] for g in soup["genres"]["data"]}

    def parse_release_type(self, soup):
        # Try to get from Deezer's type mapping
        try:
            return RECORD_TYPES[soup["record_type"]]
        except KeyError:
            return None

    def parse_upc(self, soup):
        return soup["upc"]

    def parse_tracks(self, soup):
        tracks = defaultdict(dict)
        for track in soup["tracklist"]:
            tracks[str(track["DISK_NUMBER"])][str(track["TRACK_NUMBER"])] = self.generate_track(
                trackno=track["TRACK_NUMBER"],
                discno=track["DISK_NUMBER"],
                artists=self.parse_artists(track["SNG_CONTRIBUTORS"], track["ARTISTS"], track["SNG_TITLE"]),
                title=self.parse_title(track["SNG_TITLE"], track.get("VERSION", None)),
                isrc=track["ISRC"],
                explicit=track["EXPLICIT_LYRICS"],
                stream_id=track["SNG_ID"],
                md5_origin=track.get("MD5_ORIGIN"),
                media_version=track.get("MEDIA_VERSION"),
                lossless=True,
                mp3_320=True,
            )
        return dict(tracks)

    def process_label(self, data):
        label = data["label"]
        
        # Debug logging
        import click
        click.secho(f"[DEBUG] process_label: label type = {type(label)}, value = {repr(label)}", fg="yellow")
        click.secho(f"[DEBUG] process_label: artists = {repr(data.get('artists', []))}", fg="yellow")
        
        # Handle different label formats from Deezer API
        # Label can be a string, dict with "name" field, tuple/list, or other types
        if isinstance(label, dict):
            label = label.get("name", "")
        elif isinstance(label, (tuple, list)):
            # If tuple/list, take first element (usually the name)
            label = label[0] if label else ""
        elif not isinstance(label, str):
            label = str(label) if label else ""
        
        # Debug logging after conversion
        click.secho(f"[DEBUG] process_label: converted label type = {type(label)}, value = {repr(label)}", fg="yellow")
        
        # Check for self-released albums
        if label and any(
            label.lower().startswith(artist_name.lower()) and role == "main" 
            for artist_name, role in data["artists"]
        ):
            return "Self-Released"
        
        return label

    def parse_artists(self, artists, default_artists, title):
        """
        Iterate over all artists and roles, returning a compliant list of
        artist tuples.
        """
        result = []

        feat = RE_FEAT.search(title)
        if feat:
            for artist in re_split(feat[1]):
                result.append((unescape(artist), "guest"))

        if artists:
            for a in artists.get("mainartist", []) + artists.get("main_artist", []):
                for b in re_split(a):
                    if (b, "main") not in result:
                        result.append((b, "main"))
            for a in artists.get("featuredartist", []) + artists.get("featuring", []):
                for b in re_split(a):
                    if (b, "guest") not in result:
                        result.append((b, "guest"))
        else:
            for artist in default_artists:
                for b in re_split(artist["ART_NAME"]):
                    if (b, "main") not in result:
                        result.append((b, "main"))

        return result
