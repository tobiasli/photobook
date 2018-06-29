from typing import List

from photobook.main import PhotoCollection, TextCollection, Photo

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

    def __init__(self, height: float, width: float, unit: str,
                 margins: float = None, left_margin: float = None, right_margin: float = None, top_margin: float = None,
                 bottom_margin: float = None,
                 spacing: float = 0, image_crop_tolerance: float = 0.2) -> None:
        self.height = height
        self.width = width
        self.unit = unit
        self.margins = margins
        if not isinstance(margins, type(None)):
            left_margin = right_margin = top_margin = bottom_margin = margins
        if all([isinstance(margin, type(None)) for margin in
                [margins, left_margin, right_margin, bottom_margin, top_margin]]):
            raise TypeError('When no catch-all margins is set, you must define left/right/top/bottom_margin.')
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.spacing = spacing
        self.image_crop_tolerance = image_crop_tolerance

    def width_division(self, divisions) -> float:
        return (self.width - self.left_margin - self.right_margin) / divisions

    def height_division(self, divisions) -> float:
        return (self.height - self.top_margin - self.bottom_margin) / divisions


class TemplateLibrary:
    def __init__(self, page_width: int, page_height: int) -> None:
        self.page_width = page_width
        self.page_height = page_height


class Template:
    accepts = []

    def __init__(self, page, photos: PhotoCollection = None, text: TextCollection = None) -> None:
        assert self.accepts == [photo.shape for photo in photos]
        self.page = page
        self.photos = photos
        self.text = text

    def fit_photo_to_page(self, *, photo: Photo, forced_width: float=None, forced_height: float=None) -> str:
        # Ok, so we have an image. This image is shorter than page height when the width is given (i.e. 1/3 of page width.
        # This can be calculated quite easily by width*photo_width = height*photo_height => height = width*photo_width/photo_height
        # If height is less than image height, we need to crop the sides of the image by a factor of:
        # factor = page_height/photo_height
        # This factor must be less than page.image_crop_tolarence
        # The output must be a set of distances pr edge in page units.
        assert forced_height or forced_width

        pass

    @staticmethod
    def wrap(lines: List[str], name: str, args: List[str] = None, additional_commands: List[str]=None) -> List[str]:
        if args:
            arg_format = f'[{",".join(args)}]'
        else:
            arg_format = ''
        if additional_commands:
            for command in reversed(additional_commands):
                lines.insert(0, f'\\{command}')

        lines.insert(0, f'\\begin{{{name}}}' + arg_format)
        lines.append(f'\\end{{{name}}}')
        return lines


class L3P(Template):  # Landscape page, 3 Portraits
    # TODO: Get this working according to the last page of album_test_modify.tex
    accepts = ['portrait', 'portrait', 'portrait']

    def latex(self) -> str:
        image_width_str = f'{self.page.width_division(3):n}{self.page.unit}'
        lines = []
        for photo, place in zip(self.photos, ['east', 'center', 'west']):
            lines.append(
                f'\\node[anchor={place}] at (current page.{place})' + f'{{\\resizebox{{{image_width_str}}}{{!}}' + f'{{{photo.includegraphics_latex}}}}};')

        self.wrap(lines, name='tikzpicture', args=['remember picture', 'overlay'])
        self.wrap(lines, name='center')
        self.wrap(lines, name='slide', additional_commands=['small'])
        lines.append('\clearpage')

        return '\n'.join(lines)
