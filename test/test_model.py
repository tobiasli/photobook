"""Testing specific parsing of diary files."""
import os

from diary import parse_model
from photobook.text import readers
from photobook.text.parsing import FileFinder

FILENAME = os.path.join(os.path.split(__file__)[0], 'bin', 'context.md')


def test_diary_text():
    file = FileFinder(sub_content_finders=[parse_model.ENTRY_FINDER])

    stream = readers.TextStream(reader=readers.FileReader(filepath=FILENAME, encoding='utf-8'))
    c = file.parse_file(stream=stream)

    assert len(c.contents) == 3
    assert c.contents[1].text == 'Consitution day was a blast!\r'
