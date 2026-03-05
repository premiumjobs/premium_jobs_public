Premium Jobs — Local Setup
🎉 Project successfully migrated from Docker!
📍 System access:

🌐 Website (public part):

http://localhost:8069

🔐 CRM (admin panel):

http://localhost:8069/web

http://localhost:8069/web/login

👤 Login credentials:

Email: admin

Password: (your current password from the database)

🚀 System management
Start Odoo:
cd /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT
./start_odoo.sh
Stop Odoo:
# Press Ctrl+C in the terminal where Odoo is running
# Or find the process and stop it:
pkill -f "odoo-bin"
Restart and update a module:
cd /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT
./start_odoo.sh -u premium_jobs
📁 Project structure
PROJECT/
├── odoo_source/          # Odoo 17 source code
├── addons/               # Custom modules
│   ├── premium_jobs/     # Main CRM module
│   └── web_overrides/    # Web interface overrides
├── filestore/            # Files and images
│   └── premium_jobs/     # Database filestore
├── database/             # Database backups
│   └── premium_jobs_export.sql
├── config/               # Configuration
│   └── odoo.conf         # Odoo settings
├── logs/                 # Logs
│   └── odoo.log          # Main log file
├── odoo_venv/            # Python virtual environment
└── start_odoo.sh         # Startup script
🛠 Technical information
Database:

PostgreSQL: localhost:5432

Database: premium_jobs_local

User: premium_jobs_user

Password: premium123

Python environment:

Python version: 3.13

Virtual environment: /PROJECT/odoo_venv/

All dependencies installed

Logs:

Odoo logs: /PROJECT/logs/odoo.log

Logging level: info

📝 Useful commands
Create a new database:
psql postgres -c "CREATE DATABASE new_db OWNER premium_jobs_user;"
Database backup:
pg_dump -U premium_jobs_user premium_jobs_local > backup_$(date +%Y%m%d).sql
Restore database:
psql -U premium_jobs_user premium_jobs_local < backup.sql
View logs in real time:
tail -f /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT/logs/odoo.log
Install additional Python packages:
source /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT/odoo_venv/bin/activate
pip install package_name
⚙️ Configuration (odoo.conf)

Main settings are located in /PROJECT/config/odoo.conf:

Port: 8069

Addons paths: Odoo standard + custom modules

Data directory: /PROJECT/filestore/

Workers: 0 (development mode)

🔧 Development
Editing the code:

All custom modules are located in:

/PROJECT/addons/premium_jobs/
/PROJECT/addons/web_overrides/
After changing the code:

Restart Odoo with the -u module_name flag

Or update via the web interface: Apps → Update Apps List

✅ What was migrated:

✓ Database (30MB)
✓ All custom modules (premium_jobs, web_overrides)
✓ Filestore (all uploaded files)
✓ Odoo configuration
✓ Python dependencies

🚨 Important:

Docker is no longer required — everything runs locally

PostgreSQL must be running — check with: brew services list

The virtual environment is activated automatically via start_odoo.sh

Port 8069 must be free — close other Odoo instances

📞 Support / Troubleshooting:

If you run into issues:

Check logs: tail -50 /PROJECT/logs/odoo.log

Ensure PostgreSQL is running: brew services list

Check the port: lsof -i :8069
