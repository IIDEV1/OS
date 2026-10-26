#!/usr/bin/env bash
set -euo pipefail
src=${1:?source}; dst=${2:?backup}; mkdir -p "$dst"
rsync -a --delete --itemize-changes "$src/" "$dst/" | tee "$dst/backup.log"
