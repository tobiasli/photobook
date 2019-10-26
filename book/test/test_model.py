"""Test model components of old."""
import os
import glob
from tempfile import NamedTemporaryFile

import pylatex as pl

from book import model as m

FILEPATH = os.path.join(os.path.split(__file__)[0], 'bin')


def test_title_construction():
    obj = m.Title('test')
    assert obj.text == 'test'


def test_text_construction():
    obj = m.Text('test')
    assert obj.text == 'test'


def test_image_construction():
    imagefile = glob.glob(os.path.join(FILEPATH, '*.jpg'))[0]
    obj = m.Image(imagefile)
    assert obj.timestampstr == '2018:01:19 08:39:51'


def test_chapter_construction():
    obj = m.Chapter(title=m.Title('test'),
                    text=m.Text('This is a test'),
                    images=[m.Image(i) for i in glob.glob(os.path.join(FILEPATH, '*.jpg'))])
    assert obj.title.text == 'test'
    assert obj.text.text == 'This is a test'
    assert os.path.split(obj.images[0].path)[1] == '2018-01-19-08.39.51.jpg'


def test_book_construction():
    obj = m.Book(title=m.Title('test'))
    assert obj.title.text == 'test'


def test_book_chapter():
    chap = m.Chapter(title=m.Title('test'),
                    text=m.Text('This is a test'),
                    images=[m.Image(i) for i in glob.glob(os.path.join(FILEPATH, '*.jpg'))])
    book = m.Book(title=m.Title('test'))

    book.add_chapters([chap, chap, chap])

    assert len(book.chapters) == 3
    assert len(book.images) == 12


