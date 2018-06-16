from photobook.text import Text
from datetime import datetime


def test_Text():
    match = """16.06.2018 21:00 Tobias
====================

* 01.01.2018-01.03.2018

It was a really, really cold winter. Everything was covered in deep, white snow for months. Most winters were dark, but because of all the snow, this winter was bright and crisp and clean."""

    result = {
        'timestamp': datetime(2018, 6, 16, 21, 0, 0),
        'author': 'Tobias',
        'content_dates': [datetime(2018, 1, 1, 0, 0, 0), datetime(2018, 3, 1, 23, 59, 59)],
        'content': 'It was a really, really cold winter. Everything was covered in deep, white snow for months. Most winters were dark, but because of all the snow, this winter was bright and crisp and clean.'}

    text = Text(match)

    assert text.__dict__ == result
