import typing as ty
from datetime import datetime
import os
import tregex
import math

from exifread import process_file
from PIL import Image as PILImage

import pylatex as pl

Number = ty.Union[int, float]


def create_latex_path(path: str) -> str:
    """Latex paths for includegraphics need forward slashes instead of windows native backward slashes."""
    # Use curly brackets to scape excess dots in name.
    directory, filename = os.path.split(path)
    file, ext = os.path.splitext(filename)
    path = f'{{{directory}/{file}}}{ext}'
    path = path.replace("_", "\_")
    path = path.replace('\\', '/')
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
    get_tags = {'EXIF DateTimeOriginal': 'timestampstr',
                'EXIF ExifImageWidth': 'width',
                'EXIF ExifImageLength': 'height',
                'Image Orientation': 'orientation'}
    path: str
    directory: str
    timestampstr: str
    width: Number
    height: Number
    orientation: str

    def __init__(self, path) -> None:
        self.path: str = path
        self.directory, file = os.path.split(path)
        self.filename, self.file_extension = os.path.splitext(file)
        self.image = PILImage.open(path)
        self.exif = process_file(open(path, 'rb'))
        for tag in self.get_tags:
            assert tag in self.exif
            setattr(self, self.get_tags[tag], str(self.exif[tag]))

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
    def path_latex(self):
        """Create a latex valid file path"""
        return create_latex_path(self.path)

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

    def __init__(self, *, title: Title) -> None:
        """A book contains a title and one or more chapters."""
        self.title = title
        self.chapters = list()

    def add_chapters(self, chapters: ty.Sequence[Chapter]) -> None:
        """Add chapters to book."""
        self.chapters.extend(chapters)

    @staticmethod
    def _create_doc(path: str = None) -> pl.Document:
        """Create a working Document from Book structure."""
        doc = pl.Document(documentclass='book', document_options=['a4paper', '11pt'])
        doc.packages.append(pl.Package('graphicx'))
        return doc

    def _add_preamble(self, doc: pl.Document) -> pl.Document:
        """Add preamble."""
        doc.preamble.append(pl.Command('title', 'Awesome Title'))
        doc.preamble.append(pl.Command('author', 'Anonymous author'))
        doc.preamble.append(pl.Command('date', pl.NoEscape(r'\today')))
        doc.append(pl.NoEscape(r'\maketitle'))
        return doc

    @staticmethod
    def _add_chapters_to_doc(doc: pl.Document, chapters: ty.Sequence[Chapter]) -> pl.Document:
        """Add Chapters to book as Sections."""
        for chapter in chapters:
            doc.create(pl.Section(chapter.title.text))
            doc.append(chapter.text.text)
            for i, image in enumerate(chapter.images):
                with doc.create(pl.Figure(position='h!')) as figure:
                    figure.add_image(image.path)#, width='400px')
                    # figure.add_caption(f'Image nr {i} taken {image.timestampstr}')
        return doc

    def _export_doc(self, doc: pl.Document, path: str) -> None:
        """Export pdf document of book."""
        doc.generate_pdf(path)
        doc.generate_tex(path)


    def _create_tex(self, doc):
        print('Generating latex!')
        with doc.create(Section('The year 2018')):
            doc.append('Here are some cool images from 2018!')
            for i, image in enumerate(self.photos.photos):
                with doc.create(Figure(position='h!')) as figure:
                    figure.add_image(image.filepath, width='400px')
                    figure.add_caption(f'Image nr {i} taken {image.timestampstr}')
        return doc