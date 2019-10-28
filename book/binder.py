"""When binding a book.model.Book, you need a Binder. BinderBase is a superclass for any latex wrappers used to bind
books."""

from tempfile import NamedTemporaryFile

from book import model as bm


class BinderBase:
    """Base class for representing specific latex implementations of the bm.Book class."""
    book: bm.Book

    def __init__(self, book: bm.Book) -> None:
        """Base class for building books."""
        self.book = book

    def bind(self) -> None:
        """Call the _bind command of the current Binder."""
        self._bind()

    def export(self, path: str = None) -> str:
        """Call the _export command of the current Binder."""
        path = path or NamedTemporaryFile().name
        return self._export(path)

    def _bind(self) -> None:
        """Build the latex model for the book."""
        raise NotImplementedError('This method needs to be implemented in your subclass.')

    def _export(self, path: str) -> str:
        """Create PDF for this specific latex implementation. Should return path."""
        raise NotImplementedError('This method needs to be implemented in your subclass.')
