#!/usr/bin/env bash

# test.sh - Convenience wrapper for pytest

SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
SCRIPT_NAME="${SCRIPT_NAME%.sh}"

set -euo pipefail

# Set the root dir relative to this script
BFHTW_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
export BFHTW_ROOT_DIR
cd "${BFHTW_ROOT_DIR}" || exit 1

# Paths
LIB_DIR="${BFHTW_ROOT_DIR}/libexec"
SOURCE_DIR="${BFHTW_ROOT_DIR}/core/src"

# Flags
# shellcheck disable=SC2034
VERBOSE=false

# shellcheck disable=SC1091
source "${LIB_DIR}/messages.sh"

export PYTHONPATH="${SOURCE_DIR}:${PYTHONPATH:-}"

usage() {
    echo "Usage: ${SCRIPT_NAME} MODE [--file FILE] [--dir DIR] [--marker MARKER] [--help]"
    echo "  MODE: one of 'core', 'func' or 'all'"
    echo
    echo "Options:"
    echo "  --file FILE     Run tests in a specific file within the mode scope"
    echo "  --dir DIR       Run tests in a specific directory within the mode scope"
    echo "  --marker MARKER Only run tests marked with @pytest.mark.<MARKER>"
    echo "  --live          Allow tests marked with @pytest.mark.live to execute"
    echo "  --help          Show this help message"
    echo
    echo "NOTE: 'live' tests will never run unless you also use --live"
}

# --- Mode-specific base directories ---
get_base_path() {
    case "$1" in
        core) echo "${BFHTW_ROOT_DIR}/core/tests" ;;
        func) echo "${BFHTW_ROOT_DIR}/functions" ;;
        all)  echo "." ;;
        *)    echo "Unknown mode: ${1}" >&2;;
    esac
}

# --- Argument defaults ---
# Argument defaults
MODE=""
BASE_DIR=""
FILE=""
DIR=""
MARKER=""
LIVE="false"

# --- Parse first positional argument (mode) ---
# Help if no args or any mention of asking for help
if [ "$#" -lt 1 ] || [ "${1}" = "-h" ] || [ "${1}" = "--help" ]; then
    echo "Error: MODE is required."
    usage
    exit 0
fi

MODE="$1"
shift
BASE_DIR="$(get_base_path "$MODE")"

# BASE_DIR will be a valid folder if mode was correct
if [ ! -d "${BASE_DIR}" ]; then
    usage
    exit 1
fi

# --- Parse longopts ---
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --file)   shift; FILE="$1" ;;
        --dir)    shift; DIR="$1" ;;
        --marker) shift; MARKER="$1" ;;
        --live)   LIVE="true" ;;
        --verbose) VERBOSE=true ;;
        --help)   usage; exit 0 ;;
        *)        echo "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
done

# --- Build pytest command ---
CMD=(pytest -s)

if [[ "$LIVE" == "true" ]]; then
    CMD+=("--live")
fi

if [[ -n "$MARKER" ]]; then
    CMD+=("-m" "$MARKER")
fi

if [[ -n "$FILE" ]]; then
    CMD+=("$BASE_DIR/$FILE")
elif [[ -n "$DIR" ]]; then
    CMD+=("$BASE_DIR/$DIR")
else
    CMD+=("$BASE_DIR")
fi

# --- Execute ---
echo "Running: ${CMD[*]}"
"${CMD[@]}"
