"""Classes for retrieving images."""
import glob
import os
from datetime import datetime, timedelta
import typing as ty
from itertools import zip_longest

from diary import parsing_definition
import book.model as bm
import dateparse

ACCEPTED_IMAGE_TYPES = ['jpg', 'jpeg']


class Period:
    def __init__(self, start: datetime = None, end: datetime = None) -> None:
        """Represent comparable time period."""
        self.start = start
        self.end = end

    def __contains__(self, item: ty.Union["Period", datetime]) -> bool:
        """Check if other Period is completely within start-end. Check if other datetime is within start-end."""
        assert isinstance(item, (Period, datetime))
        if not self.start or not self.end:
            return False
        if isinstance(item, Period):
            if not item.start or not item.end:
                return False

        if isinstance(item, datetime):
            return self.start <= item < self.end
        elif isinstance(item, Period):
            return self.start <= item.start < self.end and self.start < item.end <= self.end
        else:
            raise TypeError('Period.__contains__ only accepts Period or datetime objects')

    def __add__(self, other: "Period") -> "Period":
        """Combine two periods. Keep lowest start and highest end."""
        assert isinstance(other, Period)
        if not self.start and not other.start:
            return Period()
        elif not self.start:
            return other
        elif not other:
            return self

        start = min([self.start, other.start])
        end = max([self.end, other.end])
        return Period(start, end)

    def __str__(self) -> str:
        return f'<Period: {self.start} {self.end}>'

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> ty.List[datetime]:
        yield self.start
        yield self.end

    def __eq__(self, other: "Period") -> bool:
        if not isinstance(other, Period):
            return False
        return self.start == other.start and self.end == other.end


class ImageCollection:
    """Class for handling a collection of images, and able to return images based on period queries."""
    _images: ty.List[bm.Image]

    @property
    def images(self) -> ty.List[bm.Image]:
        return sorted(self._images, key=lambda im: im.timestamp)

    def load_images_from_path(self, path: str) -> None:
        """Search a specific path, and add all found images to ImageCollection."""
        files = list()
        for type in ACCEPTED_IMAGE_TYPES:
            files.extend(glob.glob(os.path.join(path, f'*.{type}')))

        if not files:
            raise FileNotFoundError('No images where found with that search pattern.')

        images = []
        for file in files:
            images += [bm.Image(file)]

        self._images = images

    def get_photos_from_period(self, period: Period) -> ty.List[bm.Image]:
        """Get photos from a period. Start Include, end exclude."""
        assert isinstance(period, Period)
        return [image for image in self.images if image.timestamp in period]


class DiaryChapter:
    def __init__(self, entry: parsing_definition.Entry) -> None:
        """Take the results of a parsed diary entry and build an actual DiaryChapter."""
        self.title = entry.title
        self._timestamp = entry.timestamp
        self._period = entry.period
        self.text = entry.text
        self.images: ty.List[bm.Image] = list()

    @property
    def timestamp(self) -> datetime:
        return dateparse.parse(self._timestamp)[0]

    @property
    def timestamp_str(self) -> str:
        return self._timestamp

    @property
    def period(self) -> Period:
        """Return a valid Period for this posts self._period."""
        if self._period:
            datetimes = dateparse.parse(self._period)
            if len(datetimes) == 1:
                datetimes.append(datetimes[0] + timedelta(days=1))
        else:
            ts = self.timestamp
            datetimes = [ts.replace(hour=0, minute=0, second=0, microsecond=0),
                         ts.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)]

        return Period(*datetimes)

    def add_images(self, images: ty.Sequence[bm.Image]) -> None:
        """Add images to diary."""
        self.images.extend(images)

    def to_book_chapter(self) -> bm.Chapter:
        """Convert the Diary Chapter to a Book-chapter"""
        return bm.Chapter(
            title=bm.Title(f'{self.timestamp_str} - {self.title}'),
            contents=self.create_content_list())

    def create_content_list(self) -> bm.ContentSequence:
        """Take the text and images added to this chapter, and divide them into portions of content in a sequence."""

        # Group images two and two:
        image_pairs = [[left, right] for left, right in zip_longest(self.images[::2], self.images[1::2])]

        # Divide text into sections:
        text_sections = [t for t in self.text.split('\n') if t]

        images_left = []
        text_left = []
        contents = bm.ContentSequence()
        for text, image_pair in zip_longest(text_sections, image_pairs):
            image_pair = [image for image in image_pair if image] if image_pair else list() # Pop Non-images if not a pair.
            if not text:
                images_left.extend(image_pair)
            elif not image_pair:
                text_left.append(text)
            else:
                contents.add_contents([bm.Text(text)])
                contents.add_contents([bm.ImageSequence(image_pair)])

        if images_left:
            contents.add_contents([bm.ImageSequence(images_left)])
        if text_left:
            contents.add_contents([bm.Text('\n\n'.join(text_left))])

        return contents
