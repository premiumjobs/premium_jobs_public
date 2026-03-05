# -*- coding: utf-8 -*-
"""
Premium Jobs - Jobs Controller with Category Filtering
Добавляет фильтрацию вакансий по category_id
"""

import logging
from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)


class PremiumJobsController(WebsiteHrRecruitment):
    """Расширенный контроллер вакансий с поддержкой фильтрации по категориям"""
    
    @http.route([
        '/jobs',
        '/jobs/page/<int:page>',
    ], type='http', auth="public", website=True)
    def jobs(self, category_id=None, **kwargs):
        """
        Override метода jobs() для добавления фильтрации по категориям
        
        Параметры:
            category_id: ID категории вакансии для фильтрации
        """
        
        # Если передан category_id, фильтруем по категории
        if category_id:
            try:
                category_id = int(category_id)
                env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
                
                # Получаем категорию
                category = env['hr.job.category'].sudo().browse(category_id)
                
                if category.exists():
                    # Фильтруем вакансии по категории
                    domain = [
                        ('is_published', '=', True),
                        ('main_category_id', '=', category_id)
                    ]
                    
                    Jobs = env['hr.job']
                    jobs = Jobs.sudo().search(domain, order="is_published desc, sequence, no_of_recruitment desc")
                    total = len(jobs)
                    
                    # Пагинация
                    page = kwargs.get('page', 1)
                    pager = request.website.pager(
                        url='/jobs',
                        url_args={'category_id': category_id},
                        total=total,
                        page=page,
                        step=self._jobs_per_page,
                    )
                    offset = pager['offset']
                    jobs = jobs[offset:offset + self._jobs_per_page]
                    
                    # Рендерим страницу
                    return request.render("website_hr_recruitment.index", {
                        'jobs': jobs,
                        'pager': pager,
                        'search_count': total,
                        'category_id': category,
                        # Пустые значения для остальных фильтров
                        'countries': [],
                        'departments': [],
                        'offices': [],
                        'employment_types': [],
                        'country_id': None,
                        'department_id': None,
                        'office_id': None,
                        'contract_type_id': None,
                        'is_remote': False,
                        'is_other_department': False,
                        'is_untyped': None,
                        'search': None,
                        'original_search': None,
                        'count_per_country': {},
                        'count_per_department': {},
                        'count_per_office': {},
                        'count_per_employment_type': {},
                    })
            except (ValueError, TypeError):
                pass
        
        # Если category_id не передан или невалиден, используем стандартное поведение
        return super(PremiumJobsController, self).jobs(**kwargs)

