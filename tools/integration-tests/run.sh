#!/usr/bin/env bash
# Alat 2: integracioni testovi, sa pravom bazom i pravim spaCy modelom.
#   bash tools/integration-tests/run.sh

mkdir -p tools/integration-tests/results

python -m pytest tests/integration --cov=ChatterBot/chatterbot --cov-report=term-missing | tee tools/integration-tests/results/izvestaj.txt
