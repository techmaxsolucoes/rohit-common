# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint

def execute():
	#correct the address type
	for name in frappe.db.sql_list("""select name from tabAddress 
		where address_type NOT IN ("Billing" , "Shipping", "Office", "Personal", "Plant", "Postal", "Shop", "Subsidiary", "Warehouse", "Other")""")
		add = frappe.get_doc("Address", name)
		frappe.db.set_value("Address", add.name, address_type, "Billing")
