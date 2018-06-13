from photobook import images
from pylatex import Document, Section, Figure

class Photobook:
    def __init__(self, image_store:str, text_store:str=None) -> None:
        self.images = images.load(image_store)
        #self.text = text.load(text_store)

    def generate_pdf(self, path, title) -> None:
        print('Generating pdf!')
        doc = Document(default_filepath=path)
        with doc.create(Section('The year 2018')):
            doc.append('Here are some cool images from 2018!')
            for i, image in enumerate(self.images):
                with doc.create(Figure(position='h!')) as figure:
                    figure.add_image(image.path, width='400px')
                    #figure.add_caption(f'Image nr {i} taken {image.timestampstr}')
        doc.generate_pdf(title)
        print('Done!')

