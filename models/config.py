# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import requests
from openerp.exceptions import ValidationError
import logging

LOG = logging.getLogger(__name__)

class a4i_logo_dev_config(models.Model):
    _name = 'a4i.logo.dev.config'

    @api.model
    def _get_states(self):
        return [('draft', 'Draft'), ('active', 'Active'), ('inactive', 'Inactive')]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================

    # General
    name = fields.Char(string='Name', default='Logo.dev configuration', help='Name of the configuration.')
    state = fields.Selection(selection='_get_states', string='State', help='State of the configuration.', default='draft')
    config_date = fields.Date(string='Configuration date', help='Date of the configuration', default=fields.Date.today())
    logo_dev_url = fields.Char(string='Logo.dev URL', help='URL of the logo.dev service', default="https://img.logo.dev/")
    logo_dev_public_api_key = fields.Char(string='Logo.dev Public API Key', help='Public API Key of the logo.dev service')
    logo_dev_private_api_key = fields.Char(string='Logo.dev Private API Key', help='Private API Key of the logo.dev service')
    logo_dev_daily_requests = fields.Integer(string='Daily requests', help='Number of requests made today', default=0)
    logo_dev_last_request_date = fields.Date(string='Last request date', help='Date of the last request', default=fields.Date.today)
    total_count_requests = fields.Integer(string='Total requests', help='Total number of requests made', default=0)
    max_limit_requests_daily = fields.Integer(string='Max limit requests daily', help='Max limit of requests daily', default=5000)

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.model
    def check_and_update_request_limit(self):
        """
        Check if we have reached the daily limit of requests (5000) and update the counter
        """
        active_config = self.search([('state', '=', 'active')], limit=1)
        if not active_config:
            raise ValidationError(_("No active configuration found"))

        today = fields.Date.today()
        
        # If it's a new day, reset the counter
        if active_config.logo_dev_last_request_date != today:
            active_config.write({
                'logo_dev_daily_requests': 0,
                'logo_dev_last_request_date': today
            })
        
        # Check if we've reached the limit
        if active_config.logo_dev_daily_requests >= active_config.max_limit_requests_daily:
            raise ValidationError(_("Daily request limit has been reached. Please try again tomorrow."))
        
        # Increment the counter
        active_config.logo_dev_daily_requests += 1
        return True
    
    @api.multi
    def increment_total_count_requests(self):
        active_config = self.search([('state', '=', 'active')], limit=1)
        if active_config:
            active_config.write({
                'total_count_requests': active_config.total_count_requests + 1
            })

    @api.multi
    def get_url_logo_dev(self):
        active_config = self.search([('state', '=', 'active')], limit=1)
        if active_config:
            return active_config.logo_dev_url
        else:
            raise ValidationError(_("No active configuration found"))
        
    @api.multi
    def get_public_api_key(self):
        active_config = self.search([('state', '=', 'active')], limit=1)
        if active_config:
            return active_config.logo_dev_public_api_key
        else:
            raise ValidationError(_("No active configuration found"))
        
    
