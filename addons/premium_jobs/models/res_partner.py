# -*- coding: utf-8 -*-
"""
Extension of res.partner (Contacts) for Premium Jobs
Adds tenant management and multi-tenancy support
"""

from odoo import models, fields, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    """Extended partner model for Premium Jobs tenants and users"""
    
    _inherit = 'res.partner'
    
    # Tenant-specific fields
    is_tenant = fields.Boolean(
        string='Is Tenant',
        default=False,
        help='Indicates if this partner is a Premium Jobs tenant (client company)'
    )
    
    tenant_slug = fields.Char(
        string='Tenant Slug',
        help='URL-friendly identifier for tenant'
    )
    
    subscription_status = fields.Selection([
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ], string='Subscription Status', default='trial')
    
    subscription_start_date = fields.Date(string='Subscription Start Date')
    subscription_end_date = fields.Date(string='Subscription End Date')
    
    privacy_policy_url = fields.Char(string='Privacy Policy URL')
    
    # Tenant branding
    tenant_logo = fields.Binary(string='Tenant Logo', help='Logo for tenant branding')
    tenant_logo_filename = fields.Char(string='Logo Filename')
    
    # User type for Premium Jobs
    premium_user_type = fields.Selection([
        ('super_admin', 'Super Administrator'),
        ('coordinator', 'Hiring Coordinator'),
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    ], string='Premium Jobs User Type')
    
    # Freelancer-specific fields
    is_freelancer = fields.Boolean(string='Is Freelancer', default=False)
    freelancer_skills = fields.Many2many(
        'hr.skill',
        string='Skills',
        help='Freelancer skills and specializations'
    )
    experience_level = fields.Selection([
        ('junior', 'Junior'),
        ('mid', 'Mid-Level'),
        ('senior', 'Senior'),
        ('expert', 'Expert'),
    ], string='Experience Level')
    
    # Currency field for monetary fields
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    hourly_rate = fields.Monetary(string='Hourly Rate', currency_field='currency_id')
    portfolio_url = fields.Char(string='Portfolio URL')
    linkedin_url = fields.Char(string='LinkedIn Profile')
    freelancer_timezone = fields.Selection(
        selection='_get_timezone_list',
        string='Timezone'
    )
    specialization = fields.Char(string='Specialization')
    freelancer_rating = fields.Float(string='Rating', digits=(3, 2))
    successful_projects_count = fields.Integer(string='Successful Projects', default=0)
    
    # Client employee fields
    employee_position = fields.Char(string='Position')
    employee_department = fields.Char(string='Department')
    
    @api.model
    def _get_timezone_list(self):
        """Get list of timezones"""
        import pytz
        return [(tz, tz) for tz in pytz.common_timezones]
    
    @api.model
    def create(self, vals):
        """Auto-set is_freelancer for portal users and company_id from current user"""
        # Auto-set company_id from current user if not specified
        if 'company_id' not in vals and self.env.company:
            vals['company_id'] = self.env.company.id
        
        partner = super(ResPartner, self).create(vals)
        
        # Check if partner has a portal user
        if partner.user_ids:
            for user in partner.user_ids:
                if user.share and not partner.is_freelancer:
                    partner.is_freelancer = True
                    break
        
        return partner
    
    def write(self, vals):
        """Auto-set is_freelancer when portal user is added"""
        res = super(ResPartner, self).write(vals)
        
        # If user_ids were updated, check if any are portal users
        if 'user_ids' in vals or any(self.user_ids):
            for partner in self:
                has_portal_user = any(user.share for user in partner.user_ids)
                if has_portal_user and not partner.is_freelancer:
                    partner.is_freelancer = True
        
        return res
    
    def unlink(self):
        """Prevent deletion of tenant/freelancer if used in jobs"""
        # Check if this partner is used as tenant in any job
        tenant_jobs = self.env['hr.job'].search([('tenant_id', 'in', self.ids)])
        if tenant_jobs:
            job_list = '\n'.join([f"• {job.name}" for job in tenant_jobs[:5]])
            if len(tenant_jobs) > 5:
                job_list += f"\n... ועוד {len(tenant_jobs) - 5} משרות"
            
            raise UserError(
                f"❌ לא ניתן למחוק את הלקוח\n\n"
                f"לקוח זה משמש במשרות הבאות:\n{job_list}\n\n"
                f"💡 קודם כל, מחק או שנה את המשרות האלה,\nואז תוכל למחוק את הלקוח."
            )
        
        return super(ResPartner, self).unlink()
    
    _sql_constraints = [
        ('tenant_slug_unique', 'UNIQUE(tenant_slug)', 'Tenant slug must be unique!'),
    ]

