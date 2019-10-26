import os

from diary import parsing_definition
from parsing import readers
from parsing.parsing import Parser
from diary.binders.pylatex import PylatexBinder
import book.model as bm
import diary.model as dm


IMAGE_FOLDER = os.path.join(os.path.split(__file__)[0], 'test', 'bin')
FILENAME = 'context.md'


def create_book(text_file: str, image_directory: str, output_filepath: str) -> None:
    """Create a diary given a correctly formatted text file and a folder full of images."""
# Load images:
    images = dm.ImageCollection()
    images.load_images_from_path(image_directory)

    # Get text model:
    stream = readers.TextStream(reader=readers.FileReader(filepath=text_file, encoding='utf-8'))
    parser = Parser(finders=[parsing_definition.ENTRY_FINDER])
    obj = parser.parse_stream(stream=stream)

    chapters = []
    for entry in obj.contents:
        chapter = dm.DiaryChapter(entry=entry)
        chapter.add_images(images.get_photos_from_period(chapter.period))

        chapters.append(chapter)

    chapters = [chapter for chapter in chapters if
                dm.datetime(2018, 1, 26) < chapter.timestamp < dm.datetime(2018, 4, 23)]

    # Build book model from text and images:
    book = bm.Book(title=bm.Title('Test book 2019'))
    book.add_chapters(chapters=[chap.to_book_chapter() for chap in chapters])

    print(f'Book with {len(chapters)} chapters and {len(book.images)} images.')

    # Bind pdf:
    binder = PylatexBinder(book)
    binder.bind()
    os.system(binder.export(output_filepath))

