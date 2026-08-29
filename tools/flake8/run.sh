#!/usr/bin/env bash
# Alat 4: flake8, provera stila i sitnih gresaka u kodu.
#   bash tools/flake8/run.sh

mkdir -p tools/flake8/results

# prvo sa pravilima samog projekta - postuje li projekat svoj standard
python -m flake8 --config=ChatterBot/setup.cfg ChatterBot/chatterbot | tee tools/flake8/results/projektna_konfiguracija.txt

# pa sa strozom granicom od 100 kolona - sta bi prijavio obican PEP8
python -m flake8 --max-line-length=100 --statistics ChatterBot/chatterbot | tee tools/flake8/results/stroza_konfiguracija.txt
