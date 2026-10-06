#!/usr/bin/env bash
set -euo pipefail
REF="${1:-main}"

echo "Deploying ref: $REF"
git fetch origin
git checkout "$REF"
git pull origin "$REF"

# Standard Django deployment steps
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
# Restarting services (this may vary by server config)
sudo systemctl restart gunicorn