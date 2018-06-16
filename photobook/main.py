from photobook.photos import PhotoCollection
from pylatex import Document, Section, Figure, NoEscape, Package

class Photobook:
    def __init__(self, image_store:str, text_store:str=None) -> None:
        self.images = PhotoCollection(image_store).images
        #self.text = text.load(text_store)

    def create_tex(self, doc):
        print('Generating latex!')
        with doc.create(Section('The year 2018')):
            doc.append('Here are some cool images from 2018!')
            for i, image in enumerate(self.images):
                with doc.create(Figure(position='h!')) as figure:
                    figure.add_image(image.filepath, width='400px')
                    figure.add_caption(f'Image nr {i} taken {image.timestampstr}')
        return doc

    def latex(self):
        images = [image.latex for image in self.images]

        return '\n'.join(images)

    def generate_pdf(self, path, title) -> None:
        print('Generating pdf!')
        doc = Document(title)
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
