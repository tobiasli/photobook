# !/usr/bin/env python

# Name: create.py
# Description: Generate images latex for all images defined by 'files' below
# Run: python create.py > images.tex
# Date: January 2016
# Author: Richard Hill http://retu.be

import glob
from typing import List, Union
import os, sys
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from exifread import process_file
from pylatex.utils import escape_latex

from photobook import tregex

class Photo:
    get_tags = {'EXIF DateTimeOriginal': 'timestampstr',
                'EXIF ExifImageWidth': 'width',
                'EXIF ExifImageLength': 'height',
                'Image Orientation': 'orientation'}

    rotation_pattern = '(?:Rotated)? (?P<angle>\d+(?:.\d+)?) (?P<direction>\w+)'

    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.path, file = os.path.split(filepath)
        self.filename, self.file_extension = os.path.splitext(file)
        self.image = Image.open(filepath)
        self.exif = process_file(open(filepath, 'rb'))
        for tag in self.get_tags:
            assert tag in self.exif
            setattr(self, self.get_tags[tag], str(self.exif[tag]))

        self.width = 400


    @property
    def latex(self):
        begining = r'\begin{figure}[h!]%'
        end = r'\end{figure}%'

        args = ','.join([self.width_latex, self.orientation_latex])
        includegraphics = f'\\includegraphics[{args}]{{{self.path}\\{{{self.filename}}}{self.file_extension}}}%'

        # Prints the latex for each image. Images have a black border and caption
        # detailing the file name and date taken (as determined by exif data)
        latex = '\n'.join([begining, includegraphics, end])
        return latex
        # code = ''
        # code += '\\begin{figure}[ht!]'
        # code += '\n\\centering'
        # code += "\n{%"
        # code += "\n\\setlength{\\fboxsep}{0pt}%"
        # code += "\n\\setlength{\\fboxrule}{2pt}%"
        # code += "\n\\fbox{\\includegraphics[height=95mm]{" + self.path + "}}%"
        # code += "\n}%"
        # code += '\n\\caption{' + '\\texttt{[' + self.filepath_latex + ']}' + ' ' + self.timestamp.strftime('%d' + ' ' + self.timestamp.strftime('%B') + ' ' + self.timestamp.strftime('%Y') + '}')
        # code += '\n\\end{figure}'
        # return code

    @property
    def orientation_latex(self):
        match = tregex.name(self.rotation_pattern, self.orientation)
        latex = 'angle={}'
        direction = {'CW': -1, 'CCW': 1}
        if match:
            return latex.format(float(match[0]['angle']) * direction[match[0]['direction']])
        else:
            return ''

    @property
    def width_latex(self):
        return 'width={}px'.format(self.width)

    @property
    def filepath_latex(self):
        return (os.path.basename(self.path)).replace("_", "\_");

    @property
    def timestamp(self):
        return datetime.strptime(self.timestampstr, '%Y:%m:%d %H:%M:%S')

    @staticmethod
    def rotate_original_image_according_to_orientation(self, image, orientation):
        pass


class PhotoCollection:
    def __init__(self, searches):
        self.searches = searches

        self.images = self.load(searches)

    @staticmethod
    def load(searches: Union[List, str]) -> List[Photo]:
        # Get all images (.JPG and .jpg in this example)
        if isinstance(searches, str):
            searches = [searches]

        first = True
        for search in searches:
            if first:
                files = glob.glob(search)
                first = False
            else:
                files.extend(glob.glob(search))

        if not files:
            raise FileNotFoundError('No images where found with that search pattern.')

        images = []
        for file in files:
            images += [Photo(file)]

        return images


# Returns value of specified exif field.
def get_exif_value(exif, field):
    for (k, v) in exif.iteritems():
        if TAGS.get(k) == field:
            return v


def get_comparator(filepath):
    return get_timestamp(get_exif_data(filepath))


def get_exif_data(filepath):
    return Photo.open(filepath)._getexif();


def get_timestamp(exif):
    dt = get_exif_value(exif, "DateTimeOriginal")
    return datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')


# Gets name of image from full path. Escapes underscores for latex.
def escape_latex_filename(filepath):
    return (os.path.basename(filepath)).replace("_", "\_");


# Prints the latex for each image. Images have a black border and caption
# detailing the file name and date taken (as determined by exif data)
def get_latex(filepath):
    exif = get_exif_data(filepath)
    do = get_timestamp(exif)

    print('\\begin{figure}[ht!]')
    print('\\centering')
    print("{%")
    print("\\setlength{\\fboxsep}{0pt}%")
    print("\\setlength{\\fboxrule}{2pt}%")
    print("\\fbox{\\includegraphics[height=95mm]{" + filepath + "}}%")
    print("}%")
    print('\\caption{' + '\\texttt{[' + get_filename(filepath) + ']}' + ' ' + do.strftime('%d') + ' ' + do.strftime(
        '%B') + ' ' + do.strftime('%Y') + '}')
    print('\\end{figure}\n')
    return;

# # Sort the images chronologically
# files = sorted(files, key=get_comparator)
#
# # Loop over images and print(latex for each)
# count = 0
# for filepath in files:
#     count = count + 1
#     get_latex(filepath)
#     if count % 2 == 0:
#         print("\\newpage\n")
#     else:
#         print('\\vspace{8 mm}\n')
