#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <target_directory>"
    exit 1
fi

TARGET_DIR="$1"

cd $TARGET_DIR || exit 1

filename="na-dataset-lammps-$(date +%Y-%m-%d).zip"
zip -r "${filename}" . \
    -x "*/dump.*" "*/*.json" "*/*.png" "*/log.lammps"

echo "Output compressed to ${filename}"

