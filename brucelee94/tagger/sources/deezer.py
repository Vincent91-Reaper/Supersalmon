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
        import click
        
        # Get label with safe debugging
        try:
            label = soup.get("label")
            click.secho(f"[DEBUG] parse_release_label: raw label type = {type(label).__name__}", fg="yellow", err=True)
            click.secho(f"[DEBUG] parse_release_label: raw label value = {str(label)[:100]}", fg="yellow", err=True)
        except Exception as e:
            click.secho(f"[DEBUG] parse_release_label: Error getting label: {e}", fg="red", err=True)
            label = ""
        
        # Handle different label formats from Deezer API
        # Label can be a string, dict with "name" field, tuple/list, or other types
        try:
            if isinstance(label, dict):
                label = label.get("name", "")
            elif isinstance(label, (tuple, list)):
                # If tuple/list, take first element (usually the name)
                # Handle nested structures: extract until we get a string
                while label and isinstance(label, (tuple, list)):
                    label = label[0] if label else ""
            elif not isinstance(label, str):
                label = str(label) if label else ""
            
            # Ensure label is a string
            if not isinstance(label, str):
                label = str(label) if label else ""
            
            # Debug logging after conversion
            click.secho(f"[DEBUG] parse_release_label: final label type = {type(label).__name__}", fg="cyan", err=True)
            click.secho(f"[DEBUG] parse_release_label: final label value = {str(label)[:100]}", fg="cyan", err=True)
        except Exception as e:
            click.secho(f"[DEBUG] parse_release_label: Error processing label: {e}", fg="red", err=True)
            label = str(label) if label else ""
        
        # Call parse_copyright with error handling
        try:
            result = parse_copyright(label)
            click.secho(f"[DEBUG] parse_release_label: parse_copyright returned = {str(result)[:100]}", fg="green", err=True)
            return result
        except Exception as e:
            click.secho(f"[DEBUG] parse_release_label: Error in parse_copyright: {e}", fg="red", err=True)
            return label

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
        import click
        
        # Get label with safe debugging
        try:
            label = data.get("label", "")
            click.secho(f"[DEBUG] process_label: raw label type = {type(label).__name__}", fg="magenta", err=True)
            click.secho(f"[DEBUG] process_label: raw label value = {str(label)[:100]}", fg="magenta", err=True)
        except Exception as e:
            click.secho(f"[DEBUG] process_label: Error getting label: {e}", fg="red", err=True)
            label = ""
        
        # Handle different label formats from Deezer API
        # Label can be a string, dict with "name" field, tuple/list, or other types
        try:
            if isinstance(label, dict):
                label = label.get("name", "")
            elif isinstance(label, (tuple, list)):
                # If tuple/list, take first element (usually the name)
                # Handle nested structures: extract until we get a string
                while label and isinstance(label, (tuple, list)):
                    label = label[0] if label else ""
            elif not isinstance(label, str):
                label = str(label) if label else ""
            
            # Ensure label is a string
            if not isinstance(label, str):
                label = str(label) if label else ""
            
            click.secho(f"[DEBUG] process_label: final label type = {type(label).__name__}", fg="magenta", err=True)
            click.secho(f"[DEBUG] process_label: final label value = {str(label)[:100]}", fg="magenta", err=True)
        except Exception as e:
            click.secho(f"[DEBUG] process_label: Error processing label: {e}", fg="red", err=True)
            label = str(label) if label else ""
        
        # Check for self-released albums
        if label and data.get("artists"):
            try:
                artists = data.get("artists", [])
                click.secho(f"[DEBUG] process_label: Checking {len(artists)} artists for self-released", fg="magenta", err=True)
                
                for artist_item in artists:
                    try:
                        # Safely unpack artist tuple
                        if isinstance(artist_item, (tuple, list)) and len(artist_item) >= 2:
                            artist_name, role = artist_item[0], artist_item[1]
                            # Ensure artist_name is string
                            if not isinstance(artist_name, str):
                                artist_name = str(artist_name)
                            click.secho(f"[DEBUG] process_label: Checking artist '{artist_name}' with role '{role}'", fg="magenta", err=True)
                            if label.lower().startswith(artist_name.lower()) and role == "main":
                                click.secho(f"[DEBUG] process_label: Self-released detected! Artist '{artist_name}' matches label", fg="green", err=True)
                                return "Self-Released"
                    except Exception as e:
                        click.secho(f"[DEBUG] process_label: Error checking artist {artist_item}: {e}", fg="red", err=True)
                        continue
            except Exception as e:
                click.secho(f"[DEBUG] process_label: Error in self-released check: {e}", fg="red", err=True)
                # Continue with original label if check fails
        
        click.secho(f"[DEBUG] process_label: Returning label = {str(label)[:100]}", fg="green", err=True)
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
