# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models


######################## Tracking History Model(Used from server action) ###


class TrackingHistoryWizard(models.TransientModel):
    _name = "tracking.history.wizard"
    _description = "Tracking History Wizard"

    name = fields.Char("Wizard Name")
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', domain="[('is_traccar', '=', True)]")
    driver_id = fields.Many2one(related="vehicle_id.driver_id", string="Driver", readonly=False)
    date_from = fields.Datetime(
        string='Date From',
        default=fields.Datetime.now,
        help="Trip Date starting range for filter")
    date_to = fields.Datetime(
        string='Date To',
        default=fields.Datetime.now,
        help="Trip Date end range for filter")
    source_long = fields.Char(string='Source Longitude', help="Source Longitude")
    source_lat = fields.Char(string='Source Latitude', help="Source Latitude")
    destination_long = fields.Char(string='Destination Longitude', help="Destination Longitude")
    destination_lat = fields.Char(string='Destination Latitude', help="Destination Latitude")
    driver_locations = fields.Text(string='Driver Locations', help="Driver Locations")

    def get_trip_reports(self):
        date_to = self.date_to.strftime("%Y-%m-%dT%H:%M:%SZ")
        date_from = self.date_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.env['trip.details'].cron_import_trip_details(date_to, date_from)
        return self.env['wk.wizard.message'].genrated_message("Traccar Trips are successfully created")

    def show_trip_reports(self):
        vehicle_id = self.vehicle_id.id if self.vehicle_id else False
        startFilter = [('trip_device_date', '>=', self.date_from), ('vehicle_id', '=', vehicle_id)] if vehicle_id else [('trip_device_date', '>=', self.date_from)]
        endFilter = [('trip_device_date', '<=', self.date_to), ('vehicle_id', '=', vehicle_id)] if vehicle_id else [('trip_device_date', '<=', self.date_to)]
        start = self.env['trip.details'].search(startFilter, order="id asc", limit=1)
        end = self.env['trip.details'].search(endFilter, order="id desc", limit=1)
        if not start or not end:
            return self.env['wk.wizard.message'].genrated_message("No Trips are avilable between this date")
        partial = self.env['tracking.history.wizard'].create({
            'name': 'Vehicle Trip History',
            'source_long':start.source_long,
            'source_lat':start.source_lat,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'destination_long':end.destination_long,
            'destination_lat':end.destination_lat
        })
        return {'name': ("Vehicle Trip History"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'tracking.history.wizard',
                'view_id': self.env.ref('odoo_traccar_tracking.tracking_history_map_wizard_form').id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                }

    def get_driver_locations(self):
        ends = self.env['trip.details'].search([('trip_device_date', '<=', self.date_to)], order="trip_device_date desc")
        if not ends:
            return self.env['wk.wizard.message'].genrated_message("No Drivers are avilable between this date")
        driver_locations = ""
        for end in ends:
            if end.driver_id and end.driver_id.name not in driver_locations:
                if driver_locations:
                    driver_locations = "{};{}:{},{}".format(driver_locations, end.driver_id.name, end.destination_long, end.destination_lat)
                else:
                    driver_locations = "{}:{},{}".format(end.driver_id.name, end.destination_long, end.destination_lat)
        partial = self.env['tracking.history.wizard'].create({
            'name': 'Drivers Location',
            'date_to':self.date_to,
            'driver_locations':driver_locations
        })
        return {'name': ("Vehicle Trip History"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'tracking.history.wizard',
                'view_id': self.env.ref('odoo_traccar_tracking.tracking_vehicle_location_map_wizard_form').id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                }
