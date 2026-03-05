# -*- coding: utf-8 -*-
"""
Extension of hr.job for website functionality
"""

from odoo import models, fields, api


class HrJobWebsite(models.Model):
    """Extended hr.job model for website integration"""
    
    _inherit = 'hr.job'
    
    # Website specific fields
    website_published = fields.Boolean(
        string='Publish on Website',
        default=False,
        help='Make this job visible on the public jobs page'
    )
    
    website_description = fields.Html(
        string='Website Description',
        help='Public description shown on website (different from internal description)'
    )
    
    @api.model
    def _get_jobs_for_website(self, domain=None, limit=None):
        """Get published jobs for website display"""
        base_domain = [('website_published', '=', True)]
        if domain:
            base_domain += domain
        
        jobs = self.search(base_domain, limit=limit, order='create_date desc')
        return jobs
    
    def action_publish_website(self):
        """Publish job to website"""
        for job in self:
            job.website_published = True
    
    def action_unpublish_website(self):
        """Remove job from website"""
        for job in self:
            job.website_published = False


