# -*- coding: utf-8 -*-
"""
Extension of hr.employee for Premium Jobs
Handles proper deletion cascade with res.users
"""

from odoo import models, api


class HrEmployee(models.Model):
    """Extended hr.employee model to handle user deletion properly"""
    
    _inherit = 'hr.employee'
    
    def unlink(self):
        """
        Override unlink to properly handle user deletion.
        When deleting an employee, also delete the linked user if exists.
        """
        # Collect linked users before deleting employees
        users_to_delete = self.env['res.users']
        
        for employee in self:
            if employee.user_id:
                # Add to deletion list
                users_to_delete |= employee.user_id
                
                # Temporarily remove the link to avoid FK constraint error
                employee.sudo().write({'user_id': False})
        
        # Delete employees first
        result = super(HrEmployee, self).unlink()
        
        # Then delete the users
        if users_to_delete:
            users_to_delete.sudo().unlink()
        
        return result

