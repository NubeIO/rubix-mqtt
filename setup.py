from distutils.core import setup
from os.path import join, dirname

import setuptools

import rubix_mqtt

with open(join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(name='rubix-mqtt',
      version=rubix_mqtt.__version__,
      author=rubix_mqtt.__author__,
      description=rubix_mqtt.__doc__.strip(),
      packages=setuptools.find_packages(),
      install_requires=install_requires,
      )
