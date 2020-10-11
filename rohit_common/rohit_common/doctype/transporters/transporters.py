# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document


class Transporters(Document):
	def validate(self):
		if self.fedex_credentials == 1:
			self.track_on_shipway = 0
			self.fedex_tracking_only = 0
			self.dtdc_credentials = 0
			self.self_pickup = 0
		elif self.track_on_shipway == 1:
			self.fedex_tracking_only = 0
			self.fedex_credentials = 0
			self.dtdc_credentials = 0
			self.self_pickup = 0
		elif self.fedex_tracking_only == 1:
			self.track_on_shipway = 0
			self.fedex_credentials = 0
			self.dtdc_credentials = 0
			self.self_pickup = 0
		elif self.dtdc_credentials == 1:
			self.track_on_shipway = 0
			self.fedex_credentials = 0
			self.fedex_tracking_only = 0
			self.self_pickup = 0
		elif self.self_pickup == 1:
			self.track_on_shipway = 0
			self.fedex_credentials = 0
			self.fedex_tracking_only = 0
			self.dtdc_credentials = 0