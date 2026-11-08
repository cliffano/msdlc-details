"""Shared Download Center page data for unit tests.

The views mirror the ``dlcDetailsView`` objects embedded in real details
pages, trimmed to the fields MSDLC Details reads.
"""

import json

#: Details view of a single-file download (id 56519).
SINGLE_FILE_VIEW = {
    "error": "",
    "downloadTitle": "Azure IP Ranges and Service Tags – Public Cloud",
    "downloadDescription": "Azure IP Ranges and Service Tags – Public Cloud",
    "downloadFile": [
        {
            "isPrimary": "False",
            "name": "ServiceTags_Public_20261102.json",
            "url": (
                "https://download.microsoft.com/download/7/1/d/"
                "71d86715-5596-4529-9b13-da13a5de5b63/"
                "ServiceTags_Public_20261102.json"
            ),
            "size": "4570790",
            "version": "2026.11.02",
            "datePublished": "11/3/2026 1:53:19 PM",
        }
    ],
    "localeDropdown": [{"cultureCode": "en-us", "name": "English"}],
    "detailsSection": "This file contains the IP address ranges for Public Azure.",
    "detailsSection_file_version": "2026.11.02",
    "detailsSection_file_date": "11/3/2026",
    "systemRequirementsSection": "Json reader recommended",
    "systemRequirementsSection_supportedOS": ["Windows Server 2016"],
    "installInstructionSection": "Download the new json file every week.",
    "relatedResourcesSection": [],
    "locale": "en-us",
    "detailsId": "56519",
}

#: Details view of a multi-file download with a primary file (id 102),
#: including values that cannot be parsed.
MULTI_FILE_VIEW = {
    "error": "",
    "downloadTitle": "Microsoft PowerPivot Samples",
    "downloadFile": [
        {
            "isPrimary": "False",
            "name": "PowerPivotExamplesExcel2013.zip",
            "url": "https://download.microsoft.com/download/0/2/c/2013.zip",
            "size": "93227452",
            "version": "version 1.0",
            "datePublished": "7/15/2024 3:08:07 AM",
        },
        {
            "isPrimary": "True",
            "name": "PowerPivotExamplesExcel2010.zip",
            "url": "https://download.microsoft.com/download/0/2/c/2010.zip",
            "size": "unknown",
            "version": "version 1.0",
            "datePublished": "15.07.2024 03:08:07",
        },
    ],
    "localeDropdown": [
        {"cultureCode": "en-us", "name": "English"},
        {"cultureCode": "ja-jp", "name": "Japanese"},
    ],
    "additionalInformationSection": "See the <a href='http://x'>Readme</a>.",
    "relatedResourcesSection": [
        {"title": "Developer Center", "url": "http://go.microsoft.com/fwlink/"}
    ],
    "locale": "en-us",
    "detailsId": 102,
}


def build_html(state: object) -> str:
    """Build a details page embedding state like the Download Center does.

    :param state: Value assigned to ``window.__DLCDetails__``.
    :returns: Page HTML.
    """
    return (
        "<!DOCTYPE html><html><head><title>Download</title></head><body>"
        "<script>window.__DLCDetails__="
        + json.dumps(state)
        + "</script><div id='rootContainer_DLCDetails'></div></body></html>"
    )
