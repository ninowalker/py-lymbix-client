from setuptools import setup, find_packages
import os.path, sys, subprocess, os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='lymbix',
      version='0.1',
      author = "Nino Walker",
      author_email = "nino.walker@gmail.com",
      description = ("A simple client to the Lymbix REST api."),
      license = "BSD",
      keywords = "lymbix",
      url = "https://github.com/ninowalker/py-lymbix-client",
      packages=['lymbix'],
      long_description=read('README'),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        ],
       
)