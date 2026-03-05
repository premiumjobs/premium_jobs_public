# -*- coding: utf-8 -*-
"""
Override error messages to replace Odoo with Premium Jobs
"""

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_exception_code_values(cls, exception):
        """Override error messages"""
        code, values = super()._get_exception_code_values(exception)
        
        # Replace "Odoo" with "Premium Jobs" in error messages
        if values.get('name'):
            values['name'] = values['name'].replace('Odoo', 'Premium Jobs')
        
        return code, values

