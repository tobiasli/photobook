import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='book-tobiasli',
                 version='1.0.0',
                 description='Package for creating pdfs out of compilations of text and images.',
                 author='Tobias Litherland',
                 author_email='tobiaslland@gmail.com',
                 url='https://github.com/tobiasli/dateparse',
                 packages=setuptools.find_packages(),
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 requires=['tregex-tobiasli', 'dateparse-tobiasli', 'fileparse-tobiasli', 'pillow', 'pytest', 'pylatex',
                           'exifread']
                 )
