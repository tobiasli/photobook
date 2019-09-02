"""This file contains the base classes used for representing photobook contents."""
import typing as ty
import re
from photobook.readers import TextStream


class Content:
    contents: ty.List['Content'] = None

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.contents = list()

    def add_content(self, content: 'Content') -> None:
        """Add sub-content to this content."""
        self.contents.append(content)

    def get_contents_by_type(self, t: ty.Type['Content']) -> ty.List['Content']:
        """From the current Content.contents, return a list of items matching type t."""
        return [c for c in self.contents if isinstance(c, t)]


class ContentFinder:
    """Generic class for finding and returning text file contents."""

    def __init__(self,
                 start_pattern: ty.Pattern,
                 content_type: ty.Optional[ty.Type[Content]] = Content,
                 end_pattern: ty.Optional[ty.Pattern] = None,
                 sub_content_finders: ty.Optional[ty.Sequence["ContentFinder"]] = None):
        """Class for finding and representing contents in a text file."""
        self.start_pattern = start_pattern
        self.end_pattern = end_pattern
        self.content_type = content_type
        self.sub_content_finders = sub_content_finders if sub_content_finders else list()

    def search_stream(self, stream: TextStream) -> Content:
        """Start a sequential search through a text stream."""
        content = None
        while True:
            line = stream.get_line()
            if line is None:
                break
            else:
                if not content:
                    if self.start_pattern.match(line):
                        print(f'{self.content_type} matched {line}')
                        properties = next(self.start_pattern.finditer(line)).groupdict()
                        content = self.content_type(**properties)
                else:
                    if self.end_pattern and self.end_pattern.match(line):
                        # We are done here!
                        break
                    elif self.start_pattern.match(line):
                        # Assumes that reaching a start_pattern again means end of current ant start of new.
                        # So we are done here, and need to parse current line again:
                        stream.backtrack_reader_number_of_lines(1)
                        break
                    else:  # We now go looking for sub_content.
                        for sub in self.sub_content_finders:
                            if sub.start_pattern.match(line):
                                # Backtrack stream to reevaluate current line, and send the stream into the sub_finder
                                # that matched.
                                stream.backtrack_reader_number_of_lines(1)
                                sub_content = sub.search_stream(stream)
                                content.add_content(sub_content)

        return content


class File(Content):
    """Simplest possible content for the data in an entire file."""


class FileFinder(ContentFinder):
    """Content finder for matching the entire contents of a File."""

    def __init__(self, sub_content_finders: ty.Optional[ty.Sequence["ContentFinder"]] = None) -> None:
        super(FileFinder, self).__init__(start_pattern=re.compile('.'),
                                         content_type=File,
                                         sub_content_finders=sub_content_finders)


class TextEntry:
    author: str
    timestamp: "Timestamp"
    period: "Period"
    text: str


class Timestamp:
    pass


class Period:
    pass
