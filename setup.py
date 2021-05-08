"""
Setuptools based setup module
"""
from setuptools import setup, find_packages
import versioneer


setup(
    name='twofactorcmd',
    version=versioneer.get_version(),
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
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        "console_scripts": [
            'twofactorcmd=twofactorcmd.cmd:main'
        ]
    }
)
