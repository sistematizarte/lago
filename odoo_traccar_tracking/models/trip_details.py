# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import _, api, fields, models
import requests
import json
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class TripDetails(models.Model):
    _name = "trip.details"
    _inherit = ['mail.thread']
    _description = "Trip Details"

    def _default_trip_name(self):
        return self.env[
            'ir.sequence'].next_by_code('trip.details')

    name = fields.Char(string='Name', default=lambda self: self._default_trip_name(), help="Sequence of Trip")
    source_long = fields.Char(string='Source Longitude', help="Source Longitude")
    source_lat = fields.Char(string='Source Latitude', help="Source Latitude")
    destination_long = fields.Char(string='Destination Longitude', help="Destination Longitude")
    destination_lat = fields.Char(string='Destination Latitude', help="Destination Latitude")
    driver_id = fields.Many2one(related="vehicle_id.driver_id", string="Driver", readonly=False)
    traccer_device_id = fields.Char(related="vehicle_id.traccer_device_id", string="Traccar Unique Id", readonly=False)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    value = fields.Float('Odometer Value', group_operator="max")
    unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    trip_date = fields.Date('Trip Date', default=fields.Date.today, help='Trip Date')
    trip_device_date = fields.Datetime(string='Device Date')
    battery_level = fields.Float('Battery Level')
    total_distance = fields.Float('Total Distance')
    accuracy = fields.Float('Accuracy')
    travel_id = fields.Integer('Travel ID')
    device_id = fields.Integer('Device ID')

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('trip.details')
        return super().create(vals)

    def write(self, vals):
        for obj in self:
            if not obj.name:
                vals['name'] = self.env['ir.sequence'].next_by_code('trip.details')
        return super().write(vals)

    def cron_import_trip_details(self, to_date=False, from_date=False):
        connections = self.env['traccar.configure'].search([('active', '=', True)], limit=1)
        if connections:
            try:
                to_date = to_date if to_date else datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                from_date = from_date if from_date else (fields.Datetime.from_string(datetime.now()) - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
                devices = self.getDevices(connection=connections)
                if devices:
                    for device in devices:
                        url = "{}/api/reports/route?deviceId={}&from={}&to={}".format(connections.name, device, from_date, to_date)
                        response = requests.get(url, auth=(connections.user, connections.pwd))
                        if response.status_code == 200:
                            route_reports = response.json()
                            for route_report in route_reports:
                                data = {}
                                device_id = route_report.get('deviceId', '')
                                vehicleObjs = self.env['fleet.vehicle'].search([('device_record_id', '=', device_id)], limit=1)
                                if vehicleObjs and vehicleObjs.is_traccar:
                                    vehicleObjs.is_online = 'online' if device_id in devices and devices[device_id] == 'online' else 'offline'
                                    data['vehicle_id'] = vehicleObjs.id
                                else:
                                    continue
                                travel_id = route_report.get('id', '')
                                resp = self.env['trip.details'].search([('travel_id', '=', travel_id)], limit=1, order="id desc")
                                if resp:
                                    continue
                                is_previous = self.env['trip.details'].search([('device_id', '=', device_id)], limit=1, order="id desc")
                                source_long = is_previous.destination_long if is_previous else route_report.get('latitude', '')
                                source_lat = is_previous.destination_lat if is_previous else route_report.get('longitude', '')
                                deviceTime = "".join(route_report.get('deviceTime', '').split(".")[:-1])
                                data['trip_device_date'] = datetime.strptime(deviceTime, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                                data['source_long'] = source_long
                                data['source_lat'] = source_lat
                                data['destination_long'] = route_report.get('latitude', '')
                                data['destination_lat'] = route_report.get('longitude', '')
                                data['battery_level'] = route_report.get('attributes', {}).get('batteryLevel', 0.0)
                                data['total_distance'] = route_report.get('attributes', {}).get('totalDistance', '')
                                data['travel_id'] = travel_id
                                data['value'] = route_report.get('speed', '')
                                data['accuracy'] = route_report.get('accuracy', '')
                                data['device_id'] = device_id
                                self.create(data)
                        elif response.status_code == 401:
                            _logger.info(('Traccar Unauthorized Access: Check traccar credentials %s') % response.text)
                        else :
                            _logger.info(('Traccar Connection Error: %s') % response.text)
            except Exception as e:
                _logger.info(('Error!\Traccar Connection Error: %s') % e)
        return True

    def getDevices(self, uniqueId=False, connection=False):
        devices = False
        connection = connection if connection else self.env['traccar.configure'].search([('active', '=', True)], limit=1)
        if connection:
            url = connection.name + "/api/devices"
            if uniqueId:
                uniqueId = str(uniqueId)
                url = "{}?uniqueId={}".format(url, uniqueId)
            try:
                headers = {'Content-Type' : 'application/json'}
                response = requests.get(url, auth=(connection.user, connection.pwd), headers=headers)
                if response.status_code == 200:
                    deviceData = response.json()
                    devices = {device.get('id', 0):device.get('status', 'unknown') for device in deviceData}
            except Exception as e:
                _logger.info("===========Exception==============: %r", [e])
                pass
        return devices

    def createDevice(self, data, connection=False):
        devices = 0
        connection = connection if connection else self.env['traccar.configure'].search([('active', '=', True)], limit=1)
        if connection:
            url = connection.name + "/api/devices"
            try:
                data = json.dumps(data)
                response = requests.post(url, auth=(connection.user, connection.pwd), data=data, headers={'Content-Type' : 'application/json'}, timeout=1.000)
                if response.status_code == 200:
                    deviceData = response.json()
                    devices = deviceData.get('id', 0)
            except Exception as e:
                _logger.info("===========Exception==============: %r", [e])
                pass
        return devices
