#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='ImageCapture',
 
      version='0.1',
 
      url='https://github.com/amboxer21/ImageCapturePy',
 
      license='NONE',
 
      author='Anthony Guevara',
 
      author_email='amboxer21@gmail.com',
 
      description='A program to capture a picture and geolocation data upon 3 incorrect 
        attempts at login screen. This data is then e-mailed to you.',
 
      packages=find_packages(exclude=['tests']),
 
      long_description=open('README.md').read(),
 
      zip_safe=True,
 
      setup_requires=['interpy', 'pytailf', 'opencv-python'],
 
      test_suite='nose.collector')
