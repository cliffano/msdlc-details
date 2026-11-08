"""Example: retrieve the details of the Azure IP Ranges and Service Tags
download, including the current URL of the file behind its Download button."""

from msdlcdetails import get_details
from msdlcdetails.logger import init

logger = init()

details = get_details("https://www.microsoft.com/en-us/download/details.aspx?id=56519")

logger.info("Title: %s", details.title)
logger.info("Version: %s", details.version)
logger.info("Published: %s", details.date_published)
for download_file in details.files:
    logger.info("File: %s (%s bytes)", download_file.name, download_file.size)
logger.info("Download URL: %s", details.download_url)
