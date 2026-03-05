# -*- coding: utf-8 -*-
"""Premium Jobs - Homepage Controller"""

from odoo import http
from odoo.http import request


class PremiumHomepage(http.Controller):
    """Контроллер главной страницы"""
    
    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        """Главная страница сайта"""
        
        # Получаем последние вакансии
        latest_jobs = request.env['hr.job'].sudo().search(
            [('is_published', '=', True)], 
            limit=6, 
            order='create_date desc'
        )
        
        # Получаем все категории
        categories = request.env['hr.job.category'].sudo().search([])
        
        return request.render('premium_jobs.homepage_direct', {
            'latest_jobs': latest_jobs,
            'categories': categories,
        })

