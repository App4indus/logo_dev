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
                    partner.image = logo
                else:
                    raise ValidationError(_("No logo found for the company"))
                
    @api.model
    def cron_sync_logo(self):
        """
        Cron job to sync the logo of the company
        """
        partners = self.env['res.partner'].search([('is_company', '=', True), ('website', '!=', False)])

        try:
            for partner in partners:
                partner.get_logo_company()
        except Exception as e:
            LOG.error("Error syncing logo for partner %s: %s", partner.name, e)
            pass

        return True
