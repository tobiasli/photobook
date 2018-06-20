from typing import List, Union
from photobook import tregex
from datetime import datetime, timedelta
from codecs import open
from photobook.dateparse import parse as dateparse


def parse(string: str) -> datetime:
    return dateparse(string, full_text=True)


class Text:
    def __init__(self, text: Union[List, str]) -> None:
        if isinstance(text, str):
            lines = text.split('\n')
        else:
            lines = text

        match = tregex.name('(?P<timestamp>\d.*\d) (?P<author>.*?)$', lines[0])[0]
        self.timestamp = parse(match['timestamp'])
        self.author = match['author']

        contents = []
        found_contents_dates = False
        for line in lines:
            line = line.strip('\r\n')
            if line and line[0] == '*':
                line = line.replace('*', '').strip()
                if len(line) > 10:
                    dates = line.split('-')
                else:
                    dates = [line, line]

                datetimes = [parse(date) for date in dates]
                # We define end-include by adding a day:
                datetimes[1] = datetimes[1] + timedelta(days=1)
                found_contents_dates = True
                self.period = datetimes
            elif found_contents_dates and line:
                contents += [line]

        self.text = '\r\n'.join(contents)

    def __eq__(self, other: "Text") -> bool:
        return other.timestamp == self.timestamp and other.text == self.text and other.period == self.period and other.author == self.author

    def __dict__(self) -> dict:
        return dict(timestamp=self.timestamp, author=self.author, period=self.period,
                    text=self.text)

    def __str__(self) -> str:
        return str(self.__dict__())


class TextCollection:
    def __init__(self, text_files: Union[List, str] = None) -> None:
        self.text = []
        if isinstance(text_files, str):
            text_files = [text_files]
        if text_files:
            for file in text_files:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.readlines()
                    collection = []
                    for line in text:
                        if line[0] == '#':
                            # Finish previous collection and start new
                            if collection:
                                self.text.append(Text(collection))
                                collection = []
                        if line:
                            collection += [line]

    def __contains__(self, item: Union[Text, "TextCollection"]) -> bool:
        assert isinstance(item, (Text, TextCollection))
        match = True
        strings = self.strings
        if isinstance(item, TextCollection):
            for new_text in item.strings:
                if not new_text in strings:
                    match = False
            return match
        elif isinstance(item, Text):
            return str(item) in strings

    @property
    def strings(self):
        return [str(text) for text in self.text]

    def get_text_for_timestamp(self, timestamp: datetime) -> List[Text]:
        return [text for text in self.text if text.period[0] <= timestamp < text.period[1]]

    def add_text(self, text: Union[Text, List[Text]]) -> None:
        if not isinstance(text, list):
            text = [text]
        self.text.append(text)

    def __getitem__(self, key):
        return self.text[key]