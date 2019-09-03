"""Tests for the model compontents of the photo book."""
import re

import photobook.model as model
import photobook.readers as readers

SIMPLE_TEXT = """This is a test.
# this is content
¤ this is not
fin"""

NESTED_TEXT = """

# This is a title.
This is contents.
And some more.

## This is a subtitle.
with subtitle contents.

# This is another title.
With some contents.

"""


def test_text_stream_previous():
    stream = readers.TextStream(reader=readers.StringReader(string=SIMPLE_TEXT))

    assert stream.get_line() == 'This is a test.'
    assert stream.get_line() == '# this is content'
    assert stream.get_previous_line() == 'This is a test.'
    stream.get_line()
    assert stream.get_line() is not None
    assert stream.get_line() is None  # End of file.


def test_text_stream_backtrack():
    stream = readers.TextStream(reader=readers.StringReader(string=SIMPLE_TEXT))

    assert stream.get_line() == 'This is a test.'
    assert stream.get_line() == '# this is content'
    assert stream.get_line() == '¤ this is not'
    assert stream.get_line() == 'fin'
    stream.backtrack_reader_number_of_lines(2)
    assert stream.get_line() == '¤ this is not'
    assert stream.get_line() == 'fin'
    assert stream.get_previous_line() == '¤ this is not'


def test_content_finder_simple():
    stream = readers.TextStream(reader=readers.StringReader(string=SIMPLE_TEXT))

    c = model.ContentFinder(start_pattern=re.compile('^#(?P<stuff>.+)$'),
                            end_pattern=re.compile('^¤'))

    content = c.search_stream(stream)

    assert content.stuff == ' this is content'


def test_content_finder_nested():
    class Text(model.Content):
        pass

    class Title(model.Content):
        pass

    class SubTitle(model.Content):
        pass

    text_match = re.compile('^(?P<text>[^#].+)$')
    title_match = re.compile('^# ?(?P<title>[^#].+)$')
    subtitle_match = re.compile('^## ?(?P<subtitle>[^#].+)$')
    stream = readers.TextStream(reader=readers.StringReader(string=NESTED_TEXT))

    text_finder = model.ContentFinder(start_pattern=text_match,
                                      content_type=Text)
    subtitle_finder = model.ContentFinder(start_pattern=subtitle_match,
                                          content_type=SubTitle,
                                          sub_content_finders=[text_finder]
                                          )
    title_finder = model.ContentFinder(start_pattern=title_match,
                                       content_type=Title,
                                       sub_content_finders=[subtitle_finder, text_finder])

    file_finder = model.FileFinder(sub_content_finders=[title_finder])

    file = file_finder.parse_file(stream)
    # TODO: Figure out why i can't find subtitles.
    assert file.get_contents_by_type(SubTitle)[0].subtitle == 'This is a subtitle.'
    assert file.get_contents_by_type(SubTitle)[0].contents[0].text == 'with subtitle contents.'
