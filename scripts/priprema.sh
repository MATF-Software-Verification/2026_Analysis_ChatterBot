#!/usr/bin/env bash
# instalira sve sto je potrebno za pokretanje alata
#
# pre ovoga treba napraviti i aktivirati virtuelno okruzenje:
#   python -m venv .venv
#   .venv/Scripts/activate       (Windows)
#   source .venv/bin/activate    (Linux)
#
# pokretanje:  bash scripts/priprema.sh

# preuzimanje submodula
git submodule update --init --recursive

# ChatterBot se instalira iz submodula
python -m pip install --upgrade pip
python -m pip install -e "./ChatterBot[dev]"
python -m pip install -r requirements.txt

# spaCy model za engleski
python -m spacy download en_core_web_sm
