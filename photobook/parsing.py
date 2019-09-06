"""This file contains the base classes used for representing photobook contents."""
import typing as ty
import re
import logging

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

    def _get_contents_by_type(self, t: ty.Type['Content']) -> ty.List['Content']:
        """From the current Content.contents, return a list of items matching type t."""
        return [c for c in self.contents if isinstance(c, t)]

    def get_contents_by_type(self, t: ty.Type['Content']) -> ty.List['Content']:
        """From the current Content.contents, return a list of items matching type t."""
        return self._get_contents_by_type(t) + [c for content in self.contents for c in content._get_contents_by_type(t)]


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

    def search_stream(self, stream: TextStream, rematch_on_start=False, stop_at_new_start=True) -> Content:
        """Start a sequential search through a text stream.

        Args:
            stream: The text information scanned for model contents.
            rematch_on_start: When the current ContentFinder finds a match for start at current line, do we want to
                re-evaluate the current line for the subcontent?
            stop_at_new_start: When encountering a new start_pattern before end_pattern is met, do we want to break
                or just continue parsing?
        """
        content = None
        while True:
            line = stream.get_line()
            if line is None:
                break
            else:
                if not content:
                    if self.start_pattern.match(line):

                        logging.info(f'{self.content_type} matched "{line}"')
                        properties = next(self.start_pattern.finditer(line)).groupdict()
                        content = self.content_type(**properties)
                        if not self.sub_content_finders:
                            # If there are no nested levels below this Content, we are done!
                            break
                        if rematch_on_start:
                            stream.backtrack_reader_number_of_lines(1)  # If rematch_on_start, reset pointer to read last line again.
                else:
                    if self.end_pattern and self.end_pattern.match(line):
                        # We are done here!
                        break
                    elif self.sub_content_finders:  # We now go looking for sub_content.
                        for sub in self.sub_content_finders:
                            if sub.start_pattern.match(line):
                                # Backtrack stream to reevaluate current line, and send the stream into the sub_finder
                                # that matched.
                                stream.backtrack_reader_number_of_lines(1)
                                sub_content = sub.search_stream(stream)
                                content.add_content(sub_content)
                    elif stop_at_new_start and self.start_pattern.match(line):
                        # Assumes that reaching a start_pattern again means end of current ant start of new.
                        # So we are done here, and need to parse current line again.
                        # Only works if no end-pattern is set.
                        stream.backtrack_reader_number_of_lines(1)
                        break

        return content


class File(Content):
    """Simplest possible content for the data in an entire file."""


class FileFinder(ContentFinder):
    """Content finder for matching the entire contents of a File."""

    def __init__(self, sub_content_finders: ty.Optional[ty.Sequence["ContentFinder"]] = None) -> None:
        super(FileFinder, self).__init__(start_pattern=re.compile('^.'),
                                         content_type=File,
                                         sub_content_finders=sub_content_finders)

    def parse_file(self, stream: TextStream) -> Content:
        """Given a specific TextStream, parse the contents according to the given sub_content_finders of this particular
        file."""
        return self.search_stream(stream=stream, rematch_on_start=True, stop_at_new_start=False)


class TextEntry:
    author: str
    timestamp: "Timestamp"
    period: "Period"
    text: str


class Timestamp:
    pass


class Period:
    pass
