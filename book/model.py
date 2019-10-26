import typing as ty
from datetime import datetime
import os
import tregex
import math
import tempfile
from shutil import copyfile

from exifread import process_file
from PIL import Image as PILImage

import pylatex as pl

Number = ty.Union[int, float]


class MyRandomSequence(tempfile._RandomNameSequence):
    """Create a custom character set for tempfile"""
    characters = "abcdefghijklmnopqrstuvwxyz1234567890"


tempfile._name_sequence = MyRandomSequence()


def create_latex_path(path: str) -> str:
    """Latex paths for includegraphics need forward slashes instead of windows native backward slashes."""
    # Use curly brackets to scape excess dots in name.
    # directory, filename = os.path.split(path)
    # file, ext = os.path.splitext(filename)
    # path = f'"{{{directory}/{file}}}{ext}"'
    path = path.replace('\\', '/')
    # path = path.replace("_", "\_")
    return path




class Title:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class Text:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class Image:
    get_tags = {
        'EXIF DateTimeOriginal': 'timestampstr',
        'Image XResolution': 'width',
        'Image YResolution': 'height',
        'EXIF ExifImageWidth': 'width',
        'EXIF ExifImageLength': 'height',
        'Image Orientation': 'orientation'
    }
    path: str
    directory: str
    timestampstr: str
    width: Number
    height: Number
    orientation: str

    def __init__(self, path) -> None:
        self.path: str = path
        self.directory, file = os.path.split(path)
        self.filename, file_extension = os.path.splitext(file)
        self.file_extension = file_extension.lower()
        self.image = PILImage.open(path)
        self.exif = process_file(open(path, 'rb'))
        for tag in self.get_tags:
            if tag in self.exif:
                setattr(self, self.get_tags[tag], str(self.exif[tag]))
            else:
                setattr(self, self.get_tags[tag], None)

        self.temp_copy_path = None

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
    def orientation_latex(self) -> str:
        """Return orientation as a latex argument."""
        return self.orientation_translator(self.orientation)

    @property
    def orientation_numeric(self) -> Number:
        """Return orientation as a degree from 0 to 360."""
        return self.orientation_lookup(self.orientation)['angle']

    def orientation_translator(self, orientation):
        orientation = self.orientation_lookup(orientation)
        latex = 'angle={:d}'
        direction_lookup = {'CW': lambda x: 360 - x, 'CCW': lambda x: x, None: lambda x: x}
        if orientation:
            return latex.format(direction_lookup[orientation['direction']](orientation['angle']))
        else:
            return ''

    def orientation_lookup(self, orientation):
        if not orientation:
            return {'angle': 0, 'direction': 'CW'}

        match = tregex.to_dict('(?:Rotated)? (?P<angle>\d+(?:.\d+)?) ?(?P<direction>\w+)?', orientation)
        if not match:
            return {}
        else:
            return {'angle': int(match[0]['angle']), 'direction': match[0]['direction']}

    @property
    def path_latex(self) -> str:
        """Create a latex valid file path"""
        return create_latex_path(self.path)

    @property
    def timestamp(self) -> datetime:
        return datetime.strptime(self.timestampstr, '%Y:%m:%d %H:%M:%S')

    @property
    def shape(self) -> str:
        """Return a simple 'portrait', 'landscape' or 'square' depending on the images actual orientation"""

        shift = {'portrait': 'landscape', 'landscape': 'portrait', 'square': 'square'}

        if self.width == self.height:
            shape = 'square'
        elif self.width > self.height:
            shape = 'landscape'
        else:  # self.width < self.height:
            shape = 'portrait'

        orientation = self.orientation_lookup(self.orientation)
        if not orientation:
            shift_from_original = 0
        else:
            shift_from_original = math.fmod(orientation['angle'], 180)

        if shift_from_original:
            shape = shift[shape]

        return shape

    def create_temp_copy(self):
        """Create a tempfile copy of the image to clean up any naming issues with the image file."""
        self.cleanup_temp_copy()

        self.temp_copy_path = tempfile.NamedTemporaryFile(
            prefix='bookimage'+self.timestamp.strftime('%Y%m%d%H%M%S'),
            suffix=self.file_extension).name
        copyfile(self.path, self.temp_copy_path)

    def get_temp_copy_path(self) -> str:
        """Return the path to the temp copy file."""
        return create_latex_path(self.temp_copy_path)

    def cleanup_temp_copy(self) -> None:
        """Delete the temp copy file."""
        if self.temp_copy_path:
            if os.path.exists(self.temp_copy_path):
                os.remove(self.temp_copy_path)
            self.temp_copy_path = None



class Chapter:
    def __init__(self, *, title: Title, text: Text, images: ty.Sequence[Image]) -> None:
        """A chapter contains a title, text and may contain images."""
        self.title = title
        self.text = text
        self.images = images


class Book:
    chapters: ty.List[Chapter]

    def __init__(self, *, title: Title) -> None:
        """A book contains a title and one or more chapters."""
        self.title = title
        self.chapters = list()

    def add_chapters(self, chapters: ty.Sequence[Chapter]) -> None:
        """Add chapters to book."""
        self.chapters.extend(chapters)

    @property
    def images(self) -> ty.List[Image]:
        """Return a list of all images from all chapters."""
        return [image for chapter in self.chapters for image in chapter.images]

    def temp_cleanup(self) -> None:
        """Delete all temporary files generated."""
        for image in self.images:
            image.cleanup_temp_copy()
