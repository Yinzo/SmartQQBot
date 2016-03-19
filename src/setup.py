import os

from setuptools import setup, find_packages


install_requires = (
    "Pillow"
)

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='SmartBot',
    version='0.1.1',
    packages=find_packages(
        here,
        exclude=("tests", ),
    ),
    url='https://github.com/BlinkTunnel/SmartQQBot',
    license='GPL V3',
    author='winkidney',
    install_requires=install_requires,
    author_email='winkidney@gmail.com',
    description='A SmartBot(from qq bot) bot client.'
)
