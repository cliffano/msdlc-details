"""Data classes describing a Microsoft Download Center download."""

from dataclasses import dataclass, field
from datetime import datetime
from fnmatch import fnmatch


@dataclass(frozen=True)
class DownloadFile:
    """A file offered by a download, i.e. a target of the Download button.

    :ivar name: File name, e.g. ``ServiceTags_Public_20261102.json``.
    :ivar url: Direct URL of the file on ``download.microsoft.com``.
    :ivar size: File size in bytes, or ``None`` when unknown.
    :ivar version: File version as shown on the page.
    :ivar date_published: Publication timestamp, or ``None`` when the page
        value cannot be parsed.
    :ivar date_published_raw: Publication timestamp exactly as on the page.
    :ivar is_primary: Whether the page flags this file as the primary one.
    """

    #: File name, e.g. ``ServiceTags_Public_20261102.json``.
    name: str
    #: Direct URL of the file on ``download.microsoft.com``.
    url: str
    #: File size in bytes, or ``None`` when unknown.
    size: int | None = None
    #: File version as shown on the page.
    version: str = ""
    #: Publication timestamp, or ``None`` when it cannot be parsed.
    date_published: datetime | None = None
    #: Publication timestamp exactly as on the page.
    date_published_raw: str = ""
    #: Whether the page flags this file as the primary one.
    is_primary: bool = False


@dataclass(frozen=True)
class RelatedResource:
    """A link listed in the page's Related resources section.

    :ivar title: Link title.
    :ivar url: Link URL.
    """

    #: Link title.
    title: str
    #: Link URL.
    url: str


@dataclass(frozen=True)
class Locale:
    """A language the details page is available in.

    :ivar culture_code: Culture code, e.g. ``en-us``.
    :ivar name: Language name, e.g. ``English``.
    """

    #: Culture code, e.g. ``en-us``.
    culture_code: str
    #: Language name, e.g. ``English``.
    name: str


@dataclass(frozen=True)
class DownloadDetails:  # pylint: disable=too-many-instance-attributes
    """Details of a Microsoft Download Center download.

    Text sections such as :attr:`details` and :attr:`install_instructions`
    are returned as on the page and may contain HTML markup.

    :ivar details_id: Download ID, e.g. ``56519``.
    :ivar url: Details page URL the information was retrieved from.
    :ivar locale: Culture code of the page, e.g. ``en-us``.
    :ivar title: Download title.
    :ivar description: Short description of the download.
    :ivar version: Version shown in the Details section.
    :ivar date_published: Date published shown in the Details section,
        exactly as on the page.
    :ivar files: Files offered by the Download button.
    :ivar details: Details section text.
    :ivar system_requirements: System requirements section text.
    :ivar supported_os: Supported operating systems.
    :ivar install_instructions: Install instructions section text.
    :ivar additional_information: Additional information section text.
    :ivar related_resources: Related resources links.
    :ivar available_locales: Languages the page is available in.
    :ivar raw: Unprocessed details data embedded in the page, for values
        not exposed as attributes.
    """

    #: Download ID, e.g. ``56519``.
    details_id: str
    #: Details page URL the information was retrieved from.
    url: str
    #: Culture code of the page, e.g. ``en-us``.
    locale: str
    #: Download title.
    title: str
    #: Short description of the download.
    description: str = ""
    #: Version shown in the Details section.
    version: str = ""
    #: Date published shown in the Details section, exactly as on the page.
    date_published: str = ""
    #: Files offered by the Download button.
    files: list[DownloadFile] = field(default_factory=list)
    #: Details section text.
    details: str = ""
    #: System requirements section text.
    system_requirements: str = ""
    #: Supported operating systems.
    supported_os: list[str] = field(default_factory=list)
    #: Install instructions section text.
    install_instructions: str = ""
    #: Additional information section text.
    additional_information: str = ""
    #: Related resources links.
    related_resources: list[RelatedResource] = field(default_factory=list)
    #: Languages the page is available in.
    available_locales: list[Locale] = field(default_factory=list)
    #: Unprocessed details data embedded in the page.
    raw: dict = field(default_factory=dict, repr=False, compare=False)

    @property
    def primary_file(self) -> DownloadFile | None:
        """The file the Download button points to.

        This is the file flagged as primary on the page, or the first file
        when none is flagged. For downloads offering several files, consider
        :meth:`find_file` to select a specific one.

        :returns: The primary file, or ``None`` when no files are offered.
        """
        for download_file in self.files:
            if download_file.is_primary:
                return download_file
        return self.files[0] if self.files else None

    @property
    def download_url(self) -> str | None:
        """URL of :attr:`primary_file`.

        :returns: Direct download URL, or ``None`` when no files are offered.
        """
        primary = self.primary_file
        return primary.url if primary else None

    def find_file(self, pattern: str) -> DownloadFile | None:
        """Find the first file whose name matches a shell-style pattern.

        Matching is case-insensitive, e.g. ``"*x64*.exe"`` or
        ``"ServiceTags_Public_*.json"``.

        :param pattern: :mod:`fnmatch` pattern matched against file names.
        :returns: The first matching file, or ``None`` when none matches.
        """
        for download_file in self.files:
            if fnmatch(download_file.name.lower(), pattern.lower()):
                return download_file
        return None
