<!-- BEGIN:AVATAR -->
![Avatar](avatar.jpg)
<!-- END:AVATAR -->

<!-- BEGIN:BADGES -->
[![Build Status](https://github.com/cliffano/msdlc-details/workflows/CI/badge.svg)](https://github.com/cliffano/msdlc-details/actions?query=workflow%3ACI)
[![Code Scanning Status](https://github.com/cliffano/msdlc-details/workflows/CodeQL/badge.svg)](https://github.com/cliffano/msdlc-details/actions?query=workflow%3ACodeQL)
[![Dependencies Status](https://img.shields.io/librariesio/release/pypi/msdlcdetails)](https://libraries.io/npm/msdlcdetails)
[![Security Status](https://snyk.io/test/github/cliffano/msdlc-details/badge.svg)](https://snyk.io/test/github/cliffano/msdlc-details)
[![Published Version](https://img.shields.io/pypi/v/msdlcdetails.svg)](https://pypi.python.org/pypi/msdlcdetails)
<!-- END:BADGES -->

# MSDLC Details

MSDLC Details is a micro library for retrieving Microsoft Download Center page details.

A Download Center details page such as
<https://www.microsoft.com/en-us/download/details.aspx?id=56519> keeps a stable
URL, while the file behind its Download button changes with every release.
MSDLC Details reads the page and returns the current file URL along with the
rest of the download's details.

## Installation

```shell
pip3 install msdlcdetails
```

## Usage

```python
from msdlcdetails import get_details

details = get_details("https://www.microsoft.com/en-us/download/details.aspx?id=56519")

print(details.title)         # Azure IP Ranges and Service Tags – Public Cloud
print(details.version)       # 2026.11.02
print(details.download_url)  # https://download.microsoft.com/download/.../ServiceTags_Public_20261102.json
```

`get_details` accepts a details page URL (`details.aspx?id=` or `details?id=`,
with or without a locale) or a bare download ID such as `56519`. Optional
arguments are `locale` (e.g. `ja-jp`, overriding the URL's language) and
`timeout` in seconds.

Some downloads offer several files. `download_url` returns the file flagged as
primary on the page, or the first file when none is flagged. Use `files` or
`find_file` to choose a specific one:

```python
details = get_details(40784)  # Visual C++ Redistributable for Visual Studio 2013
x64 = details.find_file("*x64*.exe")
print(x64.url, x64.size)
```

To parse HTML you have already retrieved, use `parse_details(html)`.

## Download details

| Attribute | Type | Description |
|-----------|------|-------------|
| `details_id` | String | Download ID, e.g. `56519` |
| `url` | String | Details page URL |
| `locale` | String | Page culture code, e.g. `en-us` |
| `title` | String | Download title |
| `description` | String | Short description |
| `version` | String | Version shown in the Details section |
| `date_published` | String | Date published shown in the Details section, as on the page |
| `files` | List of `DownloadFile` | Files offered by the Download button |
| `primary_file` | `DownloadFile` | File the Download button points to |
| `download_url` | String | URL of `primary_file` |
| `details` | String | Details section text (may contain HTML) |
| `system_requirements` | String | System requirements text (may contain HTML) |
| `supported_os` | List of strings | Supported operating systems |
| `install_instructions` | String | Install instructions text (may contain HTML) |
| `additional_information` | String | Additional information text (may contain HTML) |
| `related_resources` | List of `RelatedResource` | Related links, each with `title` and `url` |
| `available_locales` | List of `Locale` | Page languages, each with `culture_code` and `name` |
| `raw` | Dictionary | Unprocessed data embedded in the page |

Each `DownloadFile` has `name`, `url`, `size` (bytes), `version`,
`date_published` (`datetime`, or `None` when unparseable), `date_published_raw`
and `is_primary`.

## Errors

All errors subclass `MSDLCDetailsError`:

| Error | Raised when |
|-------|-------------|
| `InvalidUrlError` | The value is not a Download Center details URL or ID (also a `ValueError`) |
| `FetchError` | The page returns an HTTP error, or cannot be retrieved after retrying transient network failures |
| `DetailsNotFoundError` | The page has no download details, e.g. an unknown download ID |

## How it works

Details pages embed their data as JSON in an inline script,
`window.__DLCDetails__={"dlcDetailsView":{...}}`. MSDLC Details decodes that
object directly rather than scraping rendered HTML. Requests are sent with
browser-like headers because the Download Center rejects some non-browser
clients.

## Colophon

<!-- BEGIN:DEVELOPERS_GUIDE -->
[Developer's Guide](https://cliffano.github.io/developers-guide-python.html)
<!-- END:DEVELOPERS_GUIDE -->

<!-- BEGIN:BUILD_REPORTS -->
Build reports:

* [Lint report](https://cliffano.github.io/msdlc-details/lint/pylint/index.html)
* [Code complexity report](https://cliffano.github.io/msdlc-details/complexity/radon/index.html)
* [Unit tests report](https://cliffano.github.io/msdlc-details/test/pytest/index.html)
* [Test coverage report](https://cliffano.github.io/msdlc-details/coverage/coverage/index.html)
* [Integration tests report](https://cliffano.github.io/msdlc-details/test-integration/pytest/index.html)
* [API Documentation](https://cliffano.github.io/msdlc-details/doc/sphinx/index.html)

<!-- END:BUILD_REPORTS -->
