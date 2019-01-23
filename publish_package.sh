#!/usr/bin/env bash


set -x 
VERSION=$(python setup.py --version)
python setup.py sdist

$file = "dist/qclib-${VERSION}.tar.gz"
echo "uploading package $file"

curl -i --fail -F package=@$file https://${FURY_TOKEN}@push.fury.io/niva/
