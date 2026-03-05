# -*- coding: utf-8 -*-

from odoo import models


class OdooBot(models.AbstractModel):
    _inherit = 'mail.bot'

    def _get_answer(self, record, body, values, command=False):
        """Disable all automatic bot messages"""
        # Return False to disable all OdooBot automatic messages
        return False
