from photobook.main import Photobook

def test_main():
    book = Photobook(image_store=r"E:\Dropbox\Tobias\Programming\photobook\test\bin\*.jpg", text_store='somepath')
    assert len(book.images) == 4

    pdf_name = ''
    # book.generate_pdf2(path=r'E:\Dropbox\Tobias\Programming\photobook\test\output\test_main_pylatex', title=pdf_name)
    book.generate_pdf(path=r'E:\Dropbox\Tobias\Programming\photobook\test\output\test_main', title=pdf_name)

    #shutil.rmtree(os.path.join(pdf_path, pdf_name+'.pdf'))
    pass


