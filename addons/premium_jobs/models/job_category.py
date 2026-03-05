# -*- coding: utf-8 -*-
"""
Job Categories and Tags for Premium Jobs
"""

from odoo import models, fields


class HrJobCategory(models.Model):
    """Job Categories"""
    
    _name = 'hr.job.category'
    _description = 'Job Category'
    _order = 'name'
    
    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    parent_id = fields.Many2one('hr.job.category', string='Parent Category')
    child_ids = fields.One2many('hr.job.category', 'parent_id', string='Child Categories')


class HrJobTag(models.Model):
    """Job Tags"""
    
    _name = 'hr.job.tag'
    _description = 'Job Tag'
    _order = 'name'
    
    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string='Active', default=True)

