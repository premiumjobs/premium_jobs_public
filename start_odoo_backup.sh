#!/bin/bash

# Activate virtual environment
source /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT/odoo_venv/bin/activate

# Start Odoo
python3 /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT/odoo_source/odoo-bin \
    -c /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT/config/odoo.conf \
    "$@"

