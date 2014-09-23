#!/usr/bin/env python

from setuptools import setup
import sys

install_requires=[
    'setuptools',
    'docopt',
    'xlrd',
    'xlwt',
]
if sys.version_info <= (3,):
    install_requires.append('simplejson')

setup(
    name='json-squared',
    version='0.1',
    description='Convert JSON to easily editable CSV/XLS',
    license='MIT',
    author='Ian Ward',
    author_email='ian@excess.org',
    url='https://github.com/wardi/json-squared',
    packages=['jsonsquared'],
    install_requires=install_requires,
    test_suite='jsonsquared.tests',
    zip_safe=False,
    entry_points = """
        [console_scripts]
        json2=jsonsquared.json2:main
        unjson2=jsonsquared.unjson2:main
        """
    )
