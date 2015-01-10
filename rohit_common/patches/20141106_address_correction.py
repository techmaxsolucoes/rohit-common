# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.utils.fixtures import sync_fixtures

sync_fixtures()

def execute():
	#correct the address table
	for name in frappe.db.sql_list("""select name from tabAddress"""):
		add = frappe.get_doc("Address", name)
		if add.address_type not in ("Billing" , "Shipping", "Office", "Personal", "Plant", "Postal", "Shop", "Subsidiary", "Warehouse", "Other"):
			frappe.db.set_value("Address", add.name, "address_type", "Billing")
		if not add.address_line1:
			frappe.db.set_value("Address", add.name, "address_line1", "NA")
		if not add.city:
			frappe.db.set_value("Address", add.name, "city", "NA")
		if not add.country:
			frappe.db.set_value("Address", add.name, "country", "India")
		if not add.phone:
			frappe.db.set_value("Address", add.name, "phone", "NA")
		if add.customer:
			tin = frappe.db.get_value ("Customer", add.customer, "tin_no")
			ecc = frappe.db.get_value ("Customer", add.customer, "excise_no")
			frappe.db.set_value("Address", add.name, "tin_no", tin)
			frappe.db.set_value("Address", add.name, "excise_no", ecc)
			frappe.db.set_value("Address", add.name, "service_tax_no", "NA")
		if add.supplier:
			tin = frappe.db.get_value ("Supplier", add.supplier, "tin_no")
			ecc = frappe.db.get_value ("Supplier", add.supplier, "excise_no")
			stax = frappe.db.get_value("Supplier",add.supplier, "service_tax_no")
			frappe.db.set_value("Address", add.name, "tin_no", tin)
			frappe.db.set_value("Address", add.name, "excise_no", ecc)
			frappe.db.set_value("Address", add.name, "service_tax_no", stax)
