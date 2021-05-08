"""
Setuptools based setup module
"""
from setuptools import setup, find_packages


setup(
    name='twofactorcmd',
    version="0.0.1",
    description='Generate optauth codes as used by two factor authentication',
    url='https://github.com/jan-janssen/twofactorcmd',
    author='Jan Janssen',
    author_email='jan.janssen@outlook.com',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'otpauth',
        'qrcode',
    ],
    entry_points={
        "console_scripts": [
            'twofactorcmd=twofactorcmd.cmd:main'
        ]
    }
)
