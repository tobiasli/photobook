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
    assert os.path.split(obj.images[0].path)[1] == 'image.jpg'


def test_book_construction():
    obj = m.Book(title=m.Title('test'))
    assert obj.title.text == 'test'


def test_book_create_doc():
    obj = m.Book(title=m.Title('test'))
    doc = obj._create_doc('somepath')
    assert isinstance(doc, m.pl.Document)


def test_book_add_preable_doc():
    obj = m.Book(title=m.Title('test'))
    doc = obj._create_doc('somepath')
    doc = obj._add_preamble(doc)
    assert isinstance(doc, m.pl.Document)


def test_book_create_simple_pdf():
    obj = m.Book(title=m.Title('test'))
    doc = obj._create_doc()
    doc = obj._add_preamble(doc)

    filename = NamedTemporaryFile().name
    obj._export_doc(doc, filename)
    print(filename)


def test_book_create_pdf():
    obj = m.Book(title=m.Title('test'))
    doc = obj._create_doc()
    doc = obj._add_preamble(doc)

    doc.append(pl.NewPage())

    with doc.create(pl.LongTabu("X[c] X[c]")) as cheque_table:
        cheque_file = m.create_latex_path(r'{E:\Dropbox\Tobias\Programming\photobook\diary\test\bin\2018-01-19-08.39.51}.jpg')
        cheque = pl.StandAloneGraphic(cheque_file, image_options="width=200px, angle=270")
        for i in range(0, 20):
            cheque_table.add_row([cheque, cheque])

    filename = NamedTemporaryFile().name
    obj._export_doc(doc, filename)
    pdf = filename+'.pdf'
    print(pdf)
    os.system(pdf)


