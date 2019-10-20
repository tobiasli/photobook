import typing as ty
from datetime import datetime
import os
import tregex
import math

from exifread import process_file
from PIL import Image as PILImage


class Title:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class Text:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class Image:
    get_tags = {'EXIF DateTimeOriginal': 'timestampstr',
                'EXIF ExifImageWidth': 'width',
                'EXIF ExifImageLength': 'height',
                'Image Orientation': 'orientation'}

    dict_properties = ['filepath', 'width', 'height', 'orientation', 'timestamp']

    def __init__(self, path) -> None:
        self.path = path
        self.directory, file = os.path.split(path)
        self.filename, self.file_extension = os.path.splitext(file)
        self.image = PILImage.open(path)
        self.exif = process_file(open(path, 'rb'))
        for tag in self.get_tags:
            assert tag in self.exif
            setattr(self, self.get_tags[tag], str(self.exif[tag]))

    @staticmethod
    def create_args(args):
        return

    @staticmethod
    def convert_latex_path(path):
        assert not '_' in path
        assert not ' ' in path
        return path.replace('\\', '/')

    @property
    def latex(self):
        begining = r'\begin{figure}[!h]%'
        end = r'\end{figure}%'
        latex = '\n'.join([begining, self.includegraphics_latex+';', end])
        return latex

    @property
    def includegraphics_latex(self) -> str:
        args = ','.join([arg for arg in [self.orientation_latex] if arg])
        includegraphics = f'\\includegraphics[{args}]{{{self.convert_latex_path(self.directory)}/{{{self.convert_latex_path(self.filename)}}}{self.file_extension}}}'
        return includegraphics

    @property
    def orientation_latex(self):
        return self.orientation_translator(self.orientation)

    def orientation_translator(self, orientation):
        orientation = self.orientation_lookup(orientation)
        latex = 'angle={:d}'
        direction_lookup = {'CW': lambda x: 360 - x, None: lambda x: x}
        if orientation:
            return latex.format(direction_lookup[orientation['direction']](orientation['angle']))
        else:
            return ''

    def orientation_lookup(self, orientation):
        match = tregex.to_dict('(?:Rotated)? (?P<angle>\d+(?:.\d+)?) ?(?P<direction>\w+)?', orientation)
        if not match:
            return {}
        else:
            return {'angle': int(match[0]['angle']), 'direction': match[0]['direction']}

    @property
    def filepath_latex(self):
        return (os.path.basename(self.directory)).replace("_", "\_");

    @property
    def timestamp(self):
        return datetime.strptime(self.timestampstr, '%Y:%m:%d %H:%M:%S')

    @property
    def shape(self) -> str:
        """Return a simple 'portrait', 'landscape' or 'square' depending on the images actual orientation"""

        shift = {'portrait': 'landscape', 'landscape': 'portrait', 'square': 'square'}

        if self.width == self.height:
            shape = 'square'
        elif self.width > self.height:
            shape = 'landscape'
        elif self.width < self.height:
            shape = 'portrait'

        orientation = self.orientation_lookup(self.orientation)
        if not orientation:
            shift_from_original = 0
        else:
            shift_from_original = math.fmod(orientation['angle'], 180)

        if shift_from_original:
            shape = shift[shape]

        return shape


class Chapter:
    def __init__(self, *, title: Title, text: Text, images: ty.Sequence[Image]) -> None:
        """A chapter contains a title, text and may contain images."""
        self.title = title
        self.text = text
        self.images = images


class Book:
    chapters: ty.List[Chapter]

    def __init__(self, *, title) -> None:
        """A book contains a title and one or more chapters."""
        self.title = title
        self.chapters = list()

    def add_chapters(self, chapters: ty.Sequence[Chapter]) -> None:
        """Add chapters to book."""
        self.chapters.extend(chapters)



