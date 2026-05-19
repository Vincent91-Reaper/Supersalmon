import json
import re
from collections import defaultdict

from brucelee94.common import RE_FEAT, parse_copyright
from brucelee94.errors import ScrapeError
from brucelee94.sources import iTunesBase
from brucelee94.tagger.sources.base import MetadataMixin

ALIAS_GENRE = {
    "Hip-Hop/Rap": {"Hip Hop", "Rap"},
    "R&B/Soul": {"Rhythm & Blues", "Soul"},
    "Music": {},  # Aliasing Music to an empty set because we don't want a genre 'music'
}


def _amp_album(soup):
    if isinstance(soup, dict):
        data = soup.get("data") or []
        return data[0] if data else {}
    return {}


def _amp_attrs(soup):
    return _amp_album(soup).get("attributes", {})


def _amp_tracks(soup):
    album = _amp_album(soup)
    return album.get("relationships", {}).get("tracks", {}).get("data", [])


def _amp_artists(soup):
    album = _amp_album(soup)
    return album.get("relationships", {}).get("artists", {}).get("data", [])


class Scraper(iTunesBase, MetadataMixin):
    def parse_release_title(self, soup):
        if isinstance(soup, dict):
            title = _amp_attrs(soup).get("name", "").strip()
            if not title:
                raise ScrapeError("Failed to parse Apple Music title from AMP API.")
            return RE_FEAT.sub("", title)
        try:
            title = soup.find("meta", {"name": "apple:title"})["content"].strip()
            return RE_FEAT.sub("", title)
        except (TypeError, IndexError) as e:
            raise ScrapeError("Failed to parse scraped title.") from e

    def parse_cover_url(self, soup):
        if isinstance(soup, dict):
            artwork = _amp_attrs(soup).get("artwork", {}).get("url")
            return artwork.replace("{w}x{h}", "100000x100000-999") if artwork else None
        try:
            cover_url = soup.find("meta", {"property": "og:image"})["content"].strip()
            enhanced_url = re.sub(r'\d+x\d+bb', '100000x100000-999', cover_url)
            return enhanced_url
        except (TypeError, IndexError) as e:
            raise ScrapeError("Could not parse cover URL.") from e

    def parse_genres(self, soup):
        if isinstance(soup, dict):
            return {g for gs in _amp_attrs(soup).get("genreNames", []) for g in ALIAS_GENRE.get(gs, [gs])}
        try:
            info = json.loads(soup.find("script", {"id": "schema:music-album"}).text)
            genres = {g for gs in info["genre"] for g in ALIAS_GENRE.get(gs, [gs])}
            return genres
        except (TypeError, IndexError) as e:
            raise ScrapeError("Could not parse genres.") from e

    def parse_release_year(self, soup):
        try:
            return int(re.search(r"(\d{4})", self.parse_release_date(soup))[1])
        except TypeError as e:
            raise ScrapeError("Could not parse release year.") from e

    def parse_release_type(self, soup):
        try:
            if isinstance(soup, dict):
                title = _amp_attrs(soup).get("name", "")
            else:
                title = soup.find("meta", {"name": "apple:title"})["content"].strip()
            if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
                return "DJ Mix"
            if re.match(r".*\sEP$", title, re.IGNORECASE):
                return "EP"
            if re.match(r".*\sSingle$", title, re.IGNORECASE):
                return "Single"
            return "Album"
        except TypeError as e:
            raise ScrapeError("Could not parse release type.") from e

    def parse_release_date(self, soup):
        """Parse and format the Apple Music release date."""
        try:
            if isinstance(soup, dict):
                raw_date = _amp_attrs(soup).get("releaseDate")
            else:
                raw_date = soup.find(attrs={"property": "music:release_date"})["content"]
            date_string = raw_date.split("T")[0]
            if date_string:
                from datetime import datetime
                parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
                return parsed_date.strftime("%B %d, %Y")
            return None
        except BaseException:
            return None

    def parse_release_label(self, soup):
        if isinstance(soup, dict):
            title = _amp_attrs(soup).get("name", "")
            if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
                return ""
            return _amp_attrs(soup).get("recordLabel") or parse_copyright(_amp_attrs(soup).get("copyright", ""))
        try:
            title = soup.find("meta", {"name": "apple:title"})["content"].strip()
            if re.search(r"DJ[\s\-]*Mix", title, re.IGNORECASE):
                return ""
            json.loads(soup.find("script", {"id": "serialized-server-data"}).text)
            copyright = soup.find("p", {"data-testid": "tracklist-footer-description"}).text
            return parse_copyright(copyright)
        except IndexError as e:
            raise ScrapeError("Could not parse record label.") from e

    def parse_upc(self, soup):
        if isinstance(soup, dict):
            return _amp_attrs(soup).get("upc")
        return None

    def parse_comment(self, soup):
        if isinstance(soup, dict):
            return None
        try:
            return soup.select(".product-hero-desc .product-hero-desc__section > p")[0]["aria-label"].strip()
        except IndexError:
            return None

    def parse_tracks(self, soup):
        tracks = defaultdict(dict)
        cur_disc = 1

        if isinstance(soup, dict):
            album_artists = [(a.get("attributes", {}).get("name"), "main") for a in _amp_artists(soup)]
            album_artists = [(name, role) for name, role in album_artists if name]
            for track in _amp_tracks(soup):
                attrs = track.get("attributes", {})
                track_artists = [
                    (a.get("attributes", {}).get("name"), "main")
                    for a in track.get("relationships", {}).get("artists", {}).get("data", [])
                ]
                track_artists = [(name, role) for name, role in track_artists if name] or album_artists
                discno = attrs.get("discNumber") or 1
                trackno = attrs.get("trackNumber") or 1
                title = RE_FEAT.sub("", attrs.get("name", ""))
                tracks[str(discno)][trackno] = self.generate_track(
                    trackno=trackno,
                    discno=discno,
                    artists=track_artists,
                    title=title,
                    explicit=attrs.get("contentRating") == "explicit",
                )
            return dict(tracks)

        # Find and parse JSON data from <script> tag
        script_tag = soup.find("script", {"type": "application/ld+json"})
        if not script_tag:
            raise ScrapeError("JSON-LD script not found. Scraping needs to be updated")

        try:
            data = json.loads(script_tag.string)
        except json.JSONDecodeError as e:
            raise ScrapeError("Failed to decode JSON data.") from e

        if "tracks" not in data:
            raise ScrapeError("Tracks data not found in JSON.")

        # Check if this is a DJ Mix - only extract per-track artists for DJ Mix releases
        release_type = self.parse_release_type(soup)
        is_dj_mix = (release_type == "DJ Mix")

        # Try multiple methods to extract album-level artists
        header_artists = parse_artists_header(soup)
        
        # If header parsing fails, try extracting from JSON-LD data
        if not header_artists and "byArtist" in data:
            artist_data = data["byArtist"]
            if isinstance(artist_data, dict) and "name" in artist_data:
                header_artists = [artist_data["name"]]
            elif isinstance(artist_data, list):
                header_artists = [a["name"] for a in artist_data if "name" in a]
        
        # If still no artists found, try the meta tag
        if not header_artists:
            try:
                artist_meta = soup.find("meta", {"property": "music:musician"})
                if artist_meta and artist_meta.get("content"):
                    header_artists = [artist_meta["content"].strip()]
            except (TypeError, AttributeError):
                pass
        
        # Convert to the format expected by generate_track: [(name, importance)]
        # Use "main" importance for album-level artists
        artists_tuples = [(artist, "main") for artist in header_artists]

        # For DJ Mix: Parse HTML track elements to extract per-track artists
        html_tracks = []
        if is_dj_mix:
            # Find HTML track rows - they should match JSON-LD tracks by index
            html_tracks = soup.select(".songs-list-row")

        for index, track in enumerate(data["tracks"], start=1):
            try:
                num = index
                raw_title = track.get("name", "").strip()
                title = RE_FEAT.sub("", raw_title)

                # TODO: handle explicit + discnumber + artists (if available, will have to modify num too)
                # explicit = track.get("isExplicit", False)

                # Increment disc number if necessary
                # if int(num) == 1 and num in tracks[str(cur_disc)]:
                #    cur_disc += 1

                # For DJ Mix ONLY: Extract per-track artists from HTML data
                # For regular albums: Use album-level artists (existing behavior)
                track_artists = artists_tuples  # Default to album artists
                
                if is_dj_mix:
                    # Extract per-track artists for DJ Mix releases from HTML
                    per_track_artists = []
                    
                    # Get corresponding HTML track element (0-indexed)
                    if index - 1 < len(html_tracks):
                        html_track = html_tracks[index - 1]
                        # Extract main artists from HTML by-line
                        track_artist_names = parse_artists_track(html_track)
                        for artist_name in track_artist_names:
                            per_track_artists.append((artist_name, "main"))
                    
                    # Extract guest artists from title (feat. ...)
                    feat_match = RE_FEAT.search(raw_title)
                    if feat_match:
                        feat_str = feat_match.group(1)
                        # Parse featured artists
                        guest_artists = _parse_artists_commas(feat_str)
                        for guest in guest_artists:
                            per_track_artists.append((guest, "guest"))
                    
                    # Use per-track artists if found, otherwise fall back to album artists
                    if per_track_artists:
                        track_artists = per_track_artists

                tracks[str(cur_disc)][num] = self.generate_track(
                    trackno=num,
                    discno=cur_disc,
                    artists=track_artists,
                    title=title,
                    # explicit=explicit,
                )
            except (ValueError, KeyError) as e:
                raise ScrapeError("Could not parse tracks.") from e

        return dict(tracks)


def parse_artists(soup, track, title):
    """
    Parse all the artists from various locations and compile a split
    list of all of them.  This is not foolproof, but better than the
    alternative. Artists such as Vintage & Morelli will fuck this up,
    but that is why we have manual confirmation for metadata.
    """
    header_artists = parse_artists_header(soup)
    track_artists = parse_artists_track(track)
    title_artists = parse_artists_title(title)
    return reconcile_artists(header_artists, track_artists, title_artists)


def parse_artists_header(soup):
    """Parse the artists listed in the header as artists of the release."""
    artists = []
    if not hasattr(soup, "select"):
        return artists
    try:
        release_artists = soup.select(".product-creator")[0].a.string.strip()
    except (AttributeError, TypeError, IndexError):
        return artists

    if re.match(r"[^,]+, [^&]+ (& [^&]+)+", release_artists):
        first_artist, rest = release_artists.split(",", 1)
        artists.append(first_artist)
        for a in rest.split("&"):
            a = a.strip()
            if a not in artists:
                artists.append(a)
    elif "&" in release_artists:
        for a in release_artists.split("&"):
            a = a.strip()
            if a not in artists:
                artists.append(a)
    else:
        artists.append(release_artists.strip())
    return artists


def parse_artists_track(track):
    """Parse the artists listed per-track, below the track title."""
    if not hasattr(track, "select"):
        return []
    track_block = track.select(".by-line.typography-caption")
    if len(track_block) == 1:
        biline = track_block[0].text.strip().replace("\n", ", ")
        if biline[0:3] == "By ":
            return _parse_artists_commas(biline[2:])
        else:
            return _parse_artists_commas(biline)
    return []


def parse_artists_title(title):
    """Parse the guest artists from the track title."""
    feat = RE_FEAT.search(title)
    if feat:
        return _parse_artists_commas(feat[1])
    return set()


def _parse_artists_commas(artiststr):
    """
    Parse the artist names when they begin with commas and end with one
    ampersand. Split and strip them.
    """
    artists = []
    res = re.match(r"([^,]+)((?:, [^,&]+)+) & (.+)$", artiststr)
    if res:
        artists = [res[1].strip()] + [r.strip() for r in res[2].split(",") if r.strip()]
        for a in artists:
            if a not in artists:
                artists.append(a)
        artists.append(res[3].strip())
    elif "&" in artiststr:
        for a in artiststr.split("&"):
            a = a.strip()
            if a not in artists:
                artists.append(a)
    else:
        artists.append(artiststr.strip())
    return artists


def reconcile_artists(headers, tracks, titles):
    """De-duplicate the scraped artists and return a completed list."""
    artists = []
    for artist in tracks if tracks else headers:
        if (artist, "main") not in artists:
            artists.append((artist, "main"))
    for artist in titles:
        if (artist, "guest") not in artists:
            artists.append((artist, "guest"))
    return artists
