"""
Setuptools based setup module
"""
from setuptools import setup, find_packages
import versioneer


setup(
    name='pyauthenticator',
    version=versioneer.get_version(),
    description='Similar to the Google authenticator just written in python.',
    url='https://github.com/jan-janssen/pyauthenticator',
    author='Jan Janssen',
    author_email='jan.janssen@outlook.com',
    license='BSD',
    packages=find_packages(exclude=["*tests*"]),
    install_requires=[
        'otpauth',
        'qrcode',
        'pyzbar',
        'pillow'
    ],
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        "console_scripts": [
            'pyauthenticator=pyauthenticator:main'
        ]
    }
)
