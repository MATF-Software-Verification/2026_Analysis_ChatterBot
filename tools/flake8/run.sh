#!/usr/bin/env bash
# alat 1 flake8
#   bash tools/flake8/run.sh

mkdir -p tools/flake8/results

# prvo sa pravilima samog projekta
python -m flake8 --config=ChatterBot/setup.cfg ChatterBot/chatterbot | tee tools/flake8/results/projektna_konfiguracija.txt

# pa sa granicom od 100 kolona
python -m flake8 --max-line-length=100 --statistics ChatterBot/chatterbot | tee tools/flake8/results/stroza_konfiguracija.txt
