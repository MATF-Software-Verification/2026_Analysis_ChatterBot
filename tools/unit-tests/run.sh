#!/usr/bin/env bash
# Alat 1: jedinicni testovi, uz merenje pokrivenosti koda.
# Pokrece se iz korena repozitorijuma, sa aktiviranim .venv:
#   bash tools/unit-tests/run.sh

mkdir -p tools/unit-tests/results

# --cov meri koje su linije chatterbot-a izvrsene, tee cuva izlaz u fajl
python -m pytest tests/unit --cov=ChatterBot/chatterbot --cov-report=term-missing --cov-report=html:tools/unit-tests/results/htmlcov | tee tools/unit-tests/results/izvestaj.txt
