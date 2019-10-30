import subprocess

from itertools import zip_longest

import pylatex as pl

from book.binder import BinderBase
import book.model as bm


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
                for content in chapter.contents.contents:
                    if isinstance(content, bm.Text):
                        doc.append(content.text)
                    elif isinstance(content, bm.ImageSequence):
                        # Add images
                        image_pairs = [(left, right) for left, right in zip_longest(content.images[::2], content.images[1::2])]

                        for pair in image_pairs:
                            with doc.create(pl.LongTabu("X[c] X[c]")) as image_table:
                                graphics = list()
                                for image in pair:
                                    if image:
                                        image.create_temp_copy()
                                        graphics.append(pl.StandAloneGraphic(filename=image.get_temp_copy_path(),
                                                                             image_options=rf'width=\linewidth, {image.orientation_latex}'))
                                    else:
                                        graphics.append('')

                                image_table.add_row(graphics)

        self.doc = doc

    def _export(self, path: str) -> str:
        """Export the document in pylatex."""
        self.doc.generate_pdf(path)
        # time.sleep(10)
        self.book.temp_cleanup()
        return path + '.pdf'
