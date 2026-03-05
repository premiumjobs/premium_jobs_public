{
    'name': 'Premium Jobs - Recruitment Platform',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Recruitment',
    'summary': 'Multi-tenant recruitment platform with CRM, job portal, and freelancer management',
    'description': """
Premium Jobs - Complete Recruitment Solution
=============================================

Multi-tenant recruitment platform with integrated CRM and HR capabilities:

Features:
---------
* Multi-tenant architecture with data isolation
* Extended job posting management
* Candidate pipeline tracking
* Freelancer portal and management
* Commission and payment tracking
* Public job portal
* Advanced reporting and analytics

Core Modules:
--------------------
* CRM (Customer Relationship Management)
* HR Recruitment
* Contacts
* Sales

This module provides the foundation for Premium Jobs platform.
    """,
    'author': 'Premium Jobs',
    'website': 'https://github.com/yamtihoni/Premium-Jobs',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'hr_recruitment',
        'hr',
        'contacts',
        'web',
        'mail',
        'website',
        'website_hr_recruitment',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/odoobot_override.xml',
        'data/job_categories.xml',
        'data/web_branding.xml',
        'data/interface_visibility.xml',
        'views/menu_views.xml',
        'views/res_partner_views.xml',
        'views/hr_job_views.xml',
        'views/hr_applicant_views.xml',
        'views/freelancer_payment_views.xml',
        'views/website_templates.xml',
        'views/homepage_template.xml',
        'views/backend_templates.xml',
        'views/portal_freelancer_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'premium_jobs/static/src/css/premium_form.css',
            'premium_jobs/static/src/css/rtl_fixes.css',
            'website/static/src/snippets/s_website_form/000.js',
            'premium_jobs/static/src/js/skills_fix.js',
            'premium_jobs/static/src/js/hide_interface_elements.js',
        ],
        'web.assets_frontend': [
            'premium_jobs/static/src/css/website_style.css',
            'premium_jobs/static/src/css/homepage_style.css',
            'premium_jobs/static/src/css/rtl_fixes.css',
            'website/static/src/snippets/s_website_form/000.js',
        ],
    },
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

