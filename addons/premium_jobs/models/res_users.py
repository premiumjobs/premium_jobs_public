# -*- coding: utf-8 -*-
from odoo import models, api, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    birthday = fields.Date(string='תאריך לידה')

    premium_user_type = fields.Char(
        string='סוג משתמש',
        compute='_compute_premium_user_type',
    )

    # Freelancer statistics
    submitted_applicants_count = fields.Integer(
        string='מועמדים שהוגשו',
        compute='_compute_freelancer_stats',
    )
    hired_applicants_count = fields.Integer(
        string='מועמדים שהתקבלו',
        compute='_compute_freelancer_stats',
    )
    pending_commission_total = fields.Monetary(
        string='עמלות לתשלום',
        compute='_compute_freelancer_stats',
        currency_field='company_currency_id',
    )
    paid_commission_total = fields.Monetary(
        string='עמלות ששולמו',
        compute='_compute_freelancer_stats',
        currency_field='company_currency_id',
    )
    total_commission_amount = fields.Monetary(
        string='סך עמלות',
        compute='_compute_freelancer_stats',
        currency_field='company_currency_id',
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_company_currency',
    )

    def _compute_company_currency(self):
        for user in self:
            user.company_currency_id = user.company_id.currency_id or self.env.company.currency_id

    @api.depends('partner_id')
    def _compute_freelancer_stats(self):
        HrApplicant = self.env['hr.applicant']
        FreelancerPayment = self.env['freelancer.payment']

        for user in self:
            partner = user.partner_id
            if not partner:
                user.submitted_applicants_count = 0
                user.hired_applicants_count = 0
                user.pending_commission_total = 0
                user.paid_commission_total = 0
                user.total_commission_amount = 0
                continue

            submitted = HrApplicant.search_count([
                ('submitted_by_freelancer_id', '=', partner.id)
            ])
            hired = HrApplicant.search_count([
                ('submitted_by_freelancer_id', '=', partner.id),
                ('stage_id.fold', '=', True),
            ])

            payments = FreelancerPayment.search([
                ('freelancer_id', '=', partner.id)
            ])
            pending = sum(p.amount for p in payments if not p.is_paid)
            paid = sum(p.amount for p in payments if p.is_paid)

            user.submitted_applicants_count = submitted
            user.hired_applicants_count = hired
            user.pending_commission_total = pending
            user.paid_commission_total = paid
            user.total_commission_amount = pending + paid

    @api.depends('groups_id')
    def _compute_premium_user_type(self):
        freelancer_group = self.env.ref('premium_jobs.group_premium_freelancer', raise_if_not_found=False)
        coordinator_group = self.env.ref('premium_jobs.group_premium_coordinator', raise_if_not_found=False)
        client_group = self.env.ref('premium_jobs.group_premium_client', raise_if_not_found=False)

        for user in self:
            types = []
            if freelancer_group and freelancer_group in user.groups_id:
                types.append('פרילנסר')
            if coordinator_group and coordinator_group in user.groups_id:
                types.append('רכז גיוס')
            if client_group and client_group in user.groups_id:
                types.append('לקוח CRM')
            user.premium_user_type = ' | '.join(types) if types else ''

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            if user.share and not user.groups_id:
                portal_group = self.env.ref('base.group_portal')
                if portal_group:
                    user.write({'groups_id': [(4, portal_group.id)]})
        return users
