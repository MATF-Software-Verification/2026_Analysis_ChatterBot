#!/usr/bin/env bash
# alat 6 property-based testovi (Hypothesis)
#   bash tools/hypothesis/run.sh

mkdir -p tools/hypothesis/results

python -m pytest tests/property -v | tee tools/hypothesis/results/izvestaj.txt

# pokazuje kako su nalazi u parseru nastali
python tools/hypothesis/nadji_kontraprimere.py | tee tools/hypothesis/results/kontraprimeri.txt
