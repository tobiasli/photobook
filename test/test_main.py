from photobook.main import Photobook
import shutil
import os

def test_main():
    book = Photobook(image_store=r"E:\Dropbox\Tobias\Programming\photobook\test\test_photos\*.jpg", text_store='somepath')
    assert len(book.images) == 3

    pdf_path = r'E:\Dropbox\Tobias\Programming\photobook\test\test_photos'
    pdf_name = 'test_pdf'
    book.generate_pdf(path=pdf_path, title=pdf_name)

    #shutil.rmtree(os.path.join(pdf_path, pdf_name+'.pdf'))



