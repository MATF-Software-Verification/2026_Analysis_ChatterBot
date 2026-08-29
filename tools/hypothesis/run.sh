#!/usr/bin/env bash
# Alat 3: property-based testovi (Hypothesis).
#   bash tools/hypothesis/run.sh

mkdir -p tools/hypothesis/results

python -m pytest tests/property -v | tee tools/hypothesis/results/izvestaj.txt

# druga skripta pokazuje kako su bagovi u parseru datuma uopste nadjeni
python tools/hypothesis/nadji_kontraprimere.py | tee tools/hypothesis/results/kontraprimeri.txt
