#!/usr/bin/env bash
# Alat 5: mypy, provera tipova bez pokretanja koda.
#   bash tools/mypy/run.sh

mkdir -p tools/mypy/results

# ignore-missing-imports jer biblioteke poput spacy-ja nemaju opise tipova
python -m mypy --ignore-missing-imports --show-error-codes ChatterBot/chatterbot | tee tools/mypy/results/izvestaj.txt
