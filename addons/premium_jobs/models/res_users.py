# -*- coding: utf-8 -*-
from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            if user.share and not user.groups_id:
                portal_group = self.env.ref('base.group_portal')
                if portal_group:
                    user.write({'groups_id': [(4, portal_group.id)]})
        return users
