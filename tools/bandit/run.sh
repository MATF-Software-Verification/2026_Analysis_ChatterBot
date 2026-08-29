#!/usr/bin/env bash
# Alat 6: bandit, trazi poznate bezbednosne obrasce u kodu.
#   bash tools/bandit/run.sh

mkdir -p tools/bandit/results

python -m bandit -r ChatterBot/chatterbot | tee tools/bandit/results/izvestaj.txt

# provera bandit-ovog najozbiljnijeg nalaza: da li je zastita zaista probojna
python tools/bandit/poc_path_traversal.py | tee tools/bandit/results/poc_izlaz.txt
