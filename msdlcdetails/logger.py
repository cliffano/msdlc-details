"""Logger for MSDLC Details."""

from conflog import Conflog

#: Cached logger, created by :func:`init` on first use.
LOGGER = None


def init():
    """Initialise logger.

    The logger is cached to prevent duplicate handlers from being added on
    repeated calls.

    :returns: Logger for MSDLC Details.
    """

    global LOGGER  # pylint: disable=global-statement
    if LOGGER is not None:
        return LOGGER

    cfl = Conflog(
        conf_dict={
            "level": "info",
            "format": "[msdlcdetails] %(levelname)s %(message)s",
        }
    )

    LOGGER = cfl.get_logger(__name__)
    return LOGGER
