"""Retrieve Microsoft Download Center pages over HTTP."""

from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import FetchError
from .logger import init

#: Default timeout in seconds for HTTP requests.
DEFAULT_TIMEOUT = 30

#: Default number of retries after a transient network failure, such as a
#: connection reset or a truncated response.
DEFAULT_RETRIES = 2

#: HTTP headers sent with every request. The Download Center rejects
#: requests that do not look like they come from a web browser.
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_html(
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    headers: dict | None = None,
    retries: int = DEFAULT_RETRIES,
) -> str:
    """Retrieve a page and return its body as text.

    Transient network failures are retried; HTTP error statuses are not.

    :param url: URL of the page to retrieve.
    :param timeout: Request timeout in seconds.
    :param headers: Extra HTTP headers, merged over :data:`DEFAULT_HEADERS`.
    :param retries: Number of retries after a transient network failure.
    :returns: Decoded response body.
    :raises FetchError: If the server returns an error status, or the page
        cannot be retrieved after all retries.
    """
    logger = init()
    request = Request(url, headers={**DEFAULT_HEADERS, **(headers or {})})
    attempts = max(retries, 0) + 1
    attempt = 1
    while True:
        logger.debug("Fetching %s (attempt %s of %s)", url, attempt, attempts)
        try:
            return _read(request, timeout)
        except HTTPError as err:
            raise FetchError(
                f"HTTP {err.code} while fetching {url}", url, err.code
            ) from err
        except (URLError, TimeoutError, HTTPException) as err:
            if attempt >= attempts:
                raise FetchError(
                    f"Unable to fetch {url} after {attempts} attempt(s): {err!r}",
                    url,
                ) from err
            logger.warning("Retrying %s after error: %s", url, repr(err))
            attempt += 1


def _read(request: Request, timeout: float) -> str:
    """Send a request and decode the response body.

    :param request: Request to send.
    :param timeout: Request timeout in seconds.
    :returns: Decoded response body.
    """
    # URL scheme and host are validated by msdlcdetails.url before use.
    with urlopen(request, timeout=timeout) as response:  # nosec B310
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")
