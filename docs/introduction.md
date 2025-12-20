# Introduction
This tutorial covers the development of a Python based two factor authentication application, which allows you to 
generate two factor authentication codes from the command line or your python shell. 

## Technical Background
Two factor authentication is helpful as long as two separate devices are used. Still many modern webbrowsers have two 
factor authentication integrated in the auto completion, meaning everybody with access to this webbrowser can access all 
corresponding services. In the same way generating two factor authentication codes from the command line has the same 
risk, still the great advantage is the opportunity to use automation for services which use two factor authentication. 
This is the focus of this tutorial. 

## Libraries
Rather than reinventing the wheel, we are going to use there libraries, which already provide the required functionality, we just have to combine them: 
* [pyotp](https://github.com/pyauth/pyotp) - Python One-Time Password Library
* [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar/) - Read one-dimensional barcodes and QR codes from Python 2 and 3.
* [qrcode](https://github.com/lincolnloop/python-qrcode) - Python QR Code image generator

## Outline