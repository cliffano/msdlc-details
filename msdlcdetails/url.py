"""Parse and build Microsoft Download Center details page URLs."""

import re
from urllib.parse import parse_qs, urlparse

from .errors import InvalidUrlError

#: Host serving Microsoft Download Center details pages.
HOST = "www.microsoft.com"

#: Locale used when none is given or found in a URL.
DEFAULT_LOCALE = "en-us"

_PATH_PATTERN = re.compile(
    r"^/(?:(?P<locale>[a-z]{2,3}(?:-[a-z0-9]{2,4})?)/)?download/details(?:\.aspx)?/?$",
    re.IGNORECASE,
)
_ID_PATTERN = re.compile(r"^\d+$")
_LOCALE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,4})?$", re.IGNORECASE)


def build_url(details_id: str | int, locale: str = DEFAULT_LOCALE) -> str:
    """Build the canonical details page URL for a download ID.

    :param details_id: Numeric Download Center download ID, e.g. ``56519``.
    :param locale: Culture code of the page language, e.g. ``en-us``.
    :returns: Canonical details page URL.
    :raises InvalidUrlError: If the ID or locale is malformed.
    """
    details_id = str(details_id).strip()
    if not _ID_PATTERN.match(details_id):
        raise InvalidUrlError(f"Invalid download ID: {details_id!r}")
    if not _LOCALE_PATTERN.match(locale):
        raise InvalidUrlError(f"Invalid locale: {locale!r}")
    return f"https://{HOST}/{locale.lower()}/download/details.aspx?id={details_id}"


def parse_url(url_or_id: str | int) -> tuple[str, str]:
    """Extract the download ID and locale from a details page URL or ID.

    Accepts URLs such as
    ``https://www.microsoft.com/en-us/download/details.aspx?id=56519``,
    the newer ``/download/details?id=56519`` form, URLs without a locale,
    and bare download IDs.

    :param url_or_id: Details page URL or numeric download ID.
    :returns: Tuple of ``(details_id, locale)``. The locale falls back to
        :data:`DEFAULT_LOCALE` when the URL does not contain one.
    :raises InvalidUrlError: If the value is not a recognised details page
        URL or download ID.
    """
    value = str(url_or_id).strip()
    if _ID_PATTERN.match(value):
        return value, DEFAULT_LOCALE

    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or parsed.hostname not in (
        HOST,
        "microsoft.com",
    ):
        raise InvalidUrlError(f"Not a Microsoft Download Center URL: {value!r}")

    match = _PATH_PATTERN.match(parsed.path)
    if not match:
        raise InvalidUrlError(f"Not a Download Center details page URL: {value!r}")

    ids = parse_qs(parsed.query).get("id", [])
    if len(ids) != 1 or not _ID_PATTERN.match(ids[0]):
        raise InvalidUrlError(f"Missing or invalid download ID in URL: {value!r}")

    locale = (match.group("locale") or DEFAULT_LOCALE).lower()
    return ids[0], locale


def normalise_url(url_or_id: str | int, locale: str | None = None) -> str:
    """Convert a details page URL or download ID into its canonical URL.

    :param url_or_id: Details page URL or numeric download ID.
    :param locale: Culture code overriding the locale found in the URL.
    :returns: Canonical details page URL.
    :raises InvalidUrlError: If the value or locale is malformed.
    """
    details_id, url_locale = parse_url(url_or_id)
    return build_url(details_id, locale or url_locale)
