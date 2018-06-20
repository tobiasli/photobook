from photobook.text import Text, TextCollection
from datetime import datetime


def test_Text():
    match = """16.06.2018 21:00 Tobias
====================

* 01.01.2018-01.03.2018

It was a really, really cold winter. Everything was covered in deep, white snow for months. Most winters were dark, but because of all the snow, this winter was bright and crisp and clean."""

    result = {
        'timestamp': datetime(2018, 6, 16, 21, 0, 0),
        'author': 'Tobias',
        'period': [datetime(2018, 1, 1, 0, 0, 0), datetime(2018, 3, 2, 0, 0, 0)],
        'text': 'It was a really, really cold winter. Everything was covered in deep, white snow for months. Most winters were dark, but because of all the snow, this winter was bright and crisp and clean.'}

    text = Text(match)

    assert text.__dict__() == result


def test_TextCollection():
    file = r'E:\Dropbox\Tobias\Programming\photobook\test\bin\context.md'

    collection = TextCollection(file)

    assert collection.get_text_for_timestamp(datetime(2018, 2, 1, 0, 0, 0))[
               0].text == 'It was a really, really cold winter. Everything was covered in deep, white snow for months. Most winters were dark, but because of all the snow, this winter was bright and crisp and clean.'

    assert collection[1] in collection
    assert not Text(['# 20.11.2015 12:20 Tobias', '* 13.11.13', 'This text is not in collection']) in collection
