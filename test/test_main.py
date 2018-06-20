from photobook.main import Photobook

def test_Photobook():
    book = Photobook(photo_store=r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg", text_store=r'E:\Dropbox\Tobias\Programming\photobook\test\bin\context.md')
    assert len(book.photos.photos) == 4

    # Check chapters:


    pdf_name = ''
    # book.generate_pdf2(path=r'E:\Dropbox\Tobias\Programming\photobook\test\output\test_main_pylatex', title=pdf_name)
    book.generate_pdf(path=r'E:\Dropbox\Tobias\Programming\photobook\test\output\test_main', title=pdf_name)

    #shutil.rmtree(os.path.join(pdf_path, pdf_name+'.pdf'))
    pass


