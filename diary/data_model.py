from datetime import datetime
from typing import Union, List


class Period:
    def __init__(self, start: datetime = None, end: datetime = None) -> None:
        self.start = start
        self.end = end

    def __contains__(self, item: Union["Period", datetime]) -> bool:
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

    def __iter__(self) -> List[datetime]:
        yield self.start
        yield self.end

    def __eq__(self, other: "Period") -> bool:
        if not isinstance(other, Period):
            return False
        return self.start == other.start and self.end == other.end