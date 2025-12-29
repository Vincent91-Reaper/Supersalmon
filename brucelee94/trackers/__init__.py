from urllib import parse

import click

from brucelee94 import cfg
from brucelee94.trackers import red

# Only RED tracker is supported
tracker_classes = {"RED": red.RedApi}
tracker_url_code_map = {"redacted.sh": "RED"}

tracker_cfg = cfg.tracker
tracker_list = []
if tracker_cfg.red:
    tracker_list.append("RED")


def get_class(site_code):
    "Returns the api class from the tracker string."
    return tracker_classes[site_code]


def choose_tracker(choices):
    """Allows the user to choose a tracker from choices."""
    while True:
        # Loop until we have chosen a tracker or aborted.
        tracker_input = click.prompt(
            click.style(f"Your choices are {' , '.join(choices)} or [n]one.", fg="magenta"),
            default=choices[0],
        )
        tracker_input = tracker_input.strip().upper()
        if tracker_input in choices:
            return tracker_input
        # this part allows input of the first letter of the tracker.
        elif tracker_input in [choice[0] for choice in choices]:
            for choice in choices:
                if tracker_input == choice[0]:
                    return choice
        elif tracker_input.lower().startswith("n"):
            return None


def choose_tracker_first_time(question="Which tracker would you like to upload to?"):
    """Returns RED tracker. Simplified since only RED is supported."""
    # Always return RED since it's the only tracker
    return "RED"


def validate_tracker(ctx, param, value):
    """Validates and returns RED tracker. Simplified since only RED is supported."""
    # Always return RED since it's the only supported tracker
    if value is None or value.upper() == "RED":
        return "RED"
    else:
        click.secho(f"{value} is not supported. Only RED tracker is available.", fg="red")
        return "RED"


def validate_request(gazelle_site, request):
    """Check the request id is a url or number. and return the number.
    Should it check more? Currently not checking it is the right tracker.
    """
    try:
        if request is None:
            return None
        if request.strip().isdigit():
            pass
        elif request.strip().lower().startswith(gazelle_site.base_url + "/requests.php"):
            request = parse.parse_qs(parse.urlparse(request).query)["id"][0]
        click.secho(
            f"Attempting to fill {gazelle_site.base_url}/requests.php?action=view&id={request}",
            fg="green",
        )
        return request
    except (KeyError, AttributeError):
        raise click.BadParameter("This flag requires a request, either as a url or ID") from None
