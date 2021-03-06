from photobook.templates import L3P, Page
from photobook import main as photobook

def test_L3P():
    photos = photobook.PhotoCollection(r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg")

    page = Page(height=12, width=24, unit='cm', margins=0)

    layout = L3P(page=page, photos=[photos[0], photos[1], photos[0]])

    result = layout.latex()

    match = r'''\begin{slide}
\small
\begin{center}
\begin{tikzpicture}[remember picture,overlay]
\node[anchor=east] at (current page.east){\resizebox{8cm}{!}{\includegraphics[angle=270]{E:/Dropbox/Tobias/Programming/photobook/test/bin/{2018-01-19-08.39.51}.jpg}}};
\node[anchor=center] at (current page.center){\resizebox{8cm}{!}{\includegraphics[angle=270]{E:/Dropbox/Tobias/Programming/photobook/test/bin/{2018-02-28-09.12.22}.jpg}}};
\node[anchor=west] at (current page.west){\resizebox{8cm}{!}{\includegraphics[angle=270]{E:/Dropbox/Tobias/Programming/photobook/test/bin/{2018-01-19-08.39.51}.jpg}}};
\end{tikzpicture}
\end{center}
\end{slide}
\clearpage'''

    # for r, m in zip(result.split('\n'), match.split('\n')):
    #     print(r)
    #     print(m)
    #     print('\n')

    # TODO: Make these match
    assert result == match

    print(result)