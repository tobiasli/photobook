from photobook import tregex
from datetime import datetime, timedelta
from photobook.dateparse import parse as dateparse


def parse(string: str) -> datetime:
    return dateparse(string, full_text=True)


class Text:
    def __init__(self, text: str) -> None:

        lines = text.split('\n')
        match = tregex.name('(?P<timestamp>\d.*\d) (?P<author>.*?)$', lines[0])[0]
        self.timestamp = parse(match['timestamp'])
        self.author = match['author']

        for line in lines:
            if line and line[0] == '*':
                line = line.replace('*', '').strip()
                if len(line) > 10:
                    dates = line.split('-')
                else:
                    dates = [line, line]

                datetimes = [parse(date) for date in dates]
                datetimes[1] = datetimes[1] + timedelta(hours=23, minutes=59, seconds=59)
                break

        self.timestamp = datetime(2018, 6, 16, 21, 0, 0),
        self.author = 'Tobias'
        self.content_dates = [datetime(2018, 1, 1, 0, 0, 0), datetime(2018, 3, 1, 23, 59, 59)],
        self.content = 'It was a really, really cold winter. Everything was covered in deep, white snow for months. Most winters were dark, but because of all the snow, this winter was bright and crisp and clean.'

    def __dict__(self) -> dict:
        return dict(timestamp=self.timestamp, author=self.author, content_dates=self.content_dates,
                    content=self.content)
