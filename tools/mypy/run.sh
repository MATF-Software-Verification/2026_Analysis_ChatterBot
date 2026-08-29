#!/usr/bin/env bash
# alat 2 mypy
#   bash tools/mypy/run.sh

mkdir -p tools/mypy/results

# spacy nema opise tipova
python -m mypy --ignore-missing-imports --show-error-codes ChatterBot/chatterbot | tee tools/mypy/results/izvestaj.txt
