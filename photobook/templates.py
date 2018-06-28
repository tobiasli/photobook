from typing import List

from photobook.main import PhotoCollection, TextCollection

"""
Templates take a set of photos and text and create a page layout. 

A template contains resize boxes located at nodes, and these resize-boxes can contain either text or images.

The contents of a template can therefore either be a set of images with matching shapes or just the right number of 
texts.

"""


class Page:
    height = None
    width = None
    margins = None
    left_margin = margins
    right_margin = margins
    top_margin = margins
    bottom_margin = margins
    spacing = None

    image_crop_tolarence = 0.2  # 0.2 means that it tolerates 20% crop in either length or width to fit a template.

    def __init__(self, height: float, width: float, unit:str,
                 margins: float=None, left_margin: float=None, right_margin: float=None, top_margin: float=None, bottom_margin: float=None,
                 spacing: float=0, image_crop_tolerance: float=0.2) -> None:
        self.height = height
        self.width = width
        self.unit = unit
        self.margins = margins
        if not isinstance(margins, type(None)):
            left_margin=right_margin=top_margin=bottom_margin=margins
        if all([isinstance(margin, type(None)) for margin in [margins, left_margin, right_margin, bottom_margin, top_margin]]):
            raise TypeError('When no catch-all margins is set, you must define left/right/top/bottom_margin.')
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.spacing = spacing
        self.image_crop_tolerance = image_crop_tolerance

    def width_division(self, divisions) -> float:
        return (self.width-self.left_margin-self.right_margin)/divisions

    def height_division(self, divisions) -> float:
        return (self.height - self.top_margin - self.bottom_margin) / divisions


class TemplateLibrary:
    def __init__(self, page_width: int, page_height: int) -> None:
        self.page_width = page_width
        self.page_height = page_height


class Template:
    def __init__(self, page, photos:PhotoCollection=None, text: TextCollection=None) -> None:
        self.page = page
        self.photos = photos
        self.text = text


class L3P(Template):  # Landscape page, 3 Portraits
    # TODO: Get this working according to the last page of album_test_modify.tex

    def latex(self) -> str:
        lines = []
        lines.extend([r'\begin{slide}% vertically center', r'\small', r'\begin{center}'])
        lines.extend([r'\begin{tikzpicture}[remember picture,overlay]'])
        for photo, place in zip(self.photos, ['east', 'center', 'west']):
            # match = r'\node[anchor=east] at (current page.east){\resizebox{2cm}{!}{\includegraphics[angle=270]{E:/Dropbox/Tobias/Programming/photobook/test/bin/{2018-01-19-08.39.51}.jpg}}};'
            lines.append(rf'\node[anchor={place}] at (current page.{place})' + r'{\resizebox{2cm}{!}' + r'{' + photo.includegraphics_latex + r'}};')
        lines.extend([r'\end{tikzpicture}'])
        lines.extend([r'\end{center}', r'\end{slide}'])

        return '\n'.join(lines)
