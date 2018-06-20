from typing import List, Union
from photobook.photos import PhotoCollection, Photo
from photobook.text import TextCollection, Text
from pylatex import Document, Section, Figure, NoEscape, Package
from datetime import datetime


class Chapter:
    def __init__(self, photos: List[Photo] = None, text:List[Text] = None) -> None:
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
            combine = list()
            periods = [combine.extend(text.period) for text in self.text]
            return [min(periods), max(periods)]
        elif self.photos:
            timestamps = [photo.timestamp for photo in self.photos]
            return [min(timestamps), max(timestamps)]
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
        for photo in self.photos.photos:
            matched_text = self.text.get_text_for_timestamp(photo.timestamp)
            if matched_text:
                if not chapter.text:
                    chapter.text += [matched_text[0]]
                if matched_text[0] in chapter.text:
                    chapter.add_photos([photo])
                else:
                    # Matched text does not match previous chapter, starting new chapter.
                    chapters.append(chapter)
                    chapter = Chapter(text=[matched_text[0]])

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

    def generate_pdf(self, path, title) -> None:
        # TODO: Create pdf from Chapters and not directly from images.
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
