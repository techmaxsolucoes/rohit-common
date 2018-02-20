# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.utils.fixtures import sync_fixtures
from erpnext.regional.india import states

sync_fixtures()

def execute():
	#Update State Field from RIGPL State
	add_list = frappe.db.sql("""SELECT name FROM `tabAddress`""", as_list =1)
	row = 0
	row1 = 0
	row2 = 0
	for add in add_list:
		add_doc = frappe.get_doc("Address", add[0])
		if add_doc.country == 'India':
			if add_doc.state != add_doc.state_rigpl and add_doc.state_rigpl is not None:
				frappe.db.set_value("Address", add_doc.name, "state", add_doc.state_rigpl)
				row += 1
				print("Row No: " + str(row) + " Address: " + add_doc.name + \
					" State Field Updated to: " + add_doc.state_rigpl)

		if add_doc.gst_state != add_doc.state_rigpl:
			if add_doc.country == 'India' and add_doc.state_rigpl is not None:
				frappe.db.set_value("Address", add_doc.name, "gst_state", add_doc.state_rigpl)
				row1 += 1
				print("Row No: " + str(row1) + " Address: " + add_doc.name + \
					" GST State Field Update to: " + add_doc.state_rigpl)