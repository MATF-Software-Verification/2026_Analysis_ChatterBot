#!/usr/bin/env bash
# alat 3 bandit
#   bash tools/bandit/run.sh

mkdir -p tools/bandit/results

python -m bandit -r ChatterBot/chatterbot | tee tools/bandit/results/izvestaj.txt

# provera najozbiljnijeg nalaza
python tools/bandit/poc_path_traversal.py | tee tools/bandit/results/poc_izlaz.txt
