from __future__ import unicode_literals

from setuptools import find_packages, setup

setup(name='webdriver-util',
      version='0.2.0',
      description='webdriver util',
      url='https://github.com/bbusse/webdriver-util',
      author='Björn Busse',
      author_email='bj.rn@baerlin.eu',
      license='BSD 3-Clause License',
      packages=find_packages('.', exclude=['tests']),
      install_requires=["configargparse  >= 1.2.3",
                        "selenium >= 3.141.0"],
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.9",
      ],
      zip_safe=False)
