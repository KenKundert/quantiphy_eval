from setuptools import setup
from codecs import open

with open('README.rst', encoding="UTF-8") as f:
    readme = f.read()

dependencies = 'inform pyparsing quantiphy'

setup(
    name='quantiphy_eval',
    version='0.1.0',
    description='calculations with physical quantities',
    long_description=readme,
    author="Ken Kundert",
    license='GPLv3+',
    py_modules='quantiphy_eval'.split(),
    install_requires=dependencies.split(),
    setup_requires='pytest-runner>=2.0'.split(),
    tests_require='pytest'.split(),
    python_requires='>=3.6',
)
