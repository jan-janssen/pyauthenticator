"""
Setuptools based setup module
"""
from setuptools import setup, find_packages
import versioneer


setup(
    name='pyauthenticator',
    version=versioneer.get_version(),
    description='Similar to the Google authenticator just written in python.',
    long_description=open('README.md').read(),
    url='https://github.com/jan-janssen/pyauthenticator',
    author='Jan Janssen',
    author_email='jan.janssen@outlook.com',
    license='BSD',
    packages=find_packages(exclude=["*tests*"]),
    install_requires=[
        'otpauth==2.0.0',
        'qrcode==7.4.2',
        'pyzbar==0.1.9',
        'pillow==9.5.0',
    ],
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        "console_scripts": [
            'pyauthenticator=pyauthenticator.__main__:command_line_parser'
        ]
    }
)
