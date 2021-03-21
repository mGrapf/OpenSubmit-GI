#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name = 'opensubmit-exec',
    version = '0.9.9',
    url = 'https://github.com/mGrapf/opensubmit-gi',
    license='AGPL',
    author = 'Mathias Denz',
    description = 'This is a modded executor for the OpenSubmit web application.',
    long_description = '',
    author_email = 'mathias.denz@gmail.com',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4'
    ],

    install_requires=required,
    extras_require={'report-opencl': ["pyopencl"]},
    packages = ['opensubmitexec'],
    package_data = {'opensubmitexec': ['VERSION']},
    entry_points={
        'console_scripts': [
            'opensubmit-exec = opensubmitexec.cmdline:console_script',
        ],
    }
)


