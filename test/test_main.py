from datetime import datetime
from photobook import main as photos

def test_Period():
    period1 = photos.Period(datetime(2018, 1, 1), datetime(2018, 2, 1))
    period2 = photos.Period(datetime(2018, 1, 15), datetime(2018, 2, 15))
    period3 = photos.Period(datetime(2018, 3, 1), datetime(2018, 4, 1))

    periodA = period1+period2
    assert periodA.start == datetime(2018, 1, 1) and periodA.end == datetime(2018, 2, 15)

    periodB = period2 + period3
    assert periodB.start == datetime(2018, 1, 15) and periodB.end == datetime(2018, 4, 1)

def test_Photobook():
    book = photos.Photobook(photo_store=r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg", text_store=r'E:\Dropbox\Tobias\Programming\photobook\test\bin\context.md')
    assert len(book.photos.photos) == 4

    # Check chapters:
    assert book.chapters[0].period == [datetime(2018, 1, 1), datetime(2018, 3, 2)]
    assert book.chapters[1].period == [datetime(2018, 4, 8, 9, 24, 0), datetime(2018, 4, 8, 9, 24, 0)]
    assert book.chapters[2].period == [datetime(2018,5,17), datetime(2018,5,18)]
    assert book.chapters[2].period == [datetime(2018,5,31), datetime(2018,6,1)]


    pdf_name = ''
    # book.generate_pdf2(path=r'E:\Dropbox\Tobias\Programming\photobook\test\output\test_main_pylatex', title=pdf_name)
    # book.generate_pdf(path=r'E:\Dropbox\Tobias\Programming\photobook\test\output\test_main', title=pdf_name)
    book.generate_pdf_from_chapters(path=r'E:\Dropbox\Tobias\Programming\photobook\test\output\test_main', title=pdf_name)

    #shutil.rmtree(os.path.join(pdf_path, pdf_name+'.pdf'))
    pass


def test_photos():
    img = photos.PhotoCollection.load(r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg")

    assert len(img) == 4
    assert isinstance(img[0], photos.Photo)
    assert [i.orientation for i in img] == ['Rotated 90 CW', 'Rotated 90 CW', 'Rotated 180', 'Rotated 180']

    # Check translation of orientation into latex:
    assert img[0].orientation_translator('Rotated 90 CW') == 'angle=270'
    assert img[0].orientation_translator('Rotated 180') == 'angle=180'

    correct_latex = r'''\begin{figure}[!h]%
\includegraphics[width=200px,angle=270]{E:/Dropbox/Tobias/Programming/photobook/test/bin/{2018-01-19-08.39.51}.jpg}%
\end{figure}%'''
    assert img[0].latex == correct_latex

def test_PhotoCollection():
    collection = photos.PhotoCollection(r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg")

    assert [i.filepath for i in collection.get_photos_from_period([datetime(2018, 1, 1, 0, 0), datetime(2018, 3, 2, 0, 0)])] == ['E:\\Dropbox\\Tobias\\Programming\\photobook\\test\\bin\\2018-01-19-08.39.51.jpg', 'E:\\Dropbox\\Tobias\\Programming\\photobook\\test\\bin\\2018-02-28-09.12.22.jpg']


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

    text = photos.Text(match)

    assert text.__dict__() == result


def test_TextCollection():
    file = r'E:\Dropbox\Tobias\Programming\photobook\test\bin\context.md'

    collection = photos.TextCollection(file)

    assert collection.get_text_for_timestamp(datetime(2018, 2, 1, 0, 0, 0))[
               0].text == 'It was a really, really cold winter. Everything was covered in deep, white snow for months. Most winters were dark, but because of all the snow, this winter was bright and crisp and clean.'

    assert collection[1] in collection
    assert not photos.Text(['# 20.11.2015 12:20 Tobias', '* 13.11.13', 'This text is not in collection']) in collection