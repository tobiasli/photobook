from photobook import images
from pylatex import Document, Section, Figure

class Photobook:
    def __init__(self, image_store:str, text_store:str=None) -> None:
        self.images = images.load(image_store)
        #self.text = text.load(text_store)

    def generate_pdf(self, pdf_path) -> None:
        doc = Document('basic')
        with doc.create(Section('Året 2018')):
            for i, image in enumerate(self.images):
                with doc.create(Figure(position='h!')) as image:
                    image.add_image(image.path, width='120px')
                    image.add_caption(f'Image nr {i} taken {image.timestampstr}')
        doc.generate_pdf

