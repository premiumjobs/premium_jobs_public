# -*- coding: utf-8 -*-
"""
Extension of hr.applicant (Candidates) for Premium Jobs
Adds candidate management, status tracking, and freelancer submission
"""

from odoo import models, fields, api


class HrApplicant(models.Model):
    """Extended hr.applicant model for Premium Jobs candidates"""
    
    _inherit = 'hr.applicant'
    
    # Tenant relationship
    tenant_id = fields.Many2one(
        'res.partner',
        string='Tenant',
        domain=[('is_tenant', '=', True)],
        required=True,
        help='Client company (tenant) for this candidate'
    )
    
    # Submission details
    source_type = fields.Selection([
        ('job_portal', 'Job Portal'),
        ('freelancer', 'Freelancer Submission'),
        ('direct_apply', 'Direct Application'),
        ('referral', 'Referral'),
        ('linkedin', 'LinkedIn'),
        ('other', 'Other'),
    ], string='Source Type', default='direct_apply')
    
    submitted_by_freelancer_id = fields.Many2one(
        'res.partner',
        string='Submitted by Freelancer',
        domain=[('is_freelancer', '=', True)],
        help='Freelancer who submitted this candidate'
    )
    
    # Additional contact info
    city = fields.Char(string='City of Residence')
    linkedin_profile = fields.Char(string='LinkedIn Profile')
    
    # Candidate status and tracking
    rejection_reason = fields.Text(string='Rejection Reason')
    
    # Application data
    application_answers = fields.Text(string='Application Answers')
    screening_answers = fields.Text(string='Screening Question Answers')
    
    # Commission tracking
    has_commission = fields.Boolean(
        string='Has Commission',
        compute='_compute_has_commission',
        store=True
    )
    
    commission_id = fields.Many2one(
        'premium.commission',
        string='Commission Record',
        help='Related commission record if candidate was hired'
    )
    
    # Dates
    applied_date = fields.Datetime(string='Applied Date', default=fields.Datetime.now)
    
    # Status History
    status_history_ids = fields.One2many(
        'hr.applicant.status.history',
        'applicant_id',
        string='Status History'
    )
    
    @api.depends('commission_id')
    def _compute_has_commission(self):
        """Check if candidate has commission"""
        for applicant in self:
            applicant.has_commission = bool(applicant.commission_id)
    
    @api.model
    def create(self, vals):
        """Set tenant_id from job if not provided"""
        if 'job_id' in vals and not vals.get('tenant_id'):
            job = self.env['hr.job'].browse(vals['job_id'])
            if job.tenant_id:
                vals['tenant_id'] = job.tenant_id.id
        return super(HrApplicant, self).create(vals)
    
    def write(self, vals):
        """Auto-create freelancer payment when candidate is hired"""
        res = super(HrApplicant, self).write(vals)
        
        # Check if stage changed to "Hired"
        if 'stage_id' in vals:
            for applicant in self:
                stage = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
                
                # If hired and submitted by freelancer with reward
                if (stage.name == 'Hired' or stage.fold) and \
                   applicant.submitted_by_freelancer_id and \
                   applicant.job_id.freelancer_reward:
                    
                    # Check if payment record already exists
                    existing_payment = self.env['freelancer.payment'].search([
                        ('applicant_id', '=', applicant.id)
                    ], limit=1)
                    
                    if not existing_payment:
                        # Create payment record
                        self.env['freelancer.payment'].create({
                            'applicant_id': applicant.id,
                        })
        
        return res


class PremiumCommission(models.Model):
    """Commission tracking for successful placements"""
    
    _name = 'premium.commission'
    _description = 'Premium Jobs Commission'
    _order = 'create_date desc'
    
    name = fields.Char(string='Commission Reference', required=True, copy=False, readonly=True, default='New')
    
    tenant_id = fields.Many2one(
        'res.partner',
        string='Tenant',
        domain=[('is_tenant', '=', True)],
        required=True
    )
    
    job_id = fields.Many2one('hr.job', string='Job Position', required=True)
    applicant_id = fields.Many2one('hr.applicant', string='Candidate', required=True)
    freelancer_id = fields.Many2one(
        'res.partner',
        string='Freelancer',
        domain=[('is_freelancer', '=', True)]
    )
    
    # Commission amounts
    company_commission = fields.Monetary(string='Company Commission', required=True, currency_field='currency_id')
    freelancer_commission = fields.Monetary(string='Freelancer Commission', currency_field='currency_id')
    net_company_income = fields.Monetary(
        string='Net Company Income',
        compute='_compute_net_income',
        store=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # Terms
    warranty_period_days = fields.Integer(string='Warranty Period (Days)')
    warranty_end_date = fields.Date(string='Warranty End Date')
    
    # Status
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('disputed', 'Disputed'),
    ], string='Status', default='pending')
    
    # Dates
    create_date = fields.Datetime(string='Created On', readonly=True)
    approved_date = fields.Datetime(string='Approved On')
    paid_date = fields.Datetime(string='Paid On')
    
    @api.depends('company_commission', 'freelancer_commission')
    def _compute_net_income(self):
        """Calculate net company income"""
        for commission in self:
            company = commission.company_commission or 0
            freelancer = commission.freelancer_commission or 0
            commission.net_company_income = company - freelancer
    
    @api.model
    def create(self, vals):
        """Generate commission reference"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('premium.commission') or 'New'
        return super(PremiumCommission, self).create(vals)

