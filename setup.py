#!/usr/bin/env python

import io
import os
import sys
from shutil import rmtree
import os.system
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup, Command

# ----------------------  Cython compilation
# Build cython extensions as part of setup. Based on
# https://stackoverflow.com/questions/4505747/how-should-i-structure-a-python-package-that-contains-cython-code
USE_CYTHON = False
from distutils.core import setup
from distutils.extension import Extension

if USE_CYTHON:
    try:
        # Trick from
        # https://stackoverflow.com/questions/19919905/how-to-bootstrap-numpy-installation-in-setup-py
        from Cython.Distutils import build_ext as _build_ext

        class build_ext(_build_ext):
            def finalize_options(self):
                _build_ext.finalize_options(self)
                # Prevent numpy from thinking it is still in its setup process:
                __builtins__.__NUMPY_SETUP__ = False
                import numpy

                self.include_dirs.append(numpy.get_include())

    except:
        # Cython is apparently not available on the system. Make do without it
        USE_CYTHON = False

cmdclass = {}
ext_modules = []

# New Cython modules must be registered here
if USE_CYTHON:
    ext_modules += [
        Extension(
            "porepy.numerics.fv.cythoninvert",
            ["src/porepy/numerics/fv/invert_diagonal_blocks.pyx"],
        )
    ]
    cmdclass.update({"build_ext": build_ext})

# --------------------- End of cython part




def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


with open("requirements.txt") as f:
    required = f.read().splitlines()


long_description = read("Readme.rst")

class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')
        
        sys.exit()

cmdclass.update({"upload":  UploadCommand})

setup(
    name="porepy",
    version="1.1.0",
    license="GPL",
    keywords=["porous media simulation fractures deformable"],
    author="Eirik Keilegavlen, Runar Berge, Alessio Fumagalli, Michele Starnoni, Ivar Stefansson and Jhabriel Varela",
    install_requires=required,
    description="Simulation tool for fractured and deformable porous media",
    long_description=long_description,
    maintainer="Eirik Keilegavlen",
    maintainer_email="Eirik.Keilegavlen@uib.no",
    platforms=["Linux", "Windows"],
    package_data={"porepy": ["py.typed"]},
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[
        os.path.splitext(os.path.basename(path))[0] for path in glob("src/*.py")
    ],
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    zip_safe=False,
)
