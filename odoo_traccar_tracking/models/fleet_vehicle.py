# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    
    is_traccar = fields.Boolean("Is Traccar", default=True)
    traccer_device_id = fields.Char(string='Device Unique ID', help="Traccar Device ID")
    is_online = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline')
        ], string='Is Online', default="offline", help="Driver online status")
    device_record_id = fields.Integer(string='Device ID', help="Driver Record ID")
    trip_history_count = fields.Integer(compute="_compute_trip_count_all", string="Drivers Trip Count")

    def set_traccar(self):
        self.write({'is_traccar':False})

    def unset_traccar(self):
        self.write({'is_traccar':True})

    def _compute_trip_count_all(self):
        tripDetails = self.env['trip.details']
        for record in self:
            record.trip_history_count = tripDetails.search_count([('vehicle_id', '=', record.id)])

    def open_vehicle_tracking_history(self):
        partial = self.env['tracking.history.wizard'].create({'vehicle_id':self.id})
        ctx = dict(self._context or {})
        ctx['All'] = True
        return {'name': ("Vehicle Tracking History"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'tracking.history.wizard',
                'view_id': self.env.ref('odoo_traccar_tracking.tracking_history_wizard_form').id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'nodestroy': True,
                'target': 'new',
                }

    def validate_device(self):
        resp = self.env['trip.details'].getDevices(uniqueId=self.traccer_device_id)
        if not resp:
           data = {
                "name":self.model_id.name,
                "uniqueId" : self.traccer_device_id
            }
           resp = self.env['trip.details'].createDevice(data)
           if resp:
               self.device_record_id = resp
               self.is_online = 'offline'
        else:
            for res in resp:
                self.device_record_id = res
                self.is_online = 'online' if resp[res] == 'online' else 'offline'
        return True
