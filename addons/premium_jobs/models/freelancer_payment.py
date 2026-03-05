# -*- coding: utf-8 -*-
"""
Freelancer Payment Tracking
Tracks payments to freelancers for successful hires
"""

from odoo import models, fields, api


class FreelancerPayment(models.Model):
    """Track freelancer payments for successful hires"""
    
    _name = 'freelancer.payment'
    _description = 'Freelancer Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # References
    applicant_id = fields.Many2one(
        'hr.applicant',
        string='מועמדות',
        required=True,
        ondelete='cascade'
    )
    
    job_id = fields.Many2one(
        'hr.job',
        string='משרה',
        related='applicant_id.job_id',
        readonly=True
    )
    
    freelancer_id = fields.Many2one(
        'res.partner',
        string='פרילנסר',
        related='applicant_id.submitted_by_freelancer_id',
        readonly=True
    )
    
    candidate_name = fields.Char(
        string='מועמד',
        related='applicant_id.partner_name',
        readonly=True
    )
    
    # Financial
    amount = fields.Monetary(
        string='סכום תגמול',
        currency_field='currency_id',
        related='job_id.freelancer_reward',
        readonly=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Payment status
    is_paid = fields.Boolean(
        string='שולם',
        default=False,
        tracking=True
    )
    
    payment_date = fields.Date(
        string='תאריך תשלום'
    )
    
    # Additional info
    company_name = fields.Char(
        string='חברה',
        related='job_id.tenant_id.name',
        readonly=True
    )
    
    hire_date = fields.Date(
        string='תאריך גיוס',
        default=fields.Date.today
    )
    
    notes = fields.Text(
        string='הערות'
    )
    
    # Computed
    status_display = fields.Char(
        string='סטטוס תשלום',
        compute='_compute_status_display'
    )
    
    @api.depends('is_paid')
    def _compute_status_display(self):
        """Display payment status"""
        for record in self:
            record.status_display = 'שולם' if record.is_paid else 'ממתין לתשלום'
    
    def action_mark_paid(self):
        """Mark payment as paid"""
        self.write({
            'is_paid': True,
            'payment_date': fields.Date.today()
        })
    
    def action_mark_unpaid(self):
        """Mark payment as unpaid"""
        self.write({
            'is_paid': False,
            'payment_date': False
        })

