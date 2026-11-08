"""Exceptions raised by MSDLC Details."""


class MSDLCDetailsError(Exception):
    """Base class for all errors raised by MSDLC Details."""


class InvalidUrlError(MSDLCDetailsError, ValueError):
    """Raised when a value is not a Microsoft Download Center details URL
    or download ID."""


class FetchError(MSDLCDetailsError):
    """Raised when a Download Center page cannot be retrieved.

    :param message: Description of the failure.
    :param url: URL that was being retrieved.
    :param status: HTTP status code, when the server responded.
    :ivar url: URL that was being retrieved.
    :ivar status: HTTP status code, or ``None`` when no response was received.
    """

    def __init__(self, message: str, url: str, status: int | None = None) -> None:
        super().__init__(message)
        self.url = url
        self.status = status


class DetailsNotFoundError(MSDLCDetailsError):
    """Raised when a page does not contain download details, for example
    because the download ID does not exist or the page layout has changed."""
