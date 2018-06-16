from photobook import photos

def test_photos():
    img = photos.PhotoCollection.load(r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg")

    assert len(img) == 4
    assert isinstance(img[0], photos.Photo)
    assert [i.orientation for i in img] == ['Rotated 90 CW', 'Rotated 90 CW', 'Rotated 180', 'Rotated 180']

    # Check translation of orientation into latex:
    assert img[0].orientation_translator('Rotated 90 CW') == 'angle=270'
    assert img[0].orientation_translator('Rotated 180') == 'angle=180'

    correct_latex = r'''\begin{figure}[h!]%
\includegraphics[width=400px,angle=270]{E:\Dropbox\Tobias\Programming\photobook\test\bin\{2018-01-19_08.39.51}.jpg}%
\end{figure}%'''
    assert img[0].latex == correct_latex