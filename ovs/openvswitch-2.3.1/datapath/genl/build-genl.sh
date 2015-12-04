#!/bin/sh

version=2.6
if [ $# -eq 1 ]; then
    version=$1
fi

gcc -Wall -fpic -shared  -I/usr/include/python${version} genl.c -o genl.so

