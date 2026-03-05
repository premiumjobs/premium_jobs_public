# -*- coding: utf-8 -*-
"""
Portal Controller for Freelancers
Allows freelancers to view jobs and submit applications
"""

import base64
import csv
import io
import xlsxwriter
from datetime import datetime
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class FreelancerPortal(CustomerPortal):
    """Portal controller for freelancers"""

    def details_form_validate(self, data, partner_creation=False):
        """Override to ignore avatar_image field in validation"""
        # Remove avatar_image from data before validation
        data_copy = dict(data)
        data_copy.pop('avatar_image', None)
        # Call parent validation
        return super(FreelancerPortal, self).details_form_validate(data_copy, partner_creation)

    def account(self, redirect=None, **post):
        """Override to handle avatar upload"""
        # Handle avatar upload BEFORE calling parent
        avatar_file = request.httprequest.files.get('avatar_image')
        if avatar_file and avatar_file.filename:
            try:
                # Read and encode the image
                avatar_data = base64.b64encode(avatar_file.read())
                partner = request.env.user.partner_id
                # Update partner avatar using sudo
                partner.sudo().write({'image_1920': avatar_data})
            except Exception as e:
                # Log error but don't break the form submission
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f"Avatar upload error: {e}")
        
        # If no redirect specified, stay on the same page
        if not redirect and post:
            redirect = '/my/account'
        
        # Call parent method to handle other fields
        return super(FreelancerPortal, self).account(redirect=redirect, **post)

    def _prepare_home_portal_values(self, counters):
        """Add job count to portal home"""
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        if 'job_count' in counters:
            job_count = request.env['hr.job'].search_count([
                ('website_published', '=', True),
                ('activity_status', '=', 'active')
            ])
            values['job_count'] = job_count
        
        if 'application_count' in counters:
            application_count = request.env['hr.applicant'].search_count([
                ('submitted_by_freelancer_id', '=', partner.id)
            ])
            values['application_count'] = application_count
        
        return values
    
    def _prepare_portal_layout_values(self):
        """Override to add recent messages from contact chatter and financial stats"""
        values = super()._prepare_portal_layout_values()
        
        # Add recent messages from partner's contact page (chatter)
        if request.env.user.has_group('base.group_portal'):
            partner = request.env.user.partner_id
            
            # Get messages from partner's chatter using sudo
            recent_messages = request.env['mail.message'].sudo().search([
                ('model', '=', 'res.partner'),
                ('res_id', '=', partner.id),
                ('message_type', 'in', ['comment', 'email', 'notification']),
            ], order='date desc', limit=10)
            
            values['recent_messages'] = recent_messages
            
            # Calculate financial statistics
            payments = request.env['freelancer.payment'].sudo().search([
                ('freelancer_id', '=', partner.id)
            ])
            
            # 1. Всего за все время (оплачено)
            total_earned_all_time = sum(payments.filtered(lambda p: p.is_paid).mapped('amount'))
            
            # 2. Получено за текущий месяц (оплачено в этом месяце)
            from datetime import datetime
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_earned = sum(payments.filtered(
                lambda p: p.is_paid and p.payment_date and p.payment_date >= current_month_start.date()
            ).mapped('amount'))
            
            # 3. Ожидает оплаты (не оплачено)
            total_pending = sum(payments.filtered(lambda p: not p.is_paid).mapped('amount'))
            
            values.update({
                'total_earned_all_time': total_earned_all_time,
                'monthly_earned': monthly_earned,
                'total_pending': total_pending,
            })
        
        return values

    @http.route(['/my/jobs', '/my/jobs/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_jobs(self, page=1, sortby=None, search=None, date_from=None, date_to=None, company_ids=None, job_ids=None, **kw):
        """Display list of available jobs for freelancers"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')

        values = self._prepare_portal_layout_values()
        
        # Get new jobs (last 6) - always visible
        new_jobs_domain = [
            ('website_published', '=', True),
            ('activity_status', '=', 'active')
        ]
        new_jobs = request.env['hr.job'].search(new_jobs_domain, order='create_date desc', limit=6)
        
        # Domain for all jobs table: only published and recruiting jobs
        domain = [
            ('website_published', '=', True),
            ('activity_status', '=', 'active')
        ]
        
        # Apply filters
        if search:
            domain += [('name', 'ilike', search)]
        
        if date_from:
            domain += [('create_date', '>=', date_from + ' 00:00:00')]
        if date_to:
            domain += [('create_date', '<=', date_to + ' 23:59:59')]
        
        # Company filter
        selected_company_ids = []
        if company_ids:
            if company_ids == '':
                company_ids = None
            else:
                try:
                    selected_company_ids = [int(x) for x in company_ids.split(',') if x]
                    if selected_company_ids:
                        domain += ['|', ('tenant_id', 'in', selected_company_ids), ('company_id', 'in', selected_company_ids)]
                except ValueError:
                    pass
        
        # Job filter
        selected_job_ids = []
        if job_ids:
            if job_ids == '':
                job_ids = None
            else:
                try:
                    selected_job_ids = [int(x) for x in job_ids.split(',') if x]
                    if selected_job_ids:
                        domain += [('id', 'in', selected_job_ids)]
                except ValueError:
                    pass
        
        # Get all companies for filter dropdown
        companies = []
        all_jobs_for_filter = request.env['hr.job'].sudo().search([
            ('website_published', '=', True),
            ('activity_status', '=', 'active')
        ])
        company_set = set()
        for j in all_jobs_for_filter:
            company = j.tenant_id or j.company_id
            if company and company.id not in company_set:
                company_set.add(company.id)
                companies.append({'id': company.id, 'name': company.name})
        companies.sort(key=lambda x: x['name'])
        
        # Get all jobs for filter dropdown
        jobs_list = []
        for j in all_jobs_for_filter:
            jobs_list.append({'id': j.id, 'name': j.name})
        jobs_list.sort(key=lambda x: x['name'])
        
        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('תאריך פרסום'), 'order': 'create_date desc'},
            'name': {'label': _('שם'), 'order': 'name'},
            'reward': {'label': _('תגמול'), 'order': 'freelancer_reward desc'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        # Count jobs
        job_count = request.env['hr.job'].search_count(domain)
        
        # Pager
        pager = portal_pager(
            url="/my/jobs",
            url_args={'sortby': sortby, 'search': search, 'date_from': date_from or '', 'date_to': date_to or '', 
                     'company_ids': company_ids or '', 'job_ids': job_ids or ''},
            total=job_count,
            page=page,
            step=self._items_per_page
        )
        
        # Get jobs for table
        jobs = request.env['hr.job'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'new_jobs': new_jobs,
            'jobs': jobs,
            'job_count': job_count,
            'companies': companies,
            'jobs_list': jobs_list,
            'selected_company_ids': selected_company_ids,
            'selected_job_ids': selected_job_ids,
            'page_name': 'job',
            'pager': pager,
            'default_url': '/my/jobs',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'search': search or '',
            'date_from': date_from,
            'date_to': date_to,
        })
        
        return request.render("premium_jobs.portal_my_jobs", values)

    @http.route(['/my/jobs/<int:job_id>'], type='http', auth='user', website=True)
    def portal_my_job_detail(self, job_id, **kw):
        """Display job details and application form"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        try:
            job = request.env['hr.job'].sudo().browse(job_id)
            if not job.exists() or not job.website_published or job.activity_status != 'active':
                raise MissingError(_("This job is not available."))
        except (AccessError, MissingError):
            return request.redirect('/my/jobs')
        
        # Check if user already applied
        partner = request.env.user.partner_id
        existing_application = False  # Allow multiple applications for freelancers
        
        values = {
            'job': job,
            'page_name': 'job',
            'existing_application': existing_application,
        }
        
        return request.render("premium_jobs.portal_my_job_detail", values)

    @http.route(['/my/jobs/<int:job_id>/apply'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_job_apply(self, job_id, **post):
        """Submit job application"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        try:
            job = request.env['hr.job'].browse(job_id)
            if not job.exists() or not job.website_published or job.activity_status != 'active':
                raise MissingError(_("This job is not available."))
        except (AccessError, MissingError):
            return request.redirect('/my/jobs')
        
        partner = request.env.user.partner_id
        
        # Check if already applied
        existing = request.env['hr.applicant'].search([
            ('job_id', '=', job_id),
            ('submitted_by_freelancer_id', '=', partner.id)
        ], limit=1)
        
        if existing:
            return request.redirect('/my/jobs/%s?error=already_applied' % job_id)
        
        # Handle resume file upload
        resume_file = request.httprequest.files.get('resume')
        attachment_ids = []
        
        if resume_file:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': resume_file.filename,
                'type': 'binary',
                'datas': base64.b64encode(resume_file.read()),
                'res_model': 'hr.applicant',
                'res_id': 0,  # Will be updated after applicant creation
            })
            attachment_ids.append(attachment.id)
        
        # Create application
        vals = {
            'name': post.get('candidate_name'),  # Required field!
            'partner_name': post.get('candidate_name'),
            'email_from': post.get('candidate_email'),
            'partner_phone': post.get('candidate_phone'),
            'linkedin_profile': post.get('linkedin_url', ''),
            'salary_expected': float(post.get('salary_expected', 0)) if post.get('salary_expected') else 0,
            'type_id': int(post.get('degree')) if post.get('degree') else False,
            'job_id': job_id,
            'source_type': 'freelancer',
            'submitted_by_freelancer_id': partner.id,
            'tenant_id': job.tenant_id.id if job.tenant_id else False,
            'description': post.get('cover_letter', ''),
        }
        
        # Create applicant
        try:
            applicant = request.env['hr.applicant'].sudo().create(vals)
            
            # Update attachment with applicant id
            if attachment_ids:
                request.env['ir.attachment'].sudo().browse(attachment_ids).write({
                    'res_id': applicant.id
                })
            
            return request.redirect('/my/jobs/%s?success=1' % job_id)
        except Exception as e:
            return request.redirect('/my/jobs/%s?error=submission_failed' % job_id)

    @http.route(['/my/applications', '/my/applications/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_applications(self, page=1, filterby=None, sortby=None, search=None, date_from=None, date_to=None, company_ids=None, job_ids=None, **kw):
        """Display freelancer's own applications with filters"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        partner = request.env.user.partner_id
        
        # Domain: applications submitted by this freelancer
        domain = [('submitted_by_freelancer_id', '=', partner.id)]
        
        # Filter by payment status
        searchbar_filters = {
            'all': {'label': _('הכל'), 'domain': []},
            'paid': {'label': _('שולם'), 'domain': []},
            'unpaid': {'label': _('ממתין לתשלום'), 'domain': []},
        }
        
        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('תאריך הגשה'), 'order': 'create_date desc'},
            'job': {'label': _('משרה'), 'order': 'job_id'},
            'company': {'label': _('חברה'), 'order': 'tenant_id'},
        }
        
        # Get all unique companies and jobs for this freelancer
        all_applications = request.env['hr.applicant'].search([
            ('submitted_by_freelancer_id', '=', partner.id)
        ])
        
        companies = []
        jobs = []
        seen_companies = set()
        seen_jobs = set()
        
        for app in all_applications:
            company = app.job_id.tenant_id or app.job_id.company_id
            if company and company.id not in seen_companies:
                companies.append({'id': company.id, 'name': company.name})
                seen_companies.add(company.id)
            
            if app.job_id and app.job_id.id not in seen_jobs:
                jobs.append({'id': app.job_id.id, 'name': app.job_id.name})
                seen_jobs.add(app.job_id.id)
        
        # Sort by name
        companies = sorted(companies, key=lambda x: x['name'])
        jobs = sorted(jobs, key=lambda x: x['name'])
        
        # Default values
        if not filterby:
            filterby = 'all'
        if not sortby:
            sortby = 'date'
            
        # Apply filter
        domain += searchbar_filters[filterby]['domain']
        
        # Apply company filter
        if company_ids:
            if isinstance(company_ids, str):
                if company_ids:  # Not empty string
                    company_ids = [int(x) for x in company_ids.split(',') if x]
                else:
                    company_ids = None
            if company_ids:
                domain += ['|', ('job_id.tenant_id', 'in', company_ids), ('job_id.company_id', 'in', company_ids)]
        
        # Apply job filter
        if job_ids:
            if isinstance(job_ids, str):
                if job_ids:  # Not empty string
                    job_ids = [int(x) for x in job_ids.split(',') if x]
                else:
                    job_ids = None
            if job_ids:
                domain += [('job_id', 'in', job_ids)]
        
        # Apply date filters
        if date_from:
            domain += [('create_date', '>=', date_from + ' 00:00:00')]
        if date_to:
            domain += [('create_date', '<=', date_to + ' 23:59:59')]
        
        # Apply search
        if search:
            domain += ['|', '|', 
                      ('job_id.name', 'ilike', search),
                      ('tenant_id.name', 'ilike', search),
                      ('partner_name', 'ilike', search)]
        
        # Get order
        order = searchbar_sortings[sortby]['order']
        
        # Count applications
        application_count = request.env['hr.applicant'].search_count(domain)
        
        # Pager
        pager = portal_pager(
            url="/my/applications",
            url_args={'filterby': filterby, 'sortby': sortby, 'search': search, 
                     'company_ids': ','.join(map(str, company_ids)) if company_ids else '',
                     'job_ids': ','.join(map(str, job_ids)) if job_ids else '',
                     'date_from': date_from or '',
                     'date_to': date_to or ''},
            total=application_count,
            page=page,
            step=self._items_per_page
        )
        
        # Get applications
        applications = request.env['hr.applicant'].search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        # Post-filter by payment status if needed
        if filterby in ['paid', 'unpaid']:
            filtered_apps = []
            for app in applications:
                payment = request.env['freelancer.payment'].sudo().search([
                    ('applicant_id', '=', app.id)
                ], limit=1)
                if filterby == 'paid' and payment and payment.is_paid:
                    filtered_apps.append(app)
                elif filterby == 'unpaid' and payment and not payment.is_paid:
                    filtered_apps.append(app)
            applications = request.env['hr.applicant'].browse([app.id for app in filtered_apps])
        
        # Get payment status for each application
        payment_status = {}
        message_counts = {}
        for app in applications:
            payment = request.env['freelancer.payment'].sudo().search([
                ('applicant_id', '=', app.id)
            ], limit=1)
            if payment:
                payment_status[app.id] = payment.is_paid
            else:
                payment_status[app.id] = None
            
            message_counts[app.id] = request.env['mail.message'].sudo().search_count([
                ('model', '=', 'hr.applicant'),
                ('res_id', '=', app.id),
                ('message_type', 'in', ['comment', 'email']),
            ])
        
        values = {
            'applications': applications,
            'message_counts': message_counts,
            'page_name': 'application',
            'pager': pager,
            'default_url': '/my/applications',
            'payment_status': payment_status,
            'searchbar_filters': searchbar_filters,
            'searchbar_sortings': searchbar_sortings,
            'filterby': filterby,
            'sortby': sortby,
            'search': search,
            'date_from': date_from,
            'date_to': date_to,
            'companies': companies,
            'jobs': jobs,
            'selected_company_ids': company_ids if company_ids else [],
            'selected_job_ids': job_ids if job_ids else [],
        }
        
        return request.render("premium_jobs.portal_my_applications", values)

    @http.route(['/my/applications/<int:application_id>'], type='http', auth='user', website=True)
    def portal_my_application_detail(self, application_id, **kw):
        """Display application details with messaging"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        partner = request.env.user.partner_id
        
        try:
            application = request.env['hr.applicant'].search([
                ('id', '=', application_id),
                ('submitted_by_freelancer_id', '=', partner.id)
            ], limit=1)
            
            if not application:
                raise MissingError(_("Application not found."))
        except (AccessError, MissingError):
            return request.redirect('/my/applications')
        
        # Get messages using sudo to bypass access restrictions
        messages = request.env['mail.message'].sudo().search([
            ('model', '=', 'hr.applicant'),
            ('res_id', '=', application_id),
            ('message_type', 'in', ['comment', 'email']),
        ], order='date desc')
        
        # Get attachments using sudo to bypass access restrictions
        attachments = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'hr.applicant'),
            ('res_id', '=', application_id),
        ])
        
        values = {
            'application': application,
            'messages': messages,
            'attachments': attachments,
            'page_name': 'application',
        }
        
        return request.render("premium_jobs.portal_my_application_detail", values)

    @http.route(['/my/contact/message'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_contact_message(self, **post):
        """Handle message posting from portal user's contact page"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        partner = request.env.user.partner_id
        message_body = post.get('message', '').strip()
        
        if message_body:
            # Find admin users to notify
            admin_users = request.env['res.users'].sudo().search([
                ('groups_id', 'in', request.env.ref('base.group_system').id)
            ], limit=1)
            
            # Post message to admin's partner
            if admin_users:
                admin_partner = admin_users[0].partner_id
                # Post with freelancer as author so name shows correctly
                admin_partner.sudo().message_post(
                    body=message_body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=partner.id
                )
            
            # Also post to freelancer's own chatter for history
            partner.sudo().message_post(
                body=message_body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                author_id=partner.id
            )
        
        return request.redirect('/my')

    @http.route(['/my/applications/<int:application_id>/message'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_application_message(self, application_id, **post):
        """Post a message to an application"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        partner = request.env.user.partner_id
        message_text = post.get('message', '').strip()
        
        if not message_text:
            return request.redirect('/my/applications/%s?error=empty_message' % application_id)
        
        try:
            application = request.env['hr.applicant'].search([
                ('id', '=', application_id),
                ('submitted_by_freelancer_id', '=', partner.id)
            ], limit=1)
            
            if not application:
                raise MissingError(_("Application not found."))
            
            # Post message using sudo to ensure it's created
            application.sudo().message_post(
                body=message_text,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                author_id=partner.id,
            )
            
            return request.redirect('/my/applications/%s?success=1' % application_id)
        except Exception as e:
            return request.redirect('/my/applications/%s?error=message_failed' % application_id)

    @http.route(['/my/applications/export/csv'], type='http', auth='user', website=True, csrf=True)
    def portal_my_applications_export_csv(self, **kw):
        """Export applications to CSV"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        partner = request.env.user.partner_id
        
        # Get applications with same filters as portal_my_applications
        domain = [('submitted_by_freelancer_id', '=', partner.id)]
        
        # Apply filters from URL parameters
        filterby = kw.get('filterby', 'all')
        date_from = kw.get('date_from')
        date_to = kw.get('date_to')
        company_ids = kw.get('company_ids')
        job_ids = kw.get('job_ids')
        search = kw.get('search')
        
        # Apply date filters
        if date_from:
            domain += [('create_date', '>=', date_from + ' 00:00:00')]
        if date_to:
            domain += [('create_date', '<=', date_to + ' 23:59:59')]
        
        # Apply company filter
        if company_ids:
            if isinstance(company_ids, str):
                if company_ids:
                    company_ids = [int(x) for x in company_ids.split(',') if x]
                else:
                    company_ids = None
            if company_ids:
                domain += ['|', ('job_id.tenant_id', 'in', company_ids), ('job_id.company_id', 'in', company_ids)]
        
        # Apply job filter
        if job_ids:
            if isinstance(job_ids, str):
                if job_ids:
                    job_ids = [int(x) for x in job_ids.split(',') if x]
                else:
                    job_ids = None
            if job_ids:
                domain += [('job_id', 'in', job_ids)]
        
        # Apply search
        if search:
            domain += ['|', '|', 
                      ('job_id.name', 'ilike', search),
                      ('tenant_id.name', 'ilike', search),
                      ('partner_name', 'ilike', search)]
        
        # Get all applications
        applications = request.env['hr.applicant'].search(domain, order='create_date desc')
        
        # Post-filter by payment status if needed
        if filterby in ['paid', 'unpaid']:
            filtered_apps = []
            for app in applications:
                payment = request.env['freelancer.payment'].sudo().search([
                    ('applicant_id', '=', app.id)
                ], limit=1)
                if filterby == 'paid' and payment and payment.is_paid:
                    filtered_apps.append(app)
                elif filterby == 'unpaid' and payment and not payment.is_paid:
                    filtered_apps.append(app)
            applications = request.env['hr.applicant'].browse([app.id for app in filtered_apps])
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Title with date/time
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        writer.writerow([f'מועמדויות שלי - {timestamp}'])
        writer.writerow([])  # Empty row
        
        # Headers
        writer.writerow(['משרה', 'חברה', 'תאריך הגשה', 'סטטוס', 'תגמול (₪)', 'שולם/ממתין'])
        
        # Data
        for app in applications:
            company = app.job_id.tenant_id or app.job_id.company_id
            payment = request.env['freelancer.payment'].sudo().search([
                ('applicant_id', '=', app.id)
            ], limit=1)
            
            payment_status = '-'
            if payment:
                payment_status = 'שולם' if payment.is_paid else 'ממתין לתשלום'
            
            writer.writerow([
                app.job_id.name or '',
                company.name if company else '',
                app.create_date.strftime('%d/%m/%Y %H:%M') if app.create_date else '',
                app.stage_id.name or '',
                int(app.job_id.freelancer_reward) if app.job_id.freelancer_reward else '',
                payment_status
            ])
        
        # Return CSV file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'applications_{timestamp}.csv'
        
        return request.make_response(
            output.getvalue().encode('utf-8-sig'),  # utf-8-sig for Excel Hebrew support
            headers=[
                ('Content-Type', 'text/csv; charset=utf-8'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )

    @http.route(['/my/applications/export/excel'], type='http', auth='user', website=True, csrf=True)
    def portal_my_applications_export_excel(self, **kw):
        """Export applications to Excel"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        partner = request.env.user.partner_id
        
        # Get applications with same filters as portal_my_applications
        domain = [('submitted_by_freelancer_id', '=', partner.id)]
        
        # Apply filters from URL parameters (same as CSV)
        filterby = kw.get('filterby', 'all')
        date_from = kw.get('date_from')
        date_to = kw.get('date_to')
        company_ids = kw.get('company_ids')
        job_ids = kw.get('job_ids')
        search = kw.get('search')
        
        # Apply date filters
        if date_from:
            domain += [('create_date', '>=', date_from + ' 00:00:00')]
        if date_to:
            domain += [('create_date', '<=', date_to + ' 23:59:59')]
        
        # Apply company filter
        if company_ids:
            if isinstance(company_ids, str):
                if company_ids:
                    company_ids = [int(x) for x in company_ids.split(',') if x]
                else:
                    company_ids = None
            if company_ids:
                domain += ['|', ('job_id.tenant_id', 'in', company_ids), ('job_id.company_id', 'in', company_ids)]
        
        # Apply job filter
        if job_ids:
            if isinstance(job_ids, str):
                if job_ids:
                    job_ids = [int(x) for x in job_ids.split(',') if x]
                else:
                    job_ids = None
            if job_ids:
                domain += [('job_id', 'in', job_ids)]
        
        # Apply search
        if search:
            domain += ['|', '|', 
                      ('job_id.name', 'ilike', search),
                      ('tenant_id.name', 'ilike', search),
                      ('partner_name', 'ilike', search)]
        
        # Get all applications
        applications = request.env['hr.applicant'].search(domain, order='create_date desc')
        
        # Post-filter by payment status if needed
        if filterby in ['paid', 'unpaid']:
            filtered_apps = []
            for app in applications:
                payment = request.env['freelancer.payment'].sudo().search([
                    ('applicant_id', '=', app.id)
                ], limit=1)
                if filterby == 'paid' and payment and payment.is_paid:
                    filtered_apps.append(app)
                elif filterby == 'unpaid' and payment and not payment.is_paid:
                    filtered_apps.append(app)
            applications = request.env['hr.applicant'].browse([app.id for app in filtered_apps])
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('המועמדויות שלי')
        
        # Formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#2196F3',
            'font_color': 'white'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'font_color': 'white',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Set column widths
        worksheet.set_column('A:A', 30)  # משרה
        worksheet.set_column('B:B', 25)  # חברה
        worksheet.set_column('C:C', 20)  # תאריך
        worksheet.set_column('D:D', 15)  # סטטוס
        worksheet.set_column('E:E', 15)  # תגמול
        worksheet.set_column('F:F', 20)  # שולם/ממתין
        
        # Set RTL for worksheet
        worksheet.right_to_left()
        
        # Title with date/time
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        worksheet.merge_range('A1:F1', f'מועמדויות שלי - {timestamp}', title_format)
        worksheet.set_row(0, 25)  # Title row height
        
        # Headers (row 2, index 1)
        headers = ['משרה', 'חברה', 'תאריך הגשה', 'סטטוס', 'תגמול (₪)', 'שולם/ממתין']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)
        
        # Data (starting from row 3, index 2)
        row = 3
        for app in applications:
            company = app.job_id.tenant_id or app.job_id.company_id
            payment = request.env['freelancer.payment'].sudo().search([
                ('applicant_id', '=', app.id)
            ], limit=1)
            
            payment_status = '-'
            if payment:
                payment_status = 'שולם' if payment.is_paid else 'ממתין לתשלום'
            
            worksheet.write(row, 0, app.job_id.name or '', cell_format)
            worksheet.write(row, 1, company.name if company else '', cell_format)
            worksheet.write(row, 2, app.create_date.strftime('%d/%m/%Y %H:%M') if app.create_date else '', cell_format)
            worksheet.write(row, 3, app.stage_id.name or '', cell_format)
            worksheet.write(row, 4, int(app.job_id.freelancer_reward) if app.job_id.freelancer_reward else '', cell_format)
            worksheet.write(row, 5, payment_status, cell_format)
            row += 1
        
        workbook.close()
        output.seek(0)
        
        # Return Excel file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'applications_{timestamp}.xlsx'
        
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )

    @http.route(['/my/jobs/export/csv'], type='http', auth='user', website=True, csrf=True)
    def portal_my_jobs_export_csv(self, **kw):
        """Export jobs to CSV"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        # Get jobs with same filters
        domain = [
            ('website_published', '=', True),
            ('activity_status', '=', 'active')
        ]
        
        # Apply filters from URL parameters
        search = kw.get('search')
        date_from = kw.get('date_from')
        date_to = kw.get('date_to')
        company_ids = kw.get('company_ids')
        job_ids = kw.get('job_ids')
        sortby = kw.get('sortby', 'date')
        
        if search:
            domain += [('name', 'ilike', search)]
        if date_from:
            domain += [('create_date', '>=', date_from + ' 00:00:00')]
        if date_to:
            domain += [('create_date', '<=', date_to + ' 23:59:59')]
        
        # Company filter
        if company_ids and company_ids != '':
            try:
                selected_company_ids = [int(x) for x in company_ids.split(',') if x]
                if selected_company_ids:
                    domain += ['|', ('tenant_id', 'in', selected_company_ids), ('company_id', 'in', selected_company_ids)]
            except ValueError:
                pass
        
        # Job filter
        if job_ids and job_ids != '':
            try:
                selected_job_ids = [int(x) for x in job_ids.split(',') if x]
                if selected_job_ids:
                    domain += [('id', 'in', selected_job_ids)]
            except ValueError:
                pass
        
        # Sorting
        searchbar_sortings = {
            'date': 'create_date desc',
            'name': 'name',
            'reward': 'freelancer_reward desc',
        }
        order = searchbar_sortings.get(sortby, 'create_date desc')
        
        # Get all jobs
        jobs = request.env['hr.job'].search(domain, order=order)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Title with date/time
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        writer.writerow([f'משרות זמינות - {timestamp}'])
        writer.writerow([])  # Empty row
        
        # Headers
        writer.writerow(['שם המשרה', 'חברה', 'מיקום', 'תאריך פרסום', 'מספר עובדים', 'תגמול (₪)'])
        
        # Data
        for job in jobs:
            company = job.tenant_id or job.company_id
            location = job.city or (job.address_id.city if job.address_id else '')
            
            writer.writerow([
                job.name or '',
                company.name if company else '',
                location,
                job.create_date.strftime('%d/%m/%Y') if job.create_date else '',
                job.no_of_recruitment or 1,
                int(job.freelancer_reward) if job.freelancer_reward else ''
            ])
        
        # Return CSV file
        timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'jobs_{timestamp_file}.csv'
        
        return request.make_response(
            output.getvalue().encode('utf-8-sig'),
            headers=[
                ('Content-Type', 'text/csv; charset=utf-8'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )

    @http.route(['/my/jobs/export/excel'], type='http', auth='user', website=True, csrf=True)
    def portal_my_jobs_export_excel(self, **kw):
        """Export jobs to Excel"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        # Get jobs with same filters
        domain = [
            ('website_published', '=', True),
            ('activity_status', '=', 'active')
        ]
        
        # Apply filters from URL parameters
        search = kw.get('search')
        date_from = kw.get('date_from')
        date_to = kw.get('date_to')
        company_ids = kw.get('company_ids')
        job_ids = kw.get('job_ids')
        sortby = kw.get('sortby', 'date')
        
        if search:
            domain += [('name', 'ilike', search)]
        if date_from:
            domain += [('create_date', '>=', date_from + ' 00:00:00')]
        if date_to:
            domain += [('create_date', '<=', date_to + ' 23:59:59')]
        
        # Company filter
        if company_ids and company_ids != '':
            try:
                selected_company_ids = [int(x) for x in company_ids.split(',') if x]
                if selected_company_ids:
                    domain += ['|', ('tenant_id', 'in', selected_company_ids), ('company_id', 'in', selected_company_ids)]
            except ValueError:
                pass
        
        # Job filter
        if job_ids and job_ids != '':
            try:
                selected_job_ids = [int(x) for x in job_ids.split(',') if x]
                if selected_job_ids:
                    domain += [('id', 'in', selected_job_ids)]
            except ValueError:
                pass
        
        # Sorting
        searchbar_sortings = {
            'date': 'create_date desc',
            'name': 'name',
            'reward': 'freelancer_reward desc',
        }
        order = searchbar_sortings.get(sortby, 'create_date desc')
        
        # Get all jobs
        jobs = request.env['hr.job'].search(domain, order=order)
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('משרות זמינות')
        
        # Formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#2196F3',
            'font_color': 'white'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'font_color': 'white',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Set column widths
        worksheet.set_column('A:A', 40)  # שם המשרה
        worksheet.set_column('B:B', 30)  # חברה
        worksheet.set_column('C:C', 20)  # מיקום
        worksheet.set_column('D:D', 20)  # תאריך
        worksheet.set_column('E:E', 15)  # מספר עובדים
        worksheet.set_column('F:F', 15)  # תגמול
        
        # Set RTL for worksheet
        worksheet.right_to_left()
        
        # Title with date/time
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        worksheet.merge_range('A1:F1', f'משרות זמינות - {timestamp}', title_format)
        worksheet.set_row(0, 25)  # Title row height
        
        # Headers (row 3, index 2)
        headers = ['שם המשרה', 'חברה', 'מיקום', 'תאריך פרסום', 'מספר עובדים', 'תגמול (₪)']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)
        
        # Data (starting from row 4, index 3)
        row = 3
        for job in jobs:
            company = job.tenant_id or job.company_id
            location = job.city or (job.address_id.city if job.address_id else '')
            
            worksheet.write(row, 0, job.name or '', cell_format)
            worksheet.write(row, 1, company.name if company else '', cell_format)
            worksheet.write(row, 2, location, cell_format)
            worksheet.write(row, 3, job.create_date.strftime('%d/%m/%Y') if job.create_date else '', cell_format)
            worksheet.write(row, 4, job.no_of_recruitment or 1, cell_format)
            worksheet.write(row, 5, int(job.freelancer_reward) if job.freelancer_reward else '', cell_format)
            row += 1
        
        workbook.close()
        output.seek(0)
        
        # Return Excel file
        timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'jobs_{timestamp_file}.xlsx'
        
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )

