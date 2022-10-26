import os

from setuptools import setup
from setuptools.extension import Library
from distutils.command.build_ext import build_ext as _build_ext


BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class CTypesLibrary(Library): pass


class build_ext(_build_ext):
    """
    Since compiled C code imported as shared library using ctypes, it is neccessary to know its name.
    Therefore, get_ext_filename is overridden to return platform-independent name.
    See https://stackoverflow.com/questions/4529555/building-a-ctypes-based-c-library-with-distutils
    """
    def build_extension(self, ext):
        self._ctypes = isinstance(ext, CTypesLibrary)
        return super().build_extension(ext)

    def get_ext_filename(self, ext_name):
        # If you are going to use setuptools' build_ext:
        # setuptools' build_ext calls get_ext_filename() once before build_extension():
        # It's in finalize_options(), and the name doesn't seem to matter.
        if getattr(self, '_ctypes', False):
            return os.path.join(*ext_name.split('.')) + '.so'
        return super().get_ext_filename(ext_name)


with open(os.path.join(BASE_DIR, 'README.md'), 'r') as f:
    long_description = f.read()


setup(
    name='afaligner',
    version='0.1.9',
    url='https://github.com/r4victor/afaligner',
    author='Victor Skvortsov',
    author_email='vds003@gmail.com',
    description='A forced aligner intended for synchronization of narrated text',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: C',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    keywords=['forced-alignment'],
    packages=['afaligner'],
    package_dir={'': 'src'},
    package_data={'afaligner': ['templates/*']},
    install_requires=[
        'aeneas>=1.7.3.0',
        'Jinja2>=3.1.2',
    ],
    ext_modules=[CTypesLibrary(
        'afaligner.c_modules.dtwbd',
        sources=['src/afaligner/c_modules/dtwbd.c']
    )],
    cmdclass={'build_ext': build_ext}
)
