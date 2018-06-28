from typing import List

from photobook.main import PhotoCollection, TextCollection

"""
Templates take a set of photos and text and create a page layout. 

A template contains resize boxes located at nodes, and these resize-boxes can contain either text or images.

The contents of a template can therefore either be a set of images with matching shapes or just the right number of 
texts.

"""


class Template:
    height = None
    width = None
    margins = None
    left_margin = margins
    right_margin = margins
    top_margin = margins
    bottom_margin = margins
    spacing = None

    image_crop_tolarence = 0.2  # 0.2 means that it tolerates 20% crop in either length or width to fit a template.

    def __init__(self, height: float, width: float,
                 margins: float, left_margin: float, right_margin: float, top_margin: float, bottom_margin: float,
                 spacing: float, image_crop_tolerance: float, photos: PhotoCollection = None, text: TextCollection = None, ) -> None:
        self.photos = photos
        self.text = text
        self.height = height
        self.width = width
        self.margins = margins
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.spacing = spacing
        self.image_crop_tolerance = image_crop_tolerance

    def width_division(self, divisions) -> float:
        return (self.width-self.left_margin-self.right_margin)/divisions

    def height_division(self, divisions) -> float:
        return (self.width - self.top_margin - self.bottom_margin) / divisions


class TemplateLibrary:
    def __init__(self, page_width: int, page_height: int) -> None:
        self.page_width = page_width
        self.page_height = page_height

    def find_matching_template(self, shapes: List[str]) -> Template:
        pass

    class L3P(Template):  # Landscape page, 3 Portraits
        # TODO: Get this working according to the last page of album_test_modify.tex
        pass
