from photobook import images

def test_photos():
    img = images.load(r"E:\Dropbox\Tobias\Programming\photobook\test\test_photos\*.jpg")

    assert len(img) == 3
    assert isinstance(img[0], images.Image)
    assert isinstance(img[0].latex, str)
    print(img[0].latex)