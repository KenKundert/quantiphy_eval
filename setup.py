from setuptools import setup

with open('README.rst', encoding="UTF-8") as f:
    readme = f.read()


setup(
    name = 'quantiphy_eval',
    version = '0.4.0',
    description = 'calculations with physical quantities',
    long_description = readme,
    long_description_content_type = 'text/x-rst',
    author = "Ken Kundert",
    author_email = 'quantiphy@nurdletech.com',
    url = 'https://github.com/kenkundert/quantiphy_eval',
    download_url = 'https://github.com/kenkundert/quantiphy_eval/tarball/master',
    license = 'MIT',
    py_modules = 'quantiphy_eval'.split(),
    install_requires = 'inform>=1.23 quantiphy>=2.13 sly>=0.4'.split(),
    python_requires = '>=3.6',
    zip_safe = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering',
    ],
)
