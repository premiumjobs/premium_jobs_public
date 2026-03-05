# -*- coding: utf-8 -*-
"""
Candidate Status History for Premium Jobs
"""

from odoo import models, fields, api


class ApplicantStatusHistory(models.Model):
    """Candidate Status Change History"""
    
    _name = 'hr.applicant.status.history'
    _description = 'Applicant Status History'
    _order = 'change_date desc'
    
    applicant_id = fields.Many2one('hr.applicant', string='Candidate', required=True, ondelete='cascade')
    old_status = fields.Char(string='Previous Status')
    new_status = fields.Char(string='New Status', required=True)
    change_date = fields.Datetime(string='Change Date', required=True, default=fields.Datetime.now)
    changed_by_id = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user)
    comment = fields.Text(string='Comment')

