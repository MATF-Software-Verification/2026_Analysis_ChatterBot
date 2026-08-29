#!/usr/bin/env bash
# alat 5 integracioni testovi
#   bash tools/integration-tests/run.sh

mkdir -p tools/integration-tests/results

python -m pytest tests/integration --cov=ChatterBot/chatterbot --cov-report=term-missing | tee tools/integration-tests/results/izvestaj.txt
