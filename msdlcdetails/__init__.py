"""
msdlcdetails
============
Retrieve details of Microsoft Download Center downloads, including the
current URL of the files behind a details page's Download button.
"""

from .errors import (
    DetailsNotFoundError,
    FetchError,
    InvalidUrlError,
    MSDLCDetailsError,
)
from .fetcher import DEFAULT_TIMEOUT, fetch_html
from .logger import init
from .models import DownloadDetails, DownloadFile, Locale, RelatedResource
from .parser import parse_details
from .url import build_url, normalise_url, parse_url


def get_details(
    url_or_id: str | int,
    locale: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> DownloadDetails:
    """Retrieve the details of a Microsoft Download Center download.

    :param url_or_id: Details page URL, e.g.
        ``https://www.microsoft.com/en-us/download/details.aspx?id=56519``,
        or a download ID such as ``56519``.
    :param locale: Culture code overriding the URL's page language.
    :param timeout: Request timeout in seconds.
    :returns: Download details. Use :attr:`DownloadDetails.download_url` for
        the current URL of the file behind the Download button.
    :raises InvalidUrlError: If ``url_or_id`` is not a details page URL or ID.
    :raises FetchError: If the page cannot be retrieved.
    :raises DetailsNotFoundError: If the page has no download details.
    """
    logger = init()
    url = normalise_url(url_or_id, locale)
    logger.info("Retrieving download details from %s", url)
    details = parse_details(fetch_html(url, timeout=timeout), url=url)
    logger.info("Found %s file(s) for download %s", len(details.files), url)
    return details
