# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import requests
from openerp.exceptions import ValidationError
import logging

LOG = logging.getLogger(__name__)

class a4i_logo_dev_res_partner(models.Model):
    _inherit = 'res.partner'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================

    a4i_logo_dev_sync_date = fields.Datetime(string='Logo.dev sync date', help='Date of the last sync with logo.dev')

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def get_logo_company(self):
        """
        Role : Get the logo from logo.dev
        Parameters : None
        Return : None
        """

        for partner in self:

            # Check the limit of requests
            if not self.env['a4i.logo.dev.config'].check_and_update_request_limit():
                raise ValidationError(_("Limit of daily requests reached."))
    
            if not partner.is_company:
                raise ValidationError(_("You can't get the logo from a non-company partner"))
            if not partner.website:
                raise ValidationError(_("You can't get the logo from a partner without website"))
            else:
                logo = self.env['a4i.logo.dev'].get_logo_company(domain=partner.website)
                if logo:
                    partner.write({'image': logo, 'a4i_logo_dev_sync_date': fields.Datetime.now()})
                else:
                    raise ValidationError(_("No logo found for the company"))
                
    @api.model
    def cron_sync_logo(self, update_logo=False):
        """
        Role : Cron job to get companies logos from logo.dev service
        Parameters : 
            - update_logo (bool) - If True, the logo will be updated even if it already exists
        Return : True
        """

        LOG.info("Starting cron job to sync the logo of the company")

        partners = self.env['res.partner'].search([('is_company', '=', True), ('id', '!=', 1), ('website', '!=', None)], order='a4i_logo_dev_sync_date ASC')

        # Get the active configuration
        config = self.env['a4i.logo.dev.config'].search([('state', '=', 'active')], limit=1)
        if not config:
            LOG.error("No active configuration found")
            return True

        # Calculate remaining requests
        remaining_requests = config.max_limit_requests_daily - config.logo_dev_daily_requests
        if remaining_requests <= 0:
            LOG.info("No remaining requests for today")
            return True

        # Process only the number of partners we can handle with remaining requests
        partners_to_process = partners[:remaining_requests]
        LOG.info("Processing %d partners with %d remaining requests", len(partners_to_process), remaining_requests)

        for partner in partners_to_process:
            if not partner.image or update_logo:
                try:
                    partner.get_logo_company()
                except Exception as e:
                    LOG.error("Error syncing logo for partner %s: %s", partner.name, e)
                    continue
            else:
                LOG.info("Partner %s already has a logo", partner.name)
            
        LOG.info("Cron job to sync the logo of the company finished")

        return True
