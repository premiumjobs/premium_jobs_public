# -*- coding: utf-8 -*-
"""
Extension of hr.job (Job Positions) for Premium Jobs
Adds additional fields for job management, publication, and freelancer assignment
"""

from odoo import models, fields, api


class HrJob(models.Model):
    """Extended hr.job model for Premium Jobs"""
    
    _inherit = 'hr.job'
    
    # Override description field to remove default text
    description = fields.Html(string='Job Summary', default='')
    
    # Tenant relationship
    tenant_id = fields.Many2one(
        'res.partner',
        string='לקוח',
        domain=[('is_tenant', '=', True)],
        required=False,  # Changed to False to allow deletion of old records
        help='Client company (tenant) for this job'
    )
    
    # Display formatted address (computed from address_id)
    address_display = fields.Char(
        string='כתובת מלאה',
        compute='_compute_address_display',
        store=False,
        readonly=True
    )
    
    # Job numbers
    job_number = fields.Integer(string='Internal Job Number', readonly=True)
    publication_number = fields.Integer(string='Publication Number')
    
    # Extended descriptions
    client_title = fields.Text(string='Title for Client')
    internal_description = fields.Text(string='Internal Job Description')
    internal_notes = fields.Text(string='Internal Notes')
    social_media_text = fields.Text(string='Social Media Text')
    show_internal_notes = fields.Boolean(string='Show Internal Notes', default=False)
    
    # Status and activity
    activity_status = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ], string='Activity Status', default='active')
    
    is_urgent = fields.Boolean(string='Urgent', default=False)
    closed_date = fields.Datetime(string='Closed Date')
    
    # Location
    city = fields.Char(string='City')
    search_radius_km = fields.Integer(string='Search Radius (km)')
    
    # Requirements
    employment_types = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
    ], string='Employment Type')
    
    marital_status_requirement = fields.Selection([
        ('any', 'Any'),
        ('single', 'Single'),
        ('married', 'Married'),
    ], string='Marital Status')
    
    mobility_required = fields.Selection([
        ('none', 'None'),
        ('local', 'Local'),
        ('regional', 'Regional'),
        ('national', 'National'),
    ], string='Mobility Required')
    
    driver_license_required = fields.Selection([
        ('none', 'None'),
        ('any', 'Any'),
        ('specific', 'Specific Types'),
    ], string='Driver License')
    
    gender_requirement = fields.Selection([
        ('any', 'Any'),
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender Requirement')
    
    age_min = fields.Integer(string='Minimum Age')
    age_max = fields.Integer(string='Maximum Age')
    
    required_languages = fields.Many2many(
        'res.lang',
        string='Required Languages'
    )
    
    has_bonuses = fields.Boolean(string='Has Bonuses', default=False)
    has_transport = fields.Boolean(string='Has Company Transport', default=False)
    
    # Compensation
    salary_min = fields.Monetary(string='Minimum Salary', currency_field='currency_id')
    salary_max = fields.Monetary(string='Maximum Salary', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    request_salary_expectations = fields.Boolean(string='Request Salary Expectations', default=True)
    
    # Publication settings
    hide_candidate_data = fields.Boolean(string='Hide Candidate Data', default=False)
    contact_email = fields.Char(string='Contact Email')
    contact_phone = fields.Char(string='Contact Phone')
    resume_delivery_method = fields.Selection([
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    ], string='Resume Delivery Method', default='email')
    
    resume_recipient = fields.Selection([
        ('coordinator', 'Coordinator'),
        ('client', 'Client'),
    ], string='Resume Recipient', default='coordinator')
    
    show_company_logo = fields.Boolean(string='Show Company Logo', default=True)
    check_exclusivity = fields.Boolean(string='Check Exclusivity', default=False)
    
    positions_count = fields.Integer(string='Number of Positions', default=1)
    accepted_candidates_count = fields.Integer(string='Accepted Candidates', default=0)
    
    # Coordinator
    coordinator_id = fields.Many2one('res.users', string='Coordinator')
    
    # Financial terms
    company_commission = fields.Monetary(string='Company Commission', currency_field='currency_id')
    freelancer_commission = fields.Monetary(string='Freelancer Commission', currency_field='currency_id')
    freelancer_reward = fields.Monetary(string='תגמול לפרילנסר', currency_field='currency_id', 
                                       help='Reward for freelancer who brings successful candidate')
    net_income = fields.Monetary(string='Net Income', currency_field='currency_id', compute='_compute_net_income', store=True)
    
    warranty_period_days = fields.Integer(string='Warranty Period (Days)')
    payment_terms_days = fields.Integer(string='Payment Terms (Days)')
    client_warranty_period_days = fields.Integer(string='Client Warranty Period (Days)')
    client_payment_terms_days = fields.Integer(string='Client Payment Terms (Days)')
    
    # Publication portals
    publish_to_job_portal = fields.Boolean(string='Publish to Job Portal', default=False)
    publish_to_freelancer_portal = fields.Boolean(string='Publish to Freelancer Portal', default=False)
    external_sites = fields.Char(string='External Job Sites')
    
    # Freelancer-specific
    freelancer_headline = fields.Text(string='Headline for Freelancers')
    public_headline = fields.Text(string='Public Headline')
    public_description = fields.Text(string='Public Description')
    requirements_text = fields.Text(string='Requirements')
    screening_questions = fields.Text(string='Screening Questions')
    freelancer_notes = fields.Text(string='Notes for Freelancers')
    publication_date = fields.Date(string='Publication Date')
    
    # Assigned freelancers
    assigned_freelancer_ids = fields.Many2many(
        'res.partner',
        'job_freelancer_rel',
        'job_id',
        'freelancer_id',
        string='Assigned Freelancers',
        domain=[('is_freelancer', '=', True)]
    )
    
    # Categories and Tags
    main_category_id = fields.Many2one('hr.job.category', string='Main Category')
    additional_category_ids = fields.Many2many(
        'hr.job.category',
        'job_additional_category_rel',
        string='Additional Categories'
    )
    subcategory_id = fields.Many2one('hr.job.category', string='Subcategory')
    tag_ids = fields.Many2many('hr.job.tag', string='Tags')
    
    # Send-to Contacts
    sendto_contact_ids = fields.Many2many(
        'res.partner',
        'job_sendto_contact_rel',
        string='Send-to Contacts'
    )
    
    # Sector
    sector = fields.Selection([
        ('high_tech', 'High-Tech'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('construction', 'Construction'),
        ('hospitality', 'Hospitality'),
        ('other', 'Other'),
    ], string='Sector')
    
    # Job Image
    job_image = fields.Binary(string='Job Image')
    job_image_filename = fields.Char(string='Image Filename')
    
    # Approval
    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Approval Status', default='draft')
    approval_comment = fields.Text(string='Approval Comment')
    approval_date = fields.Datetime(string='Approval Date')
    approved_by_id = fields.Many2one('res.users', string='Approved By')
    
    # Collaboration
    has_collaboration = fields.Boolean(string='Collaboration with Premium Jobs', default=False)
    digital_contract = fields.Boolean(string='Digital Contract', default=False)
    collaboration_cancelled = fields.Boolean(string='Collaboration Cancelled', default=False)
    collaboration_cancel_reason = fields.Text(string='Cancel Reason')
    
    # Part 2 Fields - Candidate Filtering
    mobility_or_license = fields.Selection([('and', 'וגם'), ('or', 'או')], string='ניידות/רשיון', default='and')
    no_gender = fields.Boolean(string='כולל מועמדים שמינם אינו ידוע', default=True)
    no_age = fields.Boolean(string='כולל מועמדים שגילם אינו ידוע', default=True)
    min_wage = fields.Integer(string='שכר מינימלי', default=0)
    max_wage = fields.Integer(string='שכר מקסימלי', default=1000000)
    no_wage = fields.Boolean(string='כולל מועמדים עם ציפיות שכר לא ידועות', default=True)
    expire_days = fields.Integer(string='תוקף (ימים)', default=60)
    norepeat_months = fields.Integer(string='חזרה (חודשים)', default=3)
    full_cv = fields.Boolean(string='רק מועמדים עם קורות חיים', default=False)
    hebrew_cv = fields.Boolean(string='רק מועמדים עם קורות חיים בעברית', default=False)
    crossreferral = fields.Boolean(string='הצלבת הפניות', default=False)
    
    # Languages
    lang_hebrew = fields.Selection([
        ('0', 'לא חשוב'), ('1', 'בסיסית'), ('2', 'בינונית'),
        ('3', 'טובה'), ('4', 'טובה מאוד'), ('5', 'ברמת שפת אם'), ('6', 'שפת אם')
    ], string='עברית', default='0')
    lang_english = fields.Selection([
        ('0', 'לא חשוב'), ('1', 'בסיסית'), ('2', 'בינונית'),
        ('3', 'טובה'), ('4', 'טובה מאוד'), ('5', 'ברמת שפת אם'), ('6', 'שפת אם')
    ], string='אנגלית', default='0')
    lang_arabic = fields.Selection([
        ('0', 'לא חשוב'), ('1', 'בסיסית'), ('2', 'בינונית'),
        ('3', 'טובה'), ('4', 'טובה מאוד'), ('5', 'ברמת שפת אם'), ('6', 'שפת אם')
    ], string='ערבית', default='0')
    lang_russian = fields.Selection([
        ('0', 'לא חשוב'), ('1', 'בסיסית'), ('2', 'בינונית'),
        ('3', 'טובה'), ('4', 'טובה מאוד'), ('5', 'ברמת שפת אם'), ('6', 'שפת אם')
    ], string='רוסית', default='0')
    lang_spanish = fields.Selection([
        ('0', 'לא חשוב'), ('1', 'בסיסית'), ('2', 'בינונית'),
        ('3', 'טובה'), ('4', 'טובה מאוד'), ('5', 'ברמת שפת אם'), ('6', 'שפת אם')
    ], string='ספרדית', default='0')
    lang_french = fields.Selection([
        ('0', 'לא חשוב'), ('1', 'בסיסית'), ('2', 'בינונית'),
        ('3', 'טובה'), ('4', 'טובה מאוד'), ('5', 'ברמת שפת אם'), ('6', 'שפת אם')
    ], string='צרפתית', default='0')
    lang_amharic = fields.Selection([
        ('0', 'לא חשוב'), ('1', 'בסיסית'), ('2', 'בינונית'),
        ('3', 'טובה'), ('4', 'טובה מאוד'), ('5', 'ברמת שפת אם'), ('6', 'שפת אם')
    ], string='אמהרית', default='0')
    
    # Part 3 Fields - Administrative
    job_level = fields.Selection([
        ('1', 'ידני'),
        ('2', 'טלפוני'),
        ('3', 'שאלונים'),
        ('5', 'שאלונים+טלפוני'),
        ('0', 'אוטומטי'),
    ], string='רמת סינון ראשוני', default='2')
    refer_channel = fields.Selection([
        ('0', 'דוא"ל'),
        ('1', 'סמס'),
        ('2', 'דוא"ל + סמס'),
        ('3', 'ללא'),
        ('4', 'WhatsApp'),
        ('5', 'דוא"ל + WhatsApp'),
    ], string='שיטת שליחה', default='0')
    referfail = fields.Selection([
        ('0', 'לא'),
        ('1', 'כן'),
    ], string='שליחה מתיקון', default='1')
    sales_admin_id = fields.Many2one('res.users', string='רכז מטפל', required=True)
    oper_admin_id = fields.Many2one('res.users', string='רכז גיוס')
    more_admins_ids = fields.Many2many('res.users', 'job_admin_rel', 'job_id', 'admin_id', string='רכזים נוספים')
    openings = fields.Integer(string='תקנים פתוחים')
    
    @api.depends('company_commission', 'freelancer_commission')
    def _compute_net_income(self):
        """Calculate net income"""
        for job in self:
            company = job.company_commission or 0
            freelancer = job.freelancer_commission or 0
            job.net_income = company - freelancer
    
    @api.model
    def create(self, vals):
        """Auto-generate job number on creation"""
        if not vals.get('job_number'):
            # Get last job number
            last_job = self.search([], order='job_number desc', limit=1)
            vals['job_number'] = (last_job.job_number or 0) + 1
        return super(HrJob, self).create(vals)
    
    @api.depends('address_id', 'address_id.street', 'address_id.city', 'address_id.zip')
    def _compute_address_display(self):
        """Format address for display"""
        for record in self:
            if record.address_id:
                parts = []
                if record.address_id.street:
                    parts.append(record.address_id.street)
                if record.address_id.city:
                    parts.append(record.address_id.city)
                if record.address_id.zip:
                    parts.append(record.address_id.zip)
                record.address_display = ', '.join(parts) if parts else record.address_id.name
            else:
                record.address_display = ''
    
    @api.onchange('tenant_id')
    def _onchange_tenant_id(self):
        """Auto-fill address from tenant when tenant is selected"""
        if self.tenant_id:
            # Set address to tenant's address
            self.address_id = self.tenant_id
        else:
            self.address_id = False

