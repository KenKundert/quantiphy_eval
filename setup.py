from setuptools import setup
from codecs import open

with open('README.rst', encoding="UTF-8") as f:
    readme = f.read()

dependencies = 'inform pyparsing quantiphy'

setup(
    name = 'quantiphy_eval',
    version = '0.2.0',
    description = 'calculations with physical quantities',
    long_description = readme,
    long_description_content_type = 'text/x-rst',
    author = "Ken Kundert",
    author_email = 'quantiphy@nurdletech.com',
    url = 'https://github.com/kenkundert/quantiphy_eval',
    download_url = 'https://github.com/kenkundert/quantiphy_eval/tarball/master',
    license = 'GPLv3+',
    packages = 'quantiphy_eval'.split(),
    install_requires = dependencies.split(),
    setup_requires = 'pytest-runner>=2.0'.split(),
    tests_require = 'pytest'.split(),
    python_requires = '>=3.6',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering',
    ],
)
