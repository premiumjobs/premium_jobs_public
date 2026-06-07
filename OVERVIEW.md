# Premium Jobs — Project Overview

## What is this?

Premium Jobs is a **custom Odoo 17 module** that turns Odoo into a multi-tenant recruitment platform. It is built for an Israeli staffing/HR company. The system manages job postings, candidate pipelines, freelancer submissions, and commission/payment tracking — all inside Odoo's framework.

The repo contains **only the custom code**. Odoo 17 source code, the database, and the filestore must be obtained separately.

---

## Architecture

### Layer diagram

```
┌─────────────────────────────────────────────────────────┐
│  Public Website          Freelancer Portal    Admin CRM  │
│  /jobs  /jobs/<id>       /my/jobs  /my/apps   /web       │
└──────────────┬────────────────────┬──────────────┬───────┘
               │                    │              │
┌──────────────▼────────────────────▼──────────────▼───────┐
│                    Controllers (HTTP routes)               │
│  PremiumJobsController   FreelancerPortal   WebsiteCtrl   │
└──────────────────────────────┬────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────┐
│                    Odoo ORM Models                         │
│  hr.job  hr.applicant  res.partner  freelancer.payment     │
│  premium.commission  hr.job.category  hr.applicant.status  │
└──────────────────────────────┬────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────┐
│  PostgreSQL  ·  Odoo filestore (uploaded files/images)     │
└────────────────────────────────────────────────────────────┘
```

### Custom addons

| Addon | Purpose |
|---|---|
| `addons/premium_jobs/` | Main module — all business logic, models, views, controllers |
| `addons/web_overrides/` | Replaces Odoo's default logo/icons with Premium Jobs branding |

---

## Core concepts

### Tenants

A **tenant** is a client company (`res.partner` with `is_tenant = True`). Each job and each application is tied to a tenant. This is the central multi-tenancy hook — not Odoo's built-in multi-company.

- Tenants have a `tenant_slug` (unique URL-friendly identifier) and a subscription status (`trial / active / expired / suspended`).
- When you create a job and select a tenant, the tenant's address auto-fills the job's work location.

### User roles

Defined in `security/security.xml` — four custom security groups:

| Group XML ID | Role | Inherits from |
|---|---|---|
| `group_premium_super_admin` | Super Administrator | `base.group_system` (full Odoo admin) |
| `group_premium_coordinator` | Hiring Coordinator | `hr_recruitment.group_hr_recruitment_manager` |
| `group_premium_client` | Client | `base.group_user` (internal user) |
| `group_premium_freelancer` | Freelancer | `base.group_portal` (portal user) |
| `group_premium_finance_manager` | Finance Manager | standalone |

### The business flow

```
Tenant (client company)
  └── Job (hr.job)  ← has freelancer_reward, publish flags, coordinator
        └── Application (hr.applicant)
              ├── source_type: job_portal / freelancer / direct_apply / ...
              ├── submitted_by_freelancer_id → res.partner (is_freelancer=True)
              └── On stage → "Hired":
                    └── auto-creates → FreelancerPayment (if freelancer + reward set)
```

---

## Data models

### `hr.job` (extended)

The job position. Key additions beyond standard Odoo:

- `tenant_id` — which client company owns this job
- `activity_status` — `active / paused / closed` (separate from Odoo's publish flag)
- `publish_to_job_portal` / `publish_to_freelancer_portal` — controls where the job appears
- `freelancer_reward` — monetary reward triggered on hire
- `company_commission` / `freelancer_commission` / `net_income` — financial terms
- `assigned_freelancer_ids` — M2M to specific freelancers who can see this job
- `approval_status` — `draft / pending / approved / rejected`
- Many Israeli-specific fields: language requirements (Hebrew, Arabic, Russian…), filtering fields (`min_wage`, `max_wage`, `no_gender`, etc.)

### `hr.applicant` (extended)

The candidate/application. Key additions:

- `tenant_id` — auto-populated from the job's tenant on create
- `submitted_by_freelancer_id` — which freelancer submitted this candidate
- `source_type` — `job_portal / freelancer / direct_apply / referral / linkedin / other`
- `commission_id` — link to `premium.commission` if hired
- `status_history_ids` — O2M to `hr.applicant.status.history` for a full audit trail

**Critical behavior in `write()`:** When `stage_id` changes to a stage named `"Hired"` (or any `fold=True` stage) AND there is a `submitted_by_freelancer_id` AND the job has a `freelancer_reward`, the system **auto-creates a `freelancer.payment` record**. This is the core business automation.

### `res.partner` (extended)

Used for both tenants and freelancers:

- `is_tenant` / `is_freelancer` — boolean flags
- Portal users auto-get `is_freelancer = True` on create/write
- Deleting a tenant that has active jobs raises a `UserError` (guard in `unlink()`)
- `tenant_slug` has a unique SQL constraint

### `freelancer.payment`

Tracks money owed to a freelancer after a successful hire.

- `amount` is a related field from `job_id.freelancer_reward` (read-only, comes from the job)
- `is_paid` + `payment_date` track settlement
- Inherits `mail.thread` so it has chatter/activity support

### `premium.commission`

A separate commission record (distinct from `freelancer.payment`) for tracking the company's commission from the client:

- `company_commission` − `freelancer_commission` = `net_company_income`
- Has its own sequence for reference numbers
- Status: `pending / approved / paid / disputed`

---

## Controllers & URL routes

| URL pattern | Auth | Controller | What it does |
|---|---|---|---|
| `/jobs`, `/jobs/page/<n>` | public | `PremiumJobsController` | Public job listing, extends Odoo's default, adds `category_id` filter |
| `/my/jobs` | portal user | `FreelancerPortal` | Freelancer's job board |
| `/my/jobs/<id>` | portal user | `FreelancerPortal` | Job detail + apply form |
| `/my/jobs/<id>/apply` | portal user (POST) | `FreelancerPortal` | Submit application with resume upload |
| `/my/applications` | portal user | `FreelancerPortal` | Freelancer's submitted applications |
| `/my/applications/<id>` | portal user | `FreelancerPortal` | Application detail + chatter |
| `/my/applications/<id>/message` | portal user (POST) | `FreelancerPortal` | Post message to application chatter |
| `/my/applications/export/csv` | portal user | `FreelancerPortal` | Export applications to CSV (Hebrew Excel-compatible) |
| `/my/applications/export/excel` | portal user | `FreelancerPortal` | Export applications to XLSX (RTL, Hebrew) |
| `/my/jobs/export/csv` + `/excel` | portal user | `FreelancerPortal` | Export job list |

---

## Static assets

| File | Purpose |
|---|---|
| `static/src/css/website_style.css` | Public job portal frontend styles |
| `static/src/css/homepage_style.css` | Homepage styles |
| `static/src/css/premium_form.css` | Backend form styles |
| `static/src/css/rtl_fixes.css` | RTL (Hebrew/Arabic right-to-left) corrections for both frontend and backend |
| `static/src/js/hide_interface_elements.js` | Hides/shows Odoo UI elements based on user role (loaded in backend) |
| `static/src/js/skills_fix.js` | Fixes Odoo's skills widget behavior |

---

## Critical things to know before working on this project

### 1. This is Odoo — learn Odoo first

Everything follows Odoo 17 conventions: ORM (`_inherit`, `_name`, fields API), XML views, QWeb templates, security rules. If you are new to Odoo, the most important things to understand before touching code:

- `_inherit` vs `_name` — extending vs creating a model
- How `@api.depends`, `@api.onchange`, `@api.model` work
- The difference between `sudo()` and normal recordsets
- How `ir.rule` (record rules) and `res.groups` control data access
- XML `<record>` syntax and `noupdate="1"` — data that won't re-apply on upgrade

### 2. The `tenant_id` is not Odoo's multi-company

Odoo has a built-in `company_id` multi-company system. This project adds its own `tenant_id` layer on top. Do not confuse them. Always check which field a query/domain is using. Some places fall back to `company_id` if `tenant_id` is absent (see portal controller line ~183).

### 3. The hired-stage trigger is fragile

The auto-payment creation in `hr.applicant.write()` matches stage by `stage.name == 'Hired'`. If someone renames that stage in the Odoo backend, the automation silently breaks. If you add or change hire-stage logic, search for this string and be aware there is no `fold`-only fallback — there's an `or` check but both branches need to be valid.

### 4. Language: Hebrew + Russian + English mixed in code

Field labels, error messages, and some comments are in Hebrew (`שם`, `משרה`, `מועמד`). Some comments are in Russian. UI-facing strings in controllers are mostly Hebrew. This is intentional — the platform is built for the Israeli market. Do not "fix" Hebrew labels unless asked.

### 5. `sudo()` is used broadly in portal controllers

Freelancers (portal users) have very limited ORM access by default. The controllers use `.sudo()` extensively to read models the portal user can't normally access (payments, messages, attachments). Be careful when adding new data access in portal routes — always think about whether the user should see that data, and scope your `sudo()` call as narrowly as possible.

### 6. Module update is required after any XML or Python change

Odoo caches views and data in the database. After changing:
- Python models → restart Odoo (`-u premium_jobs` not always needed, but helps)
- XML views/templates → must run with `-u premium_jobs`
- CSS/JS assets → must clear asset cache (`delete from ir_attachment where url like '/web/assets/%'`) or run with `-u premium_jobs`

### 7. `noupdate="1"` data will not re-apply

The security groups and record rules in `security/security.xml` and `data/*.xml` that are wrapped in `<data noupdate="1">` **will not be re-applied** if they already exist in the database. If you need to update them, do it through the Odoo UI or delete them from the DB before upgrading.

### 8. The `web_overrides` addon contains only images

`addons/web_overrides/` only overrides Odoo's default logos/icons. It has no Python code. It must be in the `addons_path` for branding to work, but it doesn't affect any business logic.

### 9. `xlsxwriter` is a required non-standard dependency

The export-to-Excel feature in the portal controller uses `xlsxwriter`. This package must be installed in the virtual environment (`pip install xlsxwriter`). It is not in Odoo's default `requirements.txt`.

---

## File structure reference

```
addons/
├── premium_jobs/
│   ├── __manifest__.py          # Module declaration, dependencies, asset bundles
│   ├── models/
│   │   ├── hr_job.py            # Job position extensions (largest model file)
│   │   ├── hr_applicant.py      # Candidate + PremiumCommission models
│   │   ├── res_partner.py       # Tenant + Freelancer extensions
│   │   ├── res_users.py         # User type + freelancer stats
│   │   ├── freelancer_payment.py
│   │   ├── job_category.py      # hr.job.category model
│   │   ├── applicant_status_history.py
│   │   ├── hr_job_website.py    # Website publication helpers
│   │   ├── hr_employee.py       # Minor employee extensions
│   │   ├── ir_http.py           # HTTP middleware (adds context vars)
│   │   └── mail_bot.py          # OdooBot customization
│   ├── controllers/
│   │   ├── jobs_controller.py   # Public /jobs route with category filter
│   │   ├── portal_freelancer.py # All /my/* portal routes (largest controller)
│   │   └── website.py           # Homepage controller
│   ├── views/
│   │   ├── hr_job_views.xml     # Backend job form/list views
│   │   ├── hr_applicant_views.xml
│   │   ├── freelancer_payment_views.xml
│   │   ├── website_templates.xml    # Public job portal QWeb templates
│   │   ├── homepage_template.xml    # Homepage QWeb template
│   │   ├── portal_freelancer_templates.xml  # /my/* QWeb templates
│   │   ├── backend_templates.xml
│   │   ├── menu_views.xml       # Backend menu structure
│   │   └── res_partner_views.xml
│   ├── security/
│   │   ├── security.xml         # Groups + record rules
│   │   └── ir.model.access.csv  # Model-level CRUD permissions per group
│   ├── data/
│   │   ├── job_categories.xml   # Seed data: job category list
│   │   ├── web_branding.xml     # System name / favicon overrides
│   │   ├── interface_visibility.xml  # Ir.config_parameter entries
│   │   └── odoobot_override.xml
│   └── static/
│       └── src/
│           ├── css/             # Frontend + backend styles + RTL fixes
│           └── js/              # UI element hiding + skills fix
└── web_overrides/
    ├── static/img/              # Replacement logo files
    └── views/webclient_templates.xml  # Injects replacement logos
```

---

---

# Setup & Running

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10 or 3.11 | Odoo 17 does **not** support Python 3.13 |
| PostgreSQL | 14+ | Must be running before starting Odoo |
| Odoo 17 source | branch `17.0` | Not included in this repo — get separately |
| Node.js / npm | 18+ | Required by Odoo 17 asset pipeline |
| wkhtmltopdf | 0.12.6 | Optional — only needed for PDF reports |
| xlsxwriter (Python) | any | Required for Excel export in the freelancer portal |

---

## First-time setup

### 1. Get Odoo 17 source

Place it next to `addons/` inside the project root. The `start_odoo.sh` scripts expect it at `odoo_source/`.

```bash
git clone https://github.com/odoo/odoo.git --branch 17.0 --depth 1 odoo_source
```

### 2. Create the Python virtual environment

```bash
python3.11 -m venv odoo_venv
source odoo_venv/bin/activate          # Linux/Mac
# odoo_venv\Scripts\activate           # Windows

pip install -r odoo_source/requirements.txt
pip install xlsxwriter                 # not in Odoo's requirements
```

### 3. Create PostgreSQL user and database

```sql
CREATE USER premium_jobs_user WITH PASSWORD 'premium123';
CREATE DATABASE premium_jobs_local OWNER premium_jobs_user;
```

Or as a shell one-liner:

```bash
psql postgres -c "CREATE USER premium_jobs_user WITH PASSWORD 'premium123';"
psql postgres -c "CREATE DATABASE premium_jobs_local OWNER premium_jobs_user;"
```

### 4. Create `config/odoo.conf`

Copy the example and fill in real paths:

```bash
cp config/odoo.conf.example config/odoo.conf
```

Minimal working config:

```ini
[options]
addons_path = /absolute/path/to/odoo_source/addons,/absolute/path/to/this/repo/addons

admin_passwd = your_master_password

db_host = localhost
db_port = 5432
db_user = premium_jobs_user
db_password = premium123
db_name = premium_jobs_local

data_dir = /absolute/path/to/this/repo/data_dir

http_port = 8069
workers = 0

log_level = info
logfile = /absolute/path/to/this/repo/logs/odoo.log
```

> **`addons_path` must include both** the Odoo standard addons and this repo's `addons/` folder, or the module won't be found.

### 5. Create required directories

```bash
mkdir -p data_dir logs database
```

### 6. Start Odoo and install the module

```bash
source odoo_venv/bin/activate
python odoo_source/odoo-bin -c config/odoo.conf
```

Go to `http://localhost:8069`, log in as `admin`, then install the `premium_jobs` module from Apps.

---

## Daily workflow

### Starting and stopping

```bash
# Start
python odoo_source/odoo-bin -c config/odoo.conf

# Stop
pkill -f "odoo-bin"

# Or use the included script (Linux/Mac only — paths are hardcoded)
./start_odoo.sh
```

### After making changes

| What changed | Command |
|---|---|
| Python model/controller | Restart Odoo (no `-u` needed for logic-only changes) |
| XML views / QWeb templates | `python odoo-bin -c config/odoo.conf -u premium_jobs` |
| CSS / JS assets | Clear asset cache (see below) then `-u premium_jobs` |
| Security XML (`noupdate="0"`) | `-u premium_jobs` |
| `data/*.xml` with `noupdate="1"` | Won't re-apply — must delete the records manually in DB first |

### Clearing the asset cache

Odoo caches compiled CSS/JS bundles in the database. After changing any static file, the old bundle keeps serving until cleared:

```bash
# Via psql
psql -U premium_jobs_user -d premium_jobs_local \
  -c "DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';"

# Or (from Makefile target)
psql -U premium_jobs_user -d premium_jobs_local -c "DELETE FROM ir_asset;"
```

Then restart with `-u premium_jobs`.

### Full update (after CSS/JS changes)

```bash
pkill -f "odoo-bin"
psql -U premium_jobs_user -d premium_jobs_local -c "DELETE FROM ir_asset;"
python odoo_source/odoo-bin -c config/odoo.conf -u web,website,premium_jobs
```

---

## Makefile commands (Linux/Mac)

The `Makefile` wraps common operations. It calls `./start_odoo.sh` which has hardcoded paths — update them before use.

```bash
make start        # Start Odoo
make stop         # Kill odoo-bin process
make restart      # stop + start
make update       # stop + start -u premium_jobs
make update-full  # stop + clear ir_asset cache + start -u web,website,premium_jobs
make logs         # tail -f logs/odoo.log
make clear-cache  # DELETE FROM ir_asset
make backup       # pg_dump to database/backup_YYYYMMDD_HHMMSS.sql
make status       # Check if odoo-bin is running + PostgreSQL status
```

---

## Access URLs

| URL | What it is |
|---|---|
| `http://localhost:8069` | Public job portal (redirects to `/he` for Hebrew homepage) |
| `http://localhost:8069/jobs` | Public job listing page |
| `http://localhost:8069/web` | Backend CRM (admin panel) |
| `http://localhost:8069/web/login` | Login page |
| `http://localhost:8069/my` | Freelancer portal home |
| `http://localhost:8069/my/jobs` | Freelancer job board |
| `http://localhost:8069/my/applications` | Freelancer's submitted applications |

Default login: `admin` / (password set during Odoo database init or from existing DB dump).

---

## Database operations

```bash
# Connect to DB interactively
psql -U premium_jobs_user -d premium_jobs_local

# Backup
pg_dump -U premium_jobs_user premium_jobs_local > database/backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U premium_jobs_user -d premium_jobs_local < database/backup_20250101.sql

# Reset admin password (if locked out)
psql -U premium_jobs_user -d premium_jobs_local \
  -c "UPDATE res_users SET password='admin' WHERE login='admin';"
```

---

## Production deployment

Deploys automatically via GitHub Actions when you push to `main`. See [.github/workflows/deploy.yml](.github/workflows/deploy.yml).

The deploy workflow:
1. Runs on a self-hosted Linux runner tagged `prod`
2. `git reset --hard origin/main` in `/opt/odoo/premium_jobs`
3. `sudo systemctl restart odoo`

> This means pushing to `main` = immediate production deploy. Use feature branches and merge carefully.

The production Odoo process is managed by `systemd`. The service config is on the server at `/etc/systemd/system/odoo.service` (not in this repo).

---

## Troubleshooting

### White screen after login

```bash
make clear-cache   # or: DELETE FROM ir_asset in psql
make update-full
```
Then hard-refresh the browser (`Ctrl+Shift+R`).

### Odoo won't start — port in use

```bash
lsof -i :8069          # find what's using the port
pkill -f "odoo-bin"    # kill any leftover Odoo process
```

### Module not found / not appearing in Apps

Check that `addons_path` in `odoo.conf` includes the path to this repo's `addons/` directory.

### PostgreSQL connection refused

```bash
# Mac
brew services start postgresql@14

# Linux/Ubuntu
sudo systemctl start postgresql
```

### View live logs

```bash
tail -f logs/odoo.log
# or
make logs
```

### Translations / Hebrew text broken

The system runs in Hebrew (`he` locale). If you see broken characters in logs or the UI:
- Ensure your terminal supports UTF-8
- Check that the `he` language is installed in Odoo: Settings → Translations → Languages

---

## Interface Visibility Control

The project has a dedicated system for hiding/showing Odoo backend UI elements without touching Odoo source. See [Interface_Visibility_Control.md](Interface_Visibility_Control.md) for the full guide.

The short version:

- **Hide a menu item or form field** → edit `data/interface_visibility.xml`, add an `ir.ui.menu` or `ir.ui.view` override record, then `make update`
- **Hide a dynamic JS element** (profile menu items, dashboard widgets) → edit `static/src/js/hide_interface_elements.js`, call `registry.category("user_menuitems").remove("element_id")`, then `make update`
- To find an element's XML ID: enable Debug Mode in Odoo → hover the element → "View Metadata"
