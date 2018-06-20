from photobook import photos
from datetime import datetime

def test_photos():
    img = photos.PhotoCollection.load(r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg")

    assert len(img) == 4
    assert isinstance(img[0], photos.Photo)
    assert [i.orientation for i in img] == ['Rotated 90 CW', 'Rotated 90 CW', 'Rotated 180', 'Rotated 180']

    # Check translation of orientation into latex:
    assert img[0].orientation_translator('Rotated 90 CW') == 'angle=270'
    assert img[0].orientation_translator('Rotated 180') == 'angle=180'

    correct_latex = r'''\begin{figure}[h!]%
\includegraphics[width=400px,angle=270]{E:/Dropbox/Tobias/Programming/photobook/test/bin/{2018-01-19-08.39.51}.jpg}%
\end{figure}%'''
    assert img[0].latex == correct_latex

def test_PhotoCollection():
    collection = photos.PhotoCollection(r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg")

    assert [i.filepath for i in collection.get_photos_from_period([datetime(2018, 1, 1, 0, 0), datetime(2018, 3, 2, 0, 0)])] == ['E:\\Dropbox\\Tobias\\Programming\\photobook\\test\\bin\\2018-01-19-08.39.51.jpg', 'E:\\Dropbox\\Tobias\\Programming\\photobook\\test\\bin\\2018-02-28-09.12.22.jpg']