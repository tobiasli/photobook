"""Test image components of diary book."""
import os
import pytest
from datetime import datetime

from diary import model, parsing_definition

FILEPATH = os.path.join(os.path.split(__file__)[0], 'bin')


def test_period_construction():
    period1 = model.Period(datetime(2018, 1, 1), datetime(2018, 2, 1))
    assert period1.start == datetime(2018, 1, 1)


def test_period_contains_datetime():
    period1 = model.Period(datetime(2018, 1, 1), datetime(2018, 2, 1))
    assert datetime(2018, 1, 10) in period1
    assert datetime(2018, 3, 10) not in period1


def test_period_contains_period():
    period1 = model.Period(datetime(2018, 1, 1), datetime(2018, 2, 1))
    period2 = model.Period(datetime(2018, 1, 15), datetime(2018, 1, 30))
    period3 = model.Period(datetime(2018, 1, 15), datetime(2018, 3, 30))
    assert period2 in period1
    assert period3 not in period1


def test_period_addition():
    period1 = model.Period(datetime(2018, 1, 1), datetime(2018, 2, 1))
    period2 = model.Period(datetime(2018, 1, 15), datetime(2018, 2, 15))
    period3 = model.Period(datetime(2018, 3, 1), datetime(2018, 4, 1))

    periodA = period1 + period2
    assert periodA.start == datetime(2018, 1, 1) and periodA.end == datetime(2018, 2, 15)

    periodB = period2 + period3
    assert periodB.start == datetime(2018, 1, 15) and periodB.end == datetime(2018, 4, 1)


def test_collection_load():
    ic = model.ImageCollection()
    ic.load_images_from_path(path=FILEPATH)
    assert len(ic.images) == 4


def test_collection_get_from_period():
    period = model.Period(datetime(2018, 2, 1), datetime(2018, 4, 10))
    ic = model.ImageCollection()
    ic.load_images_from_path(path=FILEPATH)

    images = ic.get_photos_from_period(period)

    assert len(images) == 2
    assert images[0].path == os.path.join(FILEPATH, '2018-02-28-09.12.22.jpg')


@pytest.fixture()
def chapter() -> model.DiaryChapter:
    period = parsing_definition.Period(period='2019.1.1')
    entry = parsing_definition.Entry(title='this is a title', timestamp='1.2.2019')
    entry.add_content(period)
    chap = model.DiaryChapter(entry=entry)
    return chap


def test_chapter_construction(chapter):
    assert chapter


def test_chapter_period(chapter):
    assert chapter.period == model.Period(start=datetime(2019, 1, 1), end=datetime(2019, 1, 2))
