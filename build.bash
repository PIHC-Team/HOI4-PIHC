#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
HOI4DEV_PATH="$HOME/Utils/HOI4DEV"

if [[ ! -x "$PYTHON_BIN" ]]; then
	cat >&2 <<EOF
[build] Error: expected virtual environment not found at:
		$PYTHON_BIN
[build] Please create it once via:
		conda create -p "$VENV_DIR" python=3.10
		conda run -p "$VENV_DIR" python -m pip install -r requirements.txt
		conda run -p "$VENV_DIR" python -m pip install -e ~/Utils/HOI4DEV
EOF
	exit 1
fi

export KMP_DUPLICATE_LIB_OK="${KMP_DUPLICATE_LIB_OK:-TRUE}"

if [[ -z "${OMP_NUM_THREADS:-}" ]]; then
	if command -v sysctl >/dev/null 2>&1; then
		export OMP_NUM_THREADS="$(sysctl -n hw.ncpu 2>/dev/null || echo 1)"
	elif command -v nproc >/dev/null 2>&1; then
		export OMP_NUM_THREADS="$(nproc)"
	else
		export OMP_NUM_THREADS="1"
	fi
else
	export OMP_NUM_THREADS
fi

PYTHONPATH_ENTRIES=("$PROJECT_ROOT")
if [[ -d "$HOI4DEV_PATH" ]]; then
	PYTHONPATH_ENTRIES=("$HOI4DEV_PATH" "${PYTHONPATH_ENTRIES[@]}")
fi
if [[ -n "${PYTHONPATH:-}" ]]; then
	PYTHONPATH_ENTRIES+=("$PYTHONPATH")
fi
export PYTHONPATH="$(IFS=:; echo "${PYTHONPATH_ENTRIES[*]}")"

export PATH="$VENV_DIR/bin:${PATH}"

exec "$PYTHON_BIN" "$PROJECT_ROOT/v0.2.3.py" "$@"
