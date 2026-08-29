#!/usr/bin/env bash
# alat 4 jedinicni testovi
# pokrece se iz korena uz aktiviran .venv
#   bash tools/unit-tests/run.sh

mkdir -p tools/unit-tests/results

# --cov meri pokrivenost a tee cuva izlaz
python -m pytest tests/unit --cov=ChatterBot/chatterbot --cov-report=term-missing --cov-report=html:tools/unit-tests/results/htmlcov | tee tools/unit-tests/results/izvestaj.txt
