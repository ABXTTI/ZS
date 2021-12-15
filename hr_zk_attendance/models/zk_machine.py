# -*- coding: utf-8 -*-
###################################################################################
from zk import ZK, const
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: cybrosys(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import pytz
import sys
import datetime
from datetime import timedelta
import logging
import binascii

from . import zklib
from .zkconst import *
from struct import unpack
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Char(string='Biometric Device ID')


class ZkMachine(models.Model):
    _name = 'zk.machine'

    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True)
    force_udp = fields.Boolean(string="Force UDP")
    ommit_ping = fields.Boolean(string="Ommit Ping")
    password = fields.Integer(strinng="Password", default=0)
    time_out = fields.Integer(string="Time Out", default=50)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    device_id = fields.Char(string="Device ID")

    @api.model
    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        # for machine in machines:
        #     machine.download_attendance()

    def get_employees(self):
        _logger.info("++++++++++++Starting Live Capture++++++++++++++++++++++")
        zk = ZK(self.name, port=self.port_no, timeout=self.time_out, password=self.password, force_udp=self.force_udp,
                ommit_ping=self.ommit_ping)
        conn = None
        try:
            print("Connecting Device .........")
            conn = zk.connect()
            print("Disabling Device ............")
            conn.disable_device()
            users = conn.get_users()
            if not self.device_id:
                self.device_id = conn.get_serialnumber()
            # print(users)
            employee_obj = self.env['hr.employee']
            not_exist = []
            for user in users:
                print(user)
                exist = employee_obj.search([('device_id', '=', user.user_id)])
                if not exist:
                    not_exist.append(user.user_id)
                    employee_obj.create({
                        'name': user.name if user.name else user.user_id,
                        'device_id': user.user_id,
                    })

            print_info = employee_obj.search([('device_id', '=', not_exist)])
            print("*************************************", len(print_info))
            print("*************************************", len(not_exist))
        except Exception as e:
            error = "Process terminate Unable to Connect : {}".format(e)
            raise ValidationError(error)
        return conn

    def download_attendance(self):
        self = self.sudo()
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        conn = self.get_employees()
        zk_attendance = self.env['attendance.logs']
        employee_obj = self.env['hr.employee']
        attendances = conn.get_attendance()
        attendance_not_exist = []
        try:
            for att in attendances:
                attendance_exist = zk_attendance.search([('device_id', '=', att.user_id),
                                                         ('punching_time', '=', att.timestamp)])
                if not attendance_exist:
                    print(att)
                    employee_id = employee_obj.search([('device_id', '=', att.user_id)])
                    if employee_id:
                        # print(date
                        # print(type(att.timestamp))
                        zk_attendance.create({
                                                'punching_day': (att.timestamp - timedelta(hours=5)),
                                                'name': employee_id.id,
                                                'device_id': str(att.user_id),
                                                'attendance_type': str(att.status),
                                                'punch_type': str(att.punch),
                                                'punching_time': (att.timestamp - timedelta(hours=5)),
                                                'address_id': self.address_id.id
                                                })
        except Exception as e:
            error = "Process terminate Unable to Connect : {}".format(e)
            raise ValidationError(error)