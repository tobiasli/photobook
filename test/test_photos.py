from photobook import images

def test_photos():
    img = images.PhotoCollection.load(r"E:\Dropbox\Tobias\Programming\photobook\test\test_photos\*.jpg")

    assert len(img) == 3
    assert isinstance(img[0], images.Photo)
    assert isinstance(img[0].latex, str)
    assert [i.orientation for i in img] == ['Rotated 90 CW', 'Rotated 180', 'Rotated 180']
    print(img[0].latex)