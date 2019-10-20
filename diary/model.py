"""Classes for retrieving images."""
import glob
import os
from datetime import datetime, timedelta
import typing as ty

from diary import parsing
from book import model
from old.dateparse import parse


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
    images: ty.List[model.Image]

    def load_images_from_path(self, path: str) -> None:
        """Search a specific path, and add all found images to ImageCollection."""
        files = list()
        for type in ACCEPTED_IMAGE_TYPES:
            files.extend(glob.glob(os.path.join(path, f'*.{type}')))

        if not files:
            raise FileNotFoundError('No images where found with that search pattern.')

        images = []
        for file in files:
            images += [model.Image(file)]

        self.images = images

    def get_photos_from_period(self, period: Period) -> ty.List[model.Image]:
        """Get photos from a period. Start Include, end exclude."""
        assert isinstance(period, Period)
        return [image for image in self.images if image.timestamp in period]


class DiaryChapter:
    def __init__(self, parsed: parsing.Entry) -> None:
        self._title = parsed.title
        self._timestamp = parsed.timestamp
        self._period = parsed.period
        self.text = parsed.text

    @property
    def timestamp(self) -> datetime:
        return parse(self._timestamp)

    @property
    def period(self) -> Period:

        if self._period:
            if len(self._period) > 10:
                dates = self._period.split('-')
                datetimes = [parse(date) for date in dates]
            else:
                date = parse(self._period)
                datetimes = [date, date]

        else:
            ts = self.timestamp
            datetimes = [ts.replace(hour=0, minute=0, second=0, microsecond=0),
                         ts.replace(hour=0, minute=0, second=0, microsecond=0)]

        # We define end-include by adding a day:
        datetimes[1] = datetimes[1] + timedelta(days=1)

        return Period(*datetimes)
