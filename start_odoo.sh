#!/bin/bash
export PATH=/snap/bin:$PATH
export PYTHONPATH="/home/ubuntu/premium_jobs/odoo_source:$PYTHONPATH"
cd /home/ubuntu/premium_jobs
source odoo_venv/bin/activate
python3 odoo_source/odoo-bin -c config/odoo.conf "$@"
