#!/bin/bash
PROJECT_DIR="/Users/shimiyadan/Documents/APIsoul/לקוחות/עדה סיפאני-אקספלייס/Projects/premium_jobs_public"

cd "$PROJECT_DIR"
source odoo_venv/bin/activate
python odoo_source/odoo-bin -c config/odoo.conf "$@"
