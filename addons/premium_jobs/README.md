# Premium Jobs - Recruitment Module

Multi-tenant recruitment platform for recruitment agencies.

## Features

### Multi-Tenancy
- Data isolation per client (tenant)
- Tenant-specific branding
- Subscription management

### Extended Job Management
- Internal and publication job numbers
- Multiple publication channels (job portal, freelancer portal, external sites)
- Advanced job requirements (age, gender, mobility, etc.)
- Commission tracking
- Freelancer assignment

### Candidate Management
- Extended candidate profiles
- Freelancer submission tracking
- Screening questions and answers
- Commission records for successful placements

### Freelancer Portal
- Freelancer profiles with skills and ratings
- Job assignment and management
- Commission tracking

### User Types
- **Super Administrator**: Full system control
- **Hiring Coordinator**: Job and candidate management
- **Client**: Tenant-specific access
- **Freelancer**: Portal access for job submissions

## Installation

### 1. Install Dependencies

```bash
# Install platform dependencies
pip install -r requirements.txt
```

### 2. Add Module to Platform

Module is located in: `odoo/addons/premium_jobs`

### 3. Update Module List

In Premium Jobs:
1. Go to Apps
2. Update Apps List
3. Search for "Premium Jobs"
4. Click Install

### 4. Install Required Modules

The following core modules will be automatically installed:
- CRM
- HR Recruitment
- HR
- Contacts

## Database Structure

### Extended Models

**res.partner** (Contacts):
- Tenant information
- Freelancer profiles
- User type management

**hr.job** (Job Positions):
- Multi-tenant support
- Extended job fields
- Publication settings
- Commission terms
- Freelancer assignment

**hr.applicant** (Candidates):
- Tenant relationship
- Freelancer submission tracking
- Extended application data
- Commission tracking

### New Models

**premium.commission**:
- Commission records
- Payment tracking
- Warranty management

## Configuration

### Setup Tenants

1. Go to Contacts
2. Create new contact
3. Check "Is Tenant"
4. Fill in tenant details (slug, subscription, etc.)

### Setup Freelancers

1. Go to Contacts
2. Create new contact
3. Check "Is Freelancer"
4. Fill in freelancer profile

### Create Jobs

1. Go to Premium Jobs > Jobs
2. Create new job
3. Select tenant
4. Fill in job details
5. Configure publication settings
6. Assign freelancers if needed

## Usage

### For Coordinators

1. Create jobs for clients (tenants)
2. Assign freelancers to jobs
3. Review candidates
4. Track commissions

### For Clients

1. View their jobs
2. Review candidates
3. Track hiring progress

### For Freelancers

1. View assigned jobs
2. Submit candidates
3. Track commissions

## Development

### Extend the Module

Create inherited models in `models/` directory:

```python
from odoo import models, fields

class HrJobExtended(models.Model):
    _inherit = 'hr.job'
    
    custom_field = fields.Char(string='Custom Field')
```

### Add Views

Create XML views in `views/` directory.

### Security

Edit `security/ir.model.access.csv` to add model permissions.

## Architecture

Built on MVC architecture:
- **Models**: `models/` - Business logic and data
- **Views**: `views/` - XML view definitions
- **Security**: `security/` - Access rights and groups
- **Data**: `data/` - Demo and initial data (if needed)

## License

LGPL-3

## Support

GitHub: https://github.com/yamtihoni/Premium-Jobs

