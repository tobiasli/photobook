from typing import List, Union
from datetime import datetime, timedelta
import os
import glob
from collections import Iterable
import math

from pylatex import Document, Section, Figure, NoEscape, Package
from exifread import process_file
from pylatex.utils import escape_latex
from PIL import Image

from diary.data_model import Period
from photobook import tregex
from photobook.dateparse import parse as dateparse


def parse(string: str) -> datetime:
    return dateparse(string, full_text=True)


class BookContent:
    contents = []
    dict_properties = []

    def __contains__(self, item) -> bool:
        match = True
        strings = [str(item) for item in self.contents]
        if isinstance(item, Iterable):
            for new_item in item:
                if not str(new_item) in strings:
                    match = False
            return match
        else:
            return str(item) in strings

    def __getitem__(self, key):
        return self.contents[key]

    def __iter__(self):
        for content in self.contents:
            yield content

    def __bool__(self) -> bool:
        return bool(self.contents)

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __dict__(self) -> dict:
        return {prop: getattr(self, prop) for prop in self.dict_properties}

    def __str__(self) -> str:
        return str(self.__dict__())


class Text(BookContent):
    dict_properties = ('written_date', 'text', 'period', 'author')

    def __init__(self, text: Union[List, str]) -> None:
        if isinstance(text, str):
            lines = text.split('\n')
        else:
            lines = text

        match = tregex.name('(?P<timestamp>\d.*\d) (?P<author>.*?)$', lines[0])[0]
        self.written_date = parse(match['timestamp'])
        self.author = match['author']

        contents = []
        found_contents_dates = False
        for line in lines:
            line = line.strip('\r\n')
            if line and line[0] == '*':
                line = line.replace('*', '').strip()
                if len(line) > 10:
                    dates = line.split('-')
                else:
                    dates = [line, line]

                datetimes = [parse(date) for date in dates]
                # We define end-include by adding a day:
                datetimes[1] = datetimes[1] + timedelta(days=1)
                found_contents_dates = True
            elif found_contents_dates and line:
                contents += [line]

        if not found_contents_dates:
            datetimes = [self.timestamp, self.timestamp + timedelta(days=1)]

        self.period = Period(*datetimes)
        self.text = '\r\n'.join(contents)

    @property
    def text_escape(self) -> str:
        return escape_latex(self.text)

    @property
    def timestamp(self) -> datetime:
        return min(self.period)


class TextCollection:
    def __init__(self, text_files: Union[List, str] = None) -> None:
        self.text = []
        if isinstance(text_files, str):
            text_files = [text_files]
        if text_files:
            for file in text_files:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.readlines()
                    collection = []
                    for line in text:
                        if line[0] == '#':
                            # Finish previous collection and start new
                            if collection:
                                self.text.append(Text(collection))
                                collection = []
                        if line:
                            collection += [line]
            self.text.append(Text(collection))

    def __contains__(self, item: Union[Text, "TextCollection"]) -> bool:
        assert isinstance(item, (Text, TextCollection))
        match = True
        strings = self.strings
        if isinstance(item, TextCollection):
            for new_text in item.strings:
                if not new_text in strings:
                    match = False
            return match
        elif isinstance(item, Text):
            return str(item) in strings

    @property
    def strings(self):
        return [str(text) for text in self.text]

    def get_text_for_timestamp(self, timestamp: datetime) -> List[Text]:
        return [text for text in self.text if timestamp in text.period]

    def add_text(self, text: Union[Text, List[Text], "TextCollection"]) -> None:
        if not isinstance(text, Iterable):
            text = [text]
        self.text.extend(text)
        self.text = sorted(self.text, key=lambda x: x.period.start)

    def __getitem__(self, key):
        return self.text[key]

    def __iter__(self):
        for text in self.text:
            yield text

    def __bool__(self) -> bool:
        return bool(self.text)

    def __len__(self) -> int:
        return len(self.text)

    def __str__(self) -> str:
        return str(self.strings)

    def __add__(self, other) -> "TextCollection":
        assert isinstance(other, TextCollection)
        self.add_text(other)
        return self


class Photo(BookContent):
    get_tags = {'EXIF DateTimeOriginal': 'timestampstr',
                'EXIF ExifImageWidth': 'width',
                'EXIF ExifImageLength': 'height',
                'Image Orientation': 'orientation'}

    dict_properties = ['filepath', 'width', 'height', 'orientation', 'timestamp']

    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.path, file = os.path.split(filepath)
        self.filename, self.file_extension = os.path.splitext(file)
        self.image = Image.open(filepath)
        self.exif = process_file(open(filepath, 'rb'))
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
        includegraphics = f'\\includegraphics[{args}]{{{self.convert_latex_path(self.path)}/{{{self.convert_latex_path(self.filename)}}}{self.file_extension}}}'
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
        match = tregex.name('(?:Rotated)? (?P<angle>\d+(?:.\d+)?) ?(?P<direction>\w+)?', orientation)
        if not match:
            return {}
        else:
            return {'angle': int(match[0]['angle']), 'direction': match[0]['direction']}

    @property
    def filepath_latex(self):
        return (os.path.basename(self.path)).replace("_", "\_");

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


class PhotoCollection:
    def __init__(self, searches: List[str] = None):
        self.searches = searches

        self.photos = list()
        if searches:
            self.add_photos(self.load(searches))

    @staticmethod
    def load(searches: Union[List, str]) -> List[Photo]:
        # Get all images (.JPG and .jpg in this example)
        if isinstance(searches, str):
            searches = [searches]

        first = True
        for search in searches:
            if first:
                files = glob.glob(search)
                first = False
            else:
                files.extend(glob.glob(search))

        if not files:
            raise FileNotFoundError('No images where found with that search pattern.')

        images = []
        for file in files:
            images += [Photo(file)]

        return images

    def get_photos_from_period(self, period: Period) -> List[Photo]:
        """Get photos from a period. Start Include, end exclude."""
        assert isinstance(period, Period)
        return [image for image in self.photos if image.timestamp in period]

    def __getitem__(self, key):
        return self.photos[key]

    def __iter__(self):
        for photo in self.photos:
            yield photo

    def __bool__(self) -> bool:
        return bool(self.photos)

    def __len__(self) -> int:
        return len(self.photos)

    def add_photos(self, photos: Union[List[Photo], "PhotoCollection"]) -> None:
        self.photos.extend(photos)
        self.photos = sorted(self.photos, key=lambda x: x.timestamp)

    def __add__(self, other) -> "PhotoCollection":
        assert isinstance(other, PhotoCollection)
        self.add_photos(other)
        return self


class Chapter:
    def __init__(self, photos: List[Photo] = None, text: List[Text] = None) -> None:
        """A set of images and text for a specific time period that together make a chapter."""
        self.photos = PhotoCollection()
        self.text = TextCollection()

        if photos:
            self.add_photos(photos)
        if text:
            self.add_text(text)

    def add_photos(self, photos: Union[List[Photo], Photo, PhotoCollection]) -> None:
        assert isinstance(photos, (Iterable, Photo))
        if not isinstance(photos, Iterable):
            photos = [photos]
        self.photos.add_photos(photos)

    def add_text(self, text: Union[List[Text], Text, TextCollection]) -> None:
        assert isinstance(text, (Iterable, Text))
        if not isinstance(text, Iterable):
            text = [text]
        self.text.add_text(text)

    @property
    def period(self) -> Period:
        if self.text:
            periods = Period()
            for text in self.text:
                periods += text.period
            return periods
        elif self.photos:
            timestamps = [photo.timestamp for photo in self.photos]
            return Period(min(timestamps), max(timestamps))
        else:
            return Period()

    @property
    def timestamp(self) -> datetime:
        return min(self.period)

    def __bool__(self) -> bool:
        return bool(self.photos) or bool(self.text)

    def __str__(self) -> str:
        return f'<Chapter: {str(self.period)}: {len(self.text)} texts and {len(self.photos)} photos.>'

    def __repr__(self) -> str:
        return str(self)


class Photobook:  # ChapterCollection
    def __init__(self, photo_store: str, text_store: str = None) -> None:
        self.photos = PhotoCollection(photo_store)
        self.text = TextCollection(text_store)
        self.chapters = list()
        self.chapters_from_text_and_images()

    def show_contents(self) -> None:
        for chapter in self.chapters:
            print(chapter)

    def add_chapters(self, chapters: Union[List[Chapter], Chapter]) -> None:
        if not isinstance(chapters, list):
            chapters = [chapters]
        self.chapters.extend(chapters)
        self.chapters = sorted(self.chapters, key=lambda x: x.timestamp)

    def chapters_from_text_and_images(self) -> None:
        # Run through text and get all matching photos to create chapters.
        # Create chapters from photo-less text periods.
        # Create chapters from the remaining, unbroken periods of photos.
        absolute_start = datetime(1, 1, 1)
        absolute_end = datetime.now() + timedelta(days=1)

        text_chapters = []  # Combine all overlapping text into single chapters.
        current_chapter = []

        # TODO: Figure out why I'm missing a text-chapter...
        for text in self.text:
            found_matching_period = False
            for chapter in text_chapters:
                if text.period in chapter.period:
                    chapter.add_text([text])
                    found_matching_period = True
                    break
            # If no overlapping periods are found, add text as new chapter:
            if not found_matching_period:
                text_chapters.append(Chapter(text=[text]))

        # Get photos for text chapters:
        for text_chapter in text_chapters:
            text_chapter.add_photos(self.photos.get_photos_from_period(text_chapter.period))

        # Create chapters for photos in intermittent periods:
        previous_period_end = absolute_start
        photo_chapters = []
        for text_chapter in text_chapters:
            period = Period(previous_period_end, text_chapter.period.start)

            for chapter in photo_chapters:
                if period in chapter.period:
                    abs(1)
            for chapter in text_chapters:
                if period in chapter.period:
                    abs(1)

            photo_chapter = Chapter()
            photo_chapter.add_photos(self.photos.get_photos_from_period(period))
            if photo_chapter:
                photo_chapters.append(photo_chapter)

            previous_period_end = text_chapter.period.end

        # Get the photos from the end of last chapter and all the way forward:
        period = Period(previous_period_end, absolute_end)
        photo_chapter = Chapter()
        photo_chapter.add_photos(self.photos.get_photos_from_period(period))
        if photo_chapter:
            photo_chapters.append(photo_chapter)

        assert not self.chapters
        self.add_chapters(text_chapters)
        self.add_chapters(photo_chapters)
        assert self.chapters

    def create_tex(self, doc):
        print('Generating latex!')
        with doc.create(Section('The year 2018')):
            doc.append('Here are some cool images from 2018!')
            for i, image in enumerate(self.photos.photos):
                with doc.create(Figure(position='h!')) as figure:
                    figure.add_image(image.filepath, width='400px')
                    figure.add_caption(f'Image nr {i} taken {image.timestampstr}')
        return doc

    def latex(self):
        images = [image.latex for image in self.photos.photos]

        return '\n'.join(images)

    def generate_pdf_from_chapters(self, path, title) -> None:
        # TODO: Fix this!
        print('Generating pdf!')
        doc = Document(documentclass='book', document_options=['a4paper', '11pt'])
        doc.packages.append(Package('graphicx'))
        doc.default_filepath = path
        for chapter in self.chapters:
            with doc.create(Section(str(chapter.period))):
                for text in chapter.text:
                    doc.append(text.text_escape)
                for photo in chapter.photos:
                    doc.append(NoEscape(photo.latex))
            doc.append(NoEscape(r'\newpage'))

        doc.generate_pdf()
        doc.generate_tex()

        # doc = self.create_tex()
        # doc.default_filepath = path
        # doc.generate_pdf(title, clean=True, clean_tex=True)
        print('Done!')

    def generate_pdf(self, path, title) -> None:
        print('Generating pdf!')
        doc = Document(documentclass='book', document_options=['a4paper', '11pt'])
        doc.packages.append(Package('graphicx'))
        doc.default_filepath = path
        with doc.create(Section('Section 1')):
            doc.append(NoEscape(self.latex()))
        doc.generate_pdf()
        doc.generate_tex()

        # doc = self.create_tex()
        # doc.default_filepath = path
        # doc.generate_pdf(title, clean=True, clean_tex=True)
        print('Done!')

    def generate_pdf2(self, path, title) -> None:
        print('Generating pdf!')
        doc = Document(title)
        doc.default_filepath = path
        doc = self.create_tex(doc)
        doc.generate_pdf()
        doc.generate_tex()
        print('Done!')

    def generate_latex(self, path, title) -> None:
        print('Printing latex!')
        doc = self.create_tex()
        print(doc.generate_tex())
        print('Done!')
        # text = []
        # text.append('\documentclass{article}%')
        # for count, image in enumerate(self.images):
        #     count = count + 1
        #     text.append(image.latex)
        #     if count % 2 == 0:
        #         text.append("\\newpage\n")
        #     else:
        #         text.append('\\vspace{8 mm}\n')
        #
        # for l in text:
        #     print(l)
