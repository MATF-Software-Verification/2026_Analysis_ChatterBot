#!/usr/bin/env bash
# pokrece svih sest alata, istim redosledom kao u radu
#   bash scripts/pokreni_sve.sh
#
# prvo tri staticka alata, jer se brzo pokrecu i samo citaju kod,
# pa onda testovi

bash tools/flake8/run.sh
bash tools/mypy/run.sh
bash tools/bandit/run.sh

bash tools/unit-tests/run.sh
bash tools/integration-tests/run.sh
bash tools/hypothesis/run.sh
