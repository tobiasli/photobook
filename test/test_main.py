from photobook.main import Photobook

def test_main():
    book = Photobook(image_store=r"E:\Dropbox\Tobias\Programming\photobook\test\test_photos\*.jpg", text_store='somepath')
    assert len(book.images) == 3