import linecache
from setuptools import find_packages, setup

setup(
    name='spyq',
    packages=find_packages(include=['spyq']),
    version='0.0.1',
    description='Structured Python Queries',
    license='MIT'
)
