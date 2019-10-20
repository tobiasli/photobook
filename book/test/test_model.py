"""Test model components of old."""
from book import model as m


def test_title_construction():
    obj = m.Title('test')
    assert obj.text == 'test'


def test_text_construction():
    obj = m.Text('test')
    assert obj.text == 'test'


def test_image_construction():
    obj = m.Image('test')
    assert obj.path == 'test'


def test_chapter_construction():
    obj = m.Chapter(title=m.Title('test'), text=m.Text('This is a test'), images=[m.Image('filepath.jpg')])
    assert obj.title.text == 'test'
    assert obj.text.text == 'This is a test'
    assert obj.images[0].path == 'filepath.jpg'


def test_book_construction():
    obj = m.Book(title=m.Title('test'))
    assert obj.title.text == 'test'
