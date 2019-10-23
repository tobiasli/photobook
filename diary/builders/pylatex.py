import os
from tempfile import NamedTemporaryFile
import typing as ty

from itertools import zip_longest
from book import model as bm

import pylatex as pl


class BinderBase:
    """Base class for representing specific latex implementations of the bm.Book class."""
    book: bm.Book

    def __init__(self, book: bm.Book) -> None:
        """Base class for building books."""
        self.book = book

    def bind(self) -> None:
        """Call the _bind command of the current Binder."""
        self._bind()

    def export(self, path: str = None) -> str:
        """Call the _export command of the current Binder."""
        path = path or NamedTemporaryFile().name
        return self._export(path)

    def _bind(self) -> None:
        """Build the latex model for the book."""
        raise NotImplementedError('This method needs to be implemented in your subclass.')

    def _export(self, path: str) -> str:
        """Create PDF for this specific latex implementation. Should return path."""
        raise NotImplementedError('This method needs to be implemented in your subclass.')


class PylatexBinder(BinderBase):
    """Book binder for PyLatex."""
    doc: pl.Document

    def _bind(self) -> None:
        """Build the Document in pylatex."""
        doc = pl.Document(documentclass='book', document_options=['a4paper', '11pt'])
        doc.packages.append(pl.Package('graphicx'))

        # Create info page
        doc.preamble.append(pl.Command('title', self.book.title.text))
        # doc.preamble.append(pl.Command('author', 'Anonymous author'))
        doc.preamble.append(pl.Command('date', pl.NoEscape(r'\today')))
        doc.append(pl.NoEscape(r'\maketitle'))

        # Add chapters
        for chapter in self.book.chapters:
            # doc.create(pl.NewPage())
            with doc.create(pl.Section(title=chapter.title.text, numbering=False)):
                doc.append(chapter.text.text)

                # Add images
                image_pairs = [(left, right) for left, right in zip_longest(chapter.images[::2], chapter.images[1::2])]

                for pair in image_pairs:
                    with doc.create(pl.LongTabu("X[c] X[c]")) as image_table:
                        graphics = list()
                        for image in pair:
                            if image:
                                graphics.append(pl.StandAloneGraphic(filename=image.path_latex,
                                                                     image_options=rf'width=\linewidth, {image.orientation_latex}'))
                            else:
                                graphics.append('')

                        image_table.add_row(graphics)

        self.doc = doc

    def _export(self, path: str) -> str:
        """Export the document in pylatex."""
        self.doc.generate_pdf(path)
        return path + '.pdf'
