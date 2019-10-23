import os

from diary import parsing_definition
from parsing import readers
from parsing.parsing import Parser
from diary.builders.pylatex import PylatexBinder
import book.model as bm
import diary.model as dm


IMAGE_FOLDER = os.path.join(os.path.split(__file__)[0], 'test', 'bin')
FILENAME = 'context.md'

# Load images:
images = dm.ImageCollection()
images.load_images_from_path(IMAGE_FOLDER)

# Get text model:
stream = readers.TextStream(reader=readers.FileReader(filepath=os.path.join(IMAGE_FOLDER, FILENAME), encoding='utf-8'))
parser = Parser(finders=[parsing_definition.ENTRY_FINDER])
obj = parser.parse_stream(stream=stream)

chapters = []
for entry in obj.contents:
    chapter = dm.DiaryChapter(entry=entry)
    chapter.add_images(images.get_photos_from_period(chapter.period))

    chapters.append(chapter)

# Build book model from text and images:
book = bm.Book(title=bm.Title('Test book 2019'))
book.add_chapters(chapters=[chap.to_book_chapter() for chap in chapters])

# Bind pdf:
binder = PylatexBinder(book)
binder.bind()
os.system(binder.export())