"""Testing specific parsing of diary files."""
import os
import pytest
import datetime

from diary import parsing_definition
from parsing import readers
from parsing.parsing import Parser, Content

FILENAME = os.path.join(os.path.split(__file__)[0], 'bin', 'context.md')


@pytest.fixture()
def model() -> Content:
    # Get the text stream we want to parse:
    stream = readers.TextStream(reader=readers.FileReader(filepath=FILENAME, encoding='utf-8'))

    # Get the model that the contents of stream should match:
    parser = Parser(finders=[parsing_definition.ENTRY_FINDER])

    # Use model to parse stream:
    c = parser.parse_stream(stream=stream)
    return c


def test_basic_structure(model):
    assert len(model.contents) == 3
    assert model.contents[1].text == 'Constitution day was a blast!\r'


def test_timestamp(model):
    entry = model.get_contents_by_type(parsing_definition.Entry)[0]
    assert isinstance(entry.timestamp, str)
    assert entry.timestamp == datetime.datetime(2018, 6, 16, 21, 00, 00)


def test_period(model):
    """This entry does not have a specified time period, so the timestamp is floored and padded with 24 hours."""
    entry = model.get_contents_by_type(parsing_definition.Entry)[2]
    assert entry.period[0] == datetime.datetime(2018, 6, 16)
    assert entry.period[1] == datetime.datetime(2018, 6, 17)

