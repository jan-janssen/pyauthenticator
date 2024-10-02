"""
Setuptools based setup module
"""
from setuptools import find_packages, setup

import versioneer

setup(
    name='pyauthenticator',
    version=versioneer.get_version(),
    description='Similar to the Google authenticator just written in python.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/jan-janssen/pyauthenticator',
    author='Jan Janssen',
    author_email='jan.janssen@outlook.com',
    license='BSD',
    packages=find_packages(exclude=["*tests*"]),
    install_requires=[
        'pyotp==2.9.0',
        'qrcode==8.0',
        'pyzbar==0.1.9',
        'pillow==10.4.0',
    ],
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        "console_scripts": [
            'pyauthenticator=pyauthenticator.__main__:command_line_parser'
        ]
    }
)
