#!/usr/bin/env bash
# Pokrece svih sest alata jedan za drugim.
#   bash scripts/pokreni_sve.sh

bash tools/unit-tests/run.sh
bash tools/integration-tests/run.sh
bash tools/hypothesis/run.sh
bash tools/flake8/run.sh
bash tools/mypy/run.sh
bash tools/bandit/run.sh
