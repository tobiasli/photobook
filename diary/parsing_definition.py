import re

from parsing.parsing import Content, ContentFinder


class Text(Content):
    """A line of text for diary entry."""
    text: str


TEXT_PATTERN = re.compile(r'^(?P<text>[^#\*].+)$')
TEXT_FINDER = ContentFinder(start_pattern=TEXT_PATTERN, content_type=Text)


class Period(Content):
    """The relevant time period for the diary entry."""
    period: str


PERIOD_PATTERN = re.compile(r'\W?\*\W?(?P<period>\d+\.\d+\.\d+(?:-\d+\.\d+\.\d+)?)')
PERIOD_FINDER = ContentFinder(start_pattern=PERIOD_PATTERN, content_type=Period)


class Entry(Content):
    """All information related to a diary entry."""
    title: str
    timestamp: str

    @property
    def text(self) -> str:
        """Concat all matched text below this level."""
        # noinspection PyUnresolvedReferences
        return '\n'.join([t.text for t in self.get_contents_by_type(Text)])

    @property
    def period(self) -> str:
        """Get the relevant time period for the current diary entry.
        Rules:
            Always returns an actual time period. """
        # noinspection PyUnresolvedReferences
        return next((t.period for t in self.get_contents_by_type(Period)), None)


ENTRY_PATTERN = re.compile(r'^# ?(?P<timestamp>\d+\.\d+\.\d+(?:\W\d+:\d+))\W+(?P<title>\w.*?)$')
ENTRY_FINDER = ContentFinder(start_pattern=ENTRY_PATTERN,
                             content_type=Entry,
                             sub_content_finders=[TEXT_FINDER, PERIOD_FINDER]
                             )
