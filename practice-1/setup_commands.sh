#!/usr/bin/env bash
set -e
sudo groupadd -f developers
sudo useradd -m -s /bin/bash student2 2>/dev/null || true
sudo usermod -aG developers student2
sudo install -d -o root -g developers -m 2775 /srv/shared
sudo chmod g+rwX,o+rX /srv/shared
id student2
ls -ld /srv/shared
