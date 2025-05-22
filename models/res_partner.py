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

    logo_dev_sync_date = fields.Datetime(string='Logo.dev sync date', help='Date of the last sync with logo.dev')

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def get_logo_company(self):
        """
        Get the logo from logo.dev
        """
        for partner in self:
            if not partner.is_company:
                raise ValidationError(_("You can't get the logo from a non-company partner"))
            if not partner.website:
                raise ValidationError(_("You can't get the logo from a partner without website"))
            else:
                logo = self.env['a4i.logo.dev'].get_logo_company(domain=partner.website)
                if logo:
                    partner.write({'image': logo, 'logo_dev_sync_date': fields.Datetime.now()})
                else:
                    raise ValidationError(_("No logo found for the company"))
                
    @api.model
    def cron_sync_logo(self):
        """
        Cron job to sync the logo of the company
        """

        LOG.info("Starting cron job to sync the logo of the company")

        partners = self.env['res.partner'].search([('is_company', '=', True), ('website', '!=', None)], order='logo_dev_sync_date ASC')

        for partner in partners:

            # Check the limit of requests
            if self.env['a4i.logo.dev.config'].check_and_update_request_limit():

                try:
                    partner.get_logo_company()
                except Exception as e:
                    LOG.error("Error syncing logo for partner %s: %s", partner.name, e)
                    continue
            
            else:
                LOG.info("Limit of requests reached.")
                return True
            
        LOG.info("Cron job to sync the logo of the company finished")

        return True
