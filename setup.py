from setuptools import setup, Extension
from distutils.command.build_ext import build_ext as _build_ext


class CTypes(Extension): pass


class build_ext(_build_ext):
    """
    Since compiled C code imported as shared library using ctypes, it is neccessary to know its name.
    Therefore, get_ext_filename is overridden to return platform-independent name.
    See https://stackoverflow.com/questions/4529555/building-a-ctypes-based-c-library-with-distutils
    """
    def build_extension(self, ext):
        self._ctypes = isinstance(ext, CTypes)
        return super().build_extension(ext)

    def get_export_symbols(self, ext):
        if self._ctypes:
            return ext.export_symbols
        return super().get_export_symbols(ext)

    def get_ext_filename(self, ext_name):
        if self._ctypes:
            return ext_name + '.so'
        return super().get_ext_filename(ext_name)


setup(
    name='afaligner',
    version='0.0.1',
    description='A forced aligner intended for synchronization of narrated text',
    url='https://github.com/r4victor/afaligner',
    author='Victor Skvortsov',
    author_email='vds003@gmail.com',
    license='MIT',
    packages=['afaligner'],
    package_data={'afaligner': ['templates/*']},
    install_requires=[
        'numpy==1.18.4', 'aeneas==1.7.3.0', 'Jinja2==2.11.1',
    ],
    ext_modules=[CTypes(
        'afaligner.c_modules.dtwbd',
        sources=['afaligner/c_modules/dtwbd.c']
    )],
    cmdclass={'build_ext': build_ext}
)