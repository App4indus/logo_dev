# -*- coding: utf-8 -*-
import base64
from openerp import models, fields, api, _
import requests
from openerp.exceptions import ValidationError
import logging

LOG = logging.getLogger(__name__)

class a4i_logo_dev(models.Model):
    _name = 'a4i.logo.dev'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================

    # ===========================================================================
    # METHODS
    # ===========================================================================

    @api.multi
    def get_logo_company(self, domain):
        """
        Get the logo from logo.dev
        """

        # Check if the domain is valid
        if not domain:
            raise ValidationError(_("The domain is not valid"))
        
        # Convert website to domain if it is not already
        if domain.startswith('http'):
            # Remove protocol
            if '://' in domain:
                domain = domain.split('://', 1)[1]
            # Remove www if present
            if domain.startswith('www.'):
                domain = domain[4:]
            # Remove any path after domain
            domain = domain.split('/')[0]

        # Check and update request limit
        self.env['a4i.logo.dev.config'].check_and_update_request_limit()

        base_url = self.env['a4i.logo.dev.config'].get_url_logo_dev()
        token = self.env['a4i.logo.dev.config'].get_public_api_key()

        url = base_url + domain

        # Set parameters
        params = {
            'token': token,
            'format': 'jpg',
            'size': '128',
            'retina': 'true',
            'fallback': '404'
        }

        # Add parameters to the url
        url = url + '?' + '&'.join(['{}={}'.format(key, value) for key, value in params.items()])

        try:

            LOG.debug("Sending request to logo.dev: %s", url)

            response = requests.get(url)
            response.raise_for_status()

            if response.status_code == 200:
                # Encode the image to base64
                image_base64 = base64.b64encode(response.content)

                # Increment the total count requests
                self.env['a4i.logo.dev.config'].increment_total_count_requests()

                return image_base64
            else:
                return False
            
        except Exception as e:
            LOG.error("Error getting logo from logo.dev: %s", e)
            return False
