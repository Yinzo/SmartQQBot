import os

from setuptools import setup, find_packages


install_requires = (
    "Pillow",
    "six>=1.10.0",
    "requests>=2.0.0"
)

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='SmartBot',
    version='0.1.1',
    packages=find_packages(
        here,
        exclude=("tests", ),
    ),
    url='https://github.com/Yinzo/SmartQQBot',
    license='GPL V3',
    author='Yinzo',
    install_requires=install_requires,
    author_email='http://yinz.me/',
    description='A SmartBot(from qq bot) bot client.'
)
