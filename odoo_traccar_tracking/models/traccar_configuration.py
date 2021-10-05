# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################
import requests
import json
import logging
_log = logging.getLogger(__name__)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class TraccarConfigure(models.Model):
    _name = "traccar.configure"
    _inherit = ['mail.thread']
    _description = "Traccar Configuration"
    _rec_name = 'instance_name'

    def _default_instance_name(self):
        return self.env[
            'ir.sequence'].next_by_code('traccar.configure')

    name = fields.Char(
        string='Traccar URL',
        track_visibility="onchange",
        required=True,
    )
    instance_name = fields.Char(
        string='Instance Name',
        default=lambda self: self._default_instance_name())
    user = fields.Char(
        string='API User Name',
        track_visibility="onchange",
        required=True)
    pwd = fields.Char(
        string='API Password',
        track_visibility="onchange",
        required=True,
        size=100)
    status = fields.Char(string='Status', readonly=True)
    active = fields.Boolean(
        string="Active",
        track_visibility="onchange",
        default=True)
    connection_status = fields.Boolean(
        string="Connection Status", default=False)
    create_date = fields.Datetime(string='Created Date')

    def current_map_provider(self):
        map_provider_id = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.geo_provider')
        if map_provider_id:
            map_provider = self.env['base.geo_provider'].browse(int(map_provider_id))
            if map_provider:
                return map_provider.tech_name
        return 'openstreetmap'

    @api.model
    def create(self, vals):
        if 'name' in vals:
            frontEnd = vals.get('name', '').strip('/')
            vals['name'] = frontEnd
        activeConnections = self.search([('active', '=', True)])
        if vals.get('active') and activeConnections:
            raise UserError(
                _('Warning!\nSorry, Only one active connection is allowed.'))
        vals['instance_name'] = self.env[
            'ir.sequence'].next_by_code('traccar.configure')
        res = super(TraccarConfigure, self).create(vals)
        return res

    def write(self, vals):
        if 'name' in vals:
            frontEnd = vals.get('name', '').strip('/')
            vals['name'] = frontEnd
        activeConnections = self.search([('active', '=', True)])
        if vals:
            if len(activeConnections) > 0 and vals.get(
                    'active'):
                raise UserError(
                    _('Warning!\nSorry, Only one active connection is allowed.'))
            for instanceObj in self:
                if not instanceObj.instance_name:
                    vals['instance_name'] = self.env[
                        'ir.sequence'].next_by_code('traccar.configure')
        return super(TraccarConfigure, self).write(vals)

    def test_connection(self):
        connection_status = False
        status = 'Traccar Connection Un-successful'
        text = 'Test connection Un-successful please check the traccar login credentials !!!'
        url = self.name + "/api/session"
        user, pwd = self.user, self.pwd
        try:
            data = {'email': user, 'password': pwd}
            response = requests.Session().post(url=url, data=data)
            if response.status_code == 200:
                connection_status = True
                text = 'Test Connection with Traccar is successful, now you can proceed with synchronization.'
                status = "Congratulation, It's Successfully Connected with Traccar."
            elif response.status_code == 401:
                text = ('Traccar Unauthorized Access: Check traccar credentials %s') % response.text
            else :
                text = ('Traccar Connection Error: %s') % response.text
        except Exception as e:
            text = ('Error!\Traccar Connection Error: %s') % e
        self.status = status
        self.connection_status = connection_status
        return self.env['wk.wizard.message'].genrated_message(text)

    def fetch_trips(self):
        partial = self.env['tracking.history.wizard'].create({})
        return {'name': ("Vehicle Tracking History"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'tracking.history.wizard',
                'view_id': self.env.ref('odoo_traccar_tracking.tracking_history_wizard_form').id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                }
