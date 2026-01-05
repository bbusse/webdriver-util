from __future__ import unicode_literals
from setuptools import setup

setup(
    name='webdriver_util',
    version='0.2.0',
    description='webdriver util',
    url='https://github.com/bbusse/webdriver-util',
    author='Björn Busse',
    author_email='bj.rn@baerlin.eu',
    license='BSD-3-Clause',
    py_modules=['webdriver_util'],
    install_requires=[
        'configargparse>=1.7.1',
        'selenium>=4.36.0',
    ],
    entry_points={
        'console_scripts': [
            'webdriver-util=webdriver_util:main',
        ]
    },
    python_requires='>=3.12',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12',
    ],
    zip_safe=False,
)
