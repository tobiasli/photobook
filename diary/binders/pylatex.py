import subprocess

from itertools import zip_longest

import pylatex as pl

from book.binder import BinderBase


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
                                image.create_temp_copy()
                                graphics.append(pl.StandAloneGraphic(filename=image.get_temp_copy_path(),
                                                                     image_options=rf'width=\linewidth, {image.orientation_latex}'))
                            else:
                                graphics.append('')

                        image_table.add_row(graphics)

        self.doc = doc

    def _export(self, path: str) -> str:
        """Export the document in pylatex."""
        try:
            import os
            for image in self.book.images:
                if not os.path.exists(image.get_temp_copy_path()):
                    abs(1)
            self.doc.generate_pdf(path)
        except subprocess.CalledProcessError:
            pass
        # time.sleep(10)
        self.book.temp_cleanup()
        return path + '.pdf'
