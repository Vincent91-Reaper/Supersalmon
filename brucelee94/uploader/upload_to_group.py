import asyncio
from urllib import parse

import click

from brucelee94.errors import AbortAndDeleteFolder, RequestError

loop = asyncio.get_event_loop()


def check_existing_group(gazelle_site, offer_deletion=True):
    """
    Prompt user to select an existing torrent group or create a new one.
    """
    group_id = _prompt_for_group_id(gazelle_site, offer_deletion)
    if group_id:
        confirmation = _confirm_group_id(gazelle_site, group_id)
        if confirmation is True:
            return group_id
        return None
    return group_id


def _prompt_for_group_id(gazelle_site, offer_deletion):
    """Have the user choose a group ID"""
    delete_option = "/ [d]elete music folder " if offer_deletion else ""
    while True:
        group_id = click.prompt(
            click.style(
                "\nWould you like to upload to an existing group?\n"
                f"Paste a URL or enter a group ID, or [N]ew group / [a]bort {delete_option}",
                fg="magenta",
            ),
            default="",
        )
        if group_id.strip().isdigit():
            group_id_num = int(group_id)
            click.echo(f"Interpreting {group_id_num} as a group Id")
            return group_id_num

        elif group_id.strip().lower().startswith(gazelle_site.base_url + "/torrents.php"):
            parsed_query = parse.parse_qs(parse.urlparse(group_id).query)
            if "id" in parsed_query:
                group_id = parsed_query["id"][0]
            elif "torrentid" in parsed_query:
                group_id = parsed_query["torrentid"][0]
                group_id = loop.run_until_complete(gazelle_site.get_redirect_torrentgroupid(group_id))
                return group_id
            else:
                click.echo("Could not find group ID in URL.")
                continue
            return int(group_id)
        elif group_id.lower().startswith("a"):
            raise click.Abort
        elif group_id.lower().startswith("d") and offer_deletion:
            raise AbortAndDeleteFolder
        elif group_id.lower().startswith("n") or not group_id.strip():
            click.echo("Uploading to a new torrent group.")
            return None


def print_torrents(gazelle_site, group_id, rset=None, highlight_torrent_id=None):
    """Print the torrents that are a part of the torrent group."""
    # If rset is not provided, fetch it from the API
    if rset is None:
        try:
            rset = loop.run_until_complete(gazelle_site.torrentgroup(group_id))
            # account for differences between search result and group result json
            rset["groupName"] = rset["group"]["name"]
            rset["artist"] = ""
            for a in rset["group"]["musicInfo"]["artists"]:
                rset["artist"] += a["name"] + " "
            rset["groupId"] = rset["group"]["id"]
            rset["groupYear"] = rset["group"]["year"]
        except RequestError:
            click.secho(f"{group_id} does not exist.", fg="red")
            raise click.Abort from None

    group_info = {}
    click.secho(f"\nSelected ID: {rset['groupId']} ", nl=False)
    click.secho(f"| {rset['artist']} - {rset['groupName']} ", fg="cyan", nl=False)
    click.secho(f"({rset['groupYear']})", fg="yellow")
    click.secho("Torrents in this group:", fg="yellow", bold=True)
    for t in rset["torrents"]:
        color = "yellow" if highlight_torrent_id and t["id"] == highlight_torrent_id else None
        if t["remastered"]:
            click.secho(
                f"> {t['remasterYear']} / {t['remasterCatalogueNumber']} / "
                f"{t['media']} / {t['format']} / {t['encoding']}",
                fg=color,
            )
        if not t["remastered"]:
            if not group_info:
                group_info = loop.run_until_complete(gazelle_site.torrentgroup(group_id))["group"]
            click.secho(
                f"> OR / {group_info['recordLabel']} / "
                f"{group_info['catalogueNumber']} / {t['media']} / "
                f"{t['format']} / {t['encoding']}",
                fg=color,
            )


def _confirm_group_id(gazelle_site, group_id):
    """Have the user decide whether or not to upload to a torrent group."""
    print_torrents(gazelle_site, group_id)
    while True:
        resp = click.prompt(
            click.style(
                "\nAre you sure you would you like to upload this torrent to this group? [Y]es, "
                "[n]ew group, [a]bort, [d]elete music folder",
                fg="magenta",
            ),
            default="Y",
        )[0].lower()
        if resp == "a":
            raise click.Abort
        elif resp == "d":
            raise AbortAndDeleteFolder
        elif resp == "y":
            return True
        elif resp == "n":
            return False
