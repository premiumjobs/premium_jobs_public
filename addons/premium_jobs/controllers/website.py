# -*- coding: utf-8 -*-
"""
Website controller for language redirect
Forces Hebrew as default language for entire website
"""

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class WebsiteHebrew(Website):
    """Override website controller to force Hebrew language"""
    
    @http.route()
    def default_lang_redirect(self, **kwargs):
        """Redirect to Hebrew if no language specified"""
        # Get current language from URL
        lang_code = request.context.get('lang')
        
        # If not Hebrew, redirect to Hebrew version
        if lang_code != 'he_IL':
            # Get current URL without language prefix
            current_url = request.httprequest.path
            
            # If URL doesn't start with /he, add it
            if not current_url.startswith('/he'):
                return request.redirect('/he' + current_url, code=301)
        
        return super(WebsiteHebrew, self).default_lang_redirect(**kwargs)
    
    @http.route('/', type='http', auth='public', website=True)
    def index(self, **kw):
        """Homepage - force Hebrew"""
        lang_code = request.context.get('lang')
        
        if lang_code != 'he_IL':
            return request.redirect('/he/', code=301)
        
        return super(WebsiteHebrew, self).index(**kw)

