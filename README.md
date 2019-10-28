# photobook
Create a formated pdf photobook from a resource of timestamped text and a collection of photos.

The package contains, for the time being, **parsing**, **book** and **diary**.
* ```book``` contains a basic model for a book, a chapter and images, along with a framework for creating latex representations of this model.
* ```diary``` is a specific implementation of `book` for creating a pdf based on diary text file and a folder full of images.

# Requirements
Python packages:
* pylatex
* exifread

Latex framework:
* MiKTeX
