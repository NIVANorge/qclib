#!/usr/bin/env bash


VERSION=$(python setup.py --version)
python setup.py sdist

curl -i -L --fail -F package=@dist/qclib-${VERSION}.tar.gz https://${FURY_TOKEN}@push.fury.io/niva/