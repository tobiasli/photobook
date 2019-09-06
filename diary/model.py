from photobook.parsing import Content, ContentFinder

class Text(Content):
    """A line of text for diary entry."""
    text: str

class Entry(Content):
    """All information related to a diary entry """
    timestamp: str
    period: str
    title: str

    @property
    def text(self) -> str:
        """Concat all matched text below this level."""
        return '\n'.join([t.text for t in self.get_contents_by_type(Text)]