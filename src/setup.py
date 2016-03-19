import os

from setuptools import setup, find_packages


install_requires = (
    "Pillow"
)

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='SmartQQBot',
    version='0.2',
    packages=find_packages(
        here,
        exclude=("tests", ),
    ),
    url='https://github.com/Yinzo/SmartQQBot',
    license='GPL V3',
    author='Yinzo',
    install_requires=install_requires,
    author_email='yinz95@yahoo.com',
    description='A SmartQQ(original web-QQ) bot client.'
)
