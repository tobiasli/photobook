from typing import List, Union
from datetime import datetime, timedelta
import os
import glob
from collections import Iterable

from pylatex import Document, Section, Figure, NoEscape, Package
from exifread import process_file
from pylatex.utils import escape_latex
from PIL import Image

from photobook import tregex
from photobook.dateparse import parse as dateparse


def parse(string: str) -> datetime:
    return dateparse(string, full_text=True)


class Period:
    def __init__(self, start: datetime=None, end: datetime=None) -> None:
        self.start = start
        self.end = end

    def __contains__(self, item: Union["Period", datetime]) -> bool:
        if not self.start:
            return False
        if isinstance(item, datetime):
            return self.start <= item <= self.end
        elif isinstance(item, Period):
            return item.start in self or item.end in self
        else:
            raise TypeError('Period.__contains__ only accepts Period or datetime objects')

    def __add__(self, other:"Period") -> "Period":
        assert isinstance(other, Period)
        if not self.start and not other.start:
            return Period()
        elif not self.start:
            return other
        elif not self.other:
            return self

        start = min([self.start, other.start])
        end = max([self.end, other.end])
        return Period(start, end)



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
    dict_properties = ['timestamp', 'text', 'period', 'author']

    def __init__(self, text: Union[List, str]) -> None:
        if isinstance(text, str):
            lines = text.split('\n')
        else:
            lines = text

        match = tregex.name('(?P<timestamp>\d.*\d) (?P<author>.*?)$', lines[0])[0]
        self.timestamp = parse(match['timestamp'])
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

    def add_text(self, text: Union[Text, List[Text]]) -> None:
        if not isinstance(text, list):
            text = [text]
        self.text.extend(text)
        self.text = sorted(self.text, lambda x: x.period.start)

    def __getitem__(self, key):
        return self.text[key]

    def __iter__(self):
        for text in self.text:
            yield text

    def __bool__(self) -> bool:
        return bool(self.text)


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

        self.width = 200

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
        args = ','.join([arg for arg in [self.width_latex, self.orientation_latex] if arg])
        includegraphics = f'\\includegraphics[{args}]{{{self.convert_latex_path(self.path)}/{{{self.convert_latex_path(self.filename)}}}{self.file_extension}}}%'
        latex = '\n'.join([begining, includegraphics, end])
        return latex

    @property
    def orientation_latex(self):
        return self.orientation_translator(self.orientation)

    @staticmethod
    def orientation_translator(orientation):
        match = tregex.name('(?:Rotated)? (?P<angle>\d+(?:.\d+)?) ?(?P<direction>\w+)?', orientation)
        angle = int(match[0]['angle'])
        direction = match[0]['direction']
        latex = 'angle={:d}'
        direction_lookup = {'CW': lambda x: 360 - x, None: lambda x: x}
        if match:
            return latex.format(direction_lookup[direction](angle))
        else:
            return ''

    @property
    def width_latex(self):
        return 'width={}px'.format(self.width)

    @property
    def filepath_latex(self):
        return (os.path.basename(self.path)).replace("_", "\_");

    @property
    def timestamp(self):
        return datetime.strptime(self.timestampstr, '%Y:%m:%d %H:%M:%S')


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
        return [image for image in self.photos if image.timestamp in period]

    def __getitem__(self, key):
        return self.photos[key]

    def __iter__(self):
        for photo in self.photos:
            yield photo

    def __bool__(self) -> bool:
        return bool(self.photos)

    def add_photos(self, photos: List[Photo]) -> None:
        self.photos.extend(photos)
        self.photos = sorted(self.photos, lambda x: x.timestamp)


class Chapter:
    def __init__(self, photos: List[Photo] = None, text: List[Text] = None) -> None:
        """A set of images and text for a specific time period that together make a chapter."""
        self.photos = PhotoCollection()
        self.text = TextCollection()

        if photos:
            self.add_photos(photos)
        if text:
            self.add_text(text)

    def add_photos(self, photos: List[Photo]) -> None:
        assert isinstance(photos, list)
        self.photos.add_photos(photos)

    def add_text(self, text: List[Text]) -> None:
        assert isinstance(text, list)
        self.text.add_text(text)

    @property
    def period(self) -> List[datetime]:
        if self.text:
            periods = list()
            for text in self.text:
                periods.extend(text.period)
            return sum(periods)
        elif self.photos:
            timestamps = [photo.timestamp for photo in self.photos]
            return Period(min(timestamps), max(timestamps))
        else:
            return None


class Photobook:
    def __init__(self, photo_store: str, text_store: str = None) -> None:
        self.photos = PhotoCollection(photo_store)
        self.text = TextCollection(text_store)
        self.chapters = self.chapters_from_text_and_images()

    def chapters_from_text_and_images(self) -> Chapter:
        chapter = Chapter()
        chapters = []
        # Run through text and get all matching photos to create chapters.
        # Create chapters from photo-less text periods.
        # Create chapters from the remaining, unbroken periods of photos.

        last_period_end = datetime(0, 0, 0)
        text_chapters = []  # Combine all overlapping text into single chapters.
        current_chapter = []
        for text in self.text:
            if not current_chapter:
                current_chapter = Chapter(text=[text])
            elif text.period in current_chapter.period:
                current_chapter.add_text([text])
            elif text.period not in current_chapter.period:
                text_chapters.append(current_chapter)
                current_chapter = Chapter()
                current_chapter.add_text(text)



        for text in self.text:
            # Create chapter up until first text:
            textless_chapter = Chapter(photos=self.photos.get_photos_from_period(Period(start=last_period_end, end=text.period.start)))
            chapters.append(textless_chapter)

            # Chapter for first text:
            Chapter(photos=self.photos.get_photos_from_period(text.period))


        for photo in self.photos.photos:
            matched_text = self.text.get_text_for_timestamp(photo.timestamp)
            if matched_text:
                if not chapter.text:
                    chapter.text.add_text(matched_text[0])
                if matched_text[0] in chapter.text:
                    chapter.add_photos([photo])
                else:
                    # Matched text does not match previous chapter, starting new chapter.
                    chapters.append(chapter)
                    chapter.period
                    chapter = Chapter(text=[matched_text[0]])

        if not chapter.period:
            abs(1)
        chapters.append(chapter)

        return chapters

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
