# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.utils.fixtures import sync_fixtures

sync_fixtures()

def execute():
	#Transfer the address state field from data to link field
	address_list = frappe.db.sql("""SELECT name FROM `tabAddress` 
		WHERE docstatus = 0""",as_list=1)
	for add in address_list:
		add_doc = frappe.get_doc("Address", add[0])
		frappe.db.set_value("Address", add_doc.name, "state_rigpl", add_doc.state)
		print ("Update Address: " + add_doc.name + " State value to " + str(add_doc.state))
		
