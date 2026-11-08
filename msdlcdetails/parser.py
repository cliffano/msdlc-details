"""Extract download details from Microsoft Download Center page HTML.

Download Center details pages embed their data as a JSON object assigned to
``window.__DLCDetails__`` in an inline script. This module reads that object
rather than scraping rendered HTML, which keeps parsing independent of page
styling.
"""

import json
from datetime import datetime

from .errors import DetailsNotFoundError
from .models.download_details import (
    DownloadDetails,
    DownloadFile,
    Locale,
    RelatedResource,
)

#: JavaScript assignment that precedes the embedded details JSON.
STATE_MARKER = "window.__DLCDetails__"

#: Format of file publication timestamps, e.g. ``11/3/2026 1:53:19 PM``.
DATE_PUBLISHED_FORMAT = "%m/%d/%Y %I:%M:%S %p"


def extract_state(html: str) -> dict:
    """Extract the details JSON object embedded in a details page.

    :param html: Details page HTML.
    :returns: The ``dlcDetailsView`` object.
    :raises DetailsNotFoundError: If the page does not embed details data,
        or the data reports an error.
    """
    start = html.find(STATE_MARKER)
    if start == -1:
        raise DetailsNotFoundError("Page does not contain download details data")

    equals = html.find("=", start + len(STATE_MARKER))
    if equals == -1:
        raise DetailsNotFoundError("Malformed download details data")

    try:
        state, _ = json.JSONDecoder().raw_decode(html[equals + 1 :].lstrip())
    except json.JSONDecodeError as err:
        raise DetailsNotFoundError(
            f"Unable to decode download details data: {err}"
        ) from err

    view = state.get("dlcDetailsView") if isinstance(state, dict) else None
    if not isinstance(view, dict):
        raise DetailsNotFoundError("Download details data has no details view")
    if view.get("error"):
        raise DetailsNotFoundError(f"Download Center error: {view['error']}")
    return view


def parse_details(html: str, url: str = "") -> DownloadDetails:
    """Parse download details from a details page.

    :param html: Details page HTML.
    :param url: URL the page was retrieved from.
    :returns: Parsed download details.
    :raises DetailsNotFoundError: If the page does not contain download
        details.
    """
    view = extract_state(html)
    return DownloadDetails(
        details_id=str(view.get("detailsId", "")),
        url=url,
        locale=view.get("locale", ""),
        title=view.get("downloadTitle", ""),
        description=view.get("downloadDescription", ""),
        version=view.get("detailsSection_file_version", ""),
        date_published=view.get("detailsSection_file_date", ""),
        files=[_parse_file(item) for item in view.get("downloadFile") or []],
        details=view.get("detailsSection", ""),
        system_requirements=view.get("systemRequirementsSection", ""),
        supported_os=list(view.get("systemRequirementsSection_supportedOS") or []),
        install_instructions=view.get("installInstructionSection", ""),
        additional_information=view.get("additionalInformationSection", ""),
        related_resources=[
            RelatedResource(title=item.get("title", ""), url=item.get("url", ""))
            for item in view.get("relatedResourcesSection") or []
        ],
        available_locales=[
            Locale(culture_code=item.get("cultureCode", ""), name=item.get("name", ""))
            for item in view.get("localeDropdown") or []
        ],
        raw=view,
    )


def _parse_file(item: dict) -> DownloadFile:
    """Convert a ``downloadFile`` entry into a :class:`DownloadFile`.

    :param item: Entry from the page's ``downloadFile`` list.
    :returns: Parsed file.
    """
    date_raw = item.get("datePublished", "")
    return DownloadFile(
        name=item.get("name", ""),
        url=item.get("url", ""),
        size=_parse_int(item.get("size")),
        version=item.get("version", ""),
        date_published=_parse_datetime(date_raw),
        date_published_raw=date_raw,
        is_primary=str(item.get("isPrimary", "")).lower() == "true",
    )


def _parse_int(value: object) -> int | None:
    """Convert a value to an integer.

    :param value: Value to convert.
    :returns: The integer, or ``None`` when the value is not numeric.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(value: str) -> datetime | None:
    """Parse a file publication timestamp.

    :param value: Timestamp in :data:`DATE_PUBLISHED_FORMAT`.
    :returns: The timestamp, or ``None`` when it cannot be parsed.
    """
    try:
        return datetime.strptime(value, DATE_PUBLISHED_FORMAT)
    except (TypeError, ValueError):
        return None
