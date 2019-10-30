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


def test_image_sequence():
    files = glob.glob(os.path.join(FILEPATH, '*.jpg'))
    images = [m.Image(file) for file in files]
    m.ImageSequence(images=images)


def test_chapter_construction():
    images = [m.Image(file) for file in glob.glob(os.path.join(FILEPATH, '*.jpg'))]
    im_1 = m.ImageSequence(images[:2])
    im_2 = m.ImageSequence(images[2:])
    t_1 = m.Text('This is the first section.')
    t_2 = m.Text('And we have a second one.')
    obj = m.Chapter(title=m.Title('test'),
                    contents=[t_1, im_1, t_2, im_2])
    assert obj.title.text == 'test'
    assert obj.text[0].text == 'This is the first section.'
    assert os.path.split(obj.images[0].images[0].path)[1] == '2018-01-19-08.39.51.jpg'


def test_book_construction():
    obj = m.Book(title=m.Title('test'))
    assert obj.title.text == 'test'


def test_book_chapter():
    chap = m.Chapter(title=m.Title('test'),
                     contents=[m.Text('This is a test'), m.ImageSequence([m.Image(i) for i in glob.glob(os.path.join(FILEPATH, '*.jpg'))])])
    book = m.Book(title=m.Title('test'))

    book.add_chapters([chap, chap, chap])

    assert len(book.chapters) == 3
    assert len(book.images) == 12
