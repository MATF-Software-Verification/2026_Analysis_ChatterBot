#!/usr/bin/env bash
# Instalira sve sto je potrebno za pokretanje alata.
#
# Pre ovoga treba napraviti i aktivirati virtuelno okruzenje:
#   python -m venv .venv
#   .venv/Scripts/activate       (Windows)
#   source .venv/bin/activate    (Linux, macOS)
#
# Pokretanje:  bash scripts/priprema.sh

# preuzimanje analiziranog projekta (git submodul)
git submodule update --init --recursive

# ChatterBot se instalira iz submodula, alati iz requirements.txt
python -m pip install --upgrade pip
python -m pip install -e "./ChatterBot[dev]"
python -m pip install -r requirements.txt

# spaCy model za engleski, bez njega bot ne moze da se napravi
python -m spacy download en_core_web_sm
