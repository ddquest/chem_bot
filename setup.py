# -*- coding: utf-8 -*-
import pip

from pip.req import parse_requirements
from setuptools import setup, find_packages

reqs = parse_requirements(
    'requirements.txt',
    session=pip.download.PipSession()
)
install_requires = [str(req.req) for req in reqs]

setup(
    name='chem_bot',
    version='0.99',
    description='Cheminfo bot',
    author='kubor',
    packages=find_packages(),
    install_requires=install_requires,
)
