#!/usr./bin/env bash

# Common shell script messaging

log() {
    if [ "${VERBOSE:-false}" = true ]; then echo "[${SCRIPT_NAME}] $*"; fi
}

step() {
    echo "🔹 $*"
}

error_exit() {
    echo " $*" >&2
    exit 1
}