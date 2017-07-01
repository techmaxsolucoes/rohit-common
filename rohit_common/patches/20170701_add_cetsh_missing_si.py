# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.utils.fixtures import sync_fixtures

sync_fixtures()

def execute():
	#Add the CETSH Number in Sales Invoice Items where MISSING
	sales_invoice_items = frappe.db.sql("""SELECT sii.name, sii.item_code, sii.parent, 
		si.posting_date, sii.idx
		FROM `tabSales Invoice Item` sii, `tabSales Invoice` si
		WHERE sii.cetsh_number IS NULL AND si.docstatus = 1 
			AND sii.parent = si.name""", as_dict= 1)
	for si_items in sales_invoice_items:
		cetsh = frappe.db.sql("""SELECT ct.name 
			FROM `tabCustoms Tariff Number` ct, `tabItem` it
			WHERE ct.name = it.customs_tariff_number
			AND it.name = '%s'"""%(si_items.item_code), as_dict = 1)
		if cetsh:
			frappe.db.set_value("Sales Invoice Item", si_items.name, "cetsh_number", cetsh[0].name)
			print ("Sales Invoice: " + si_items.parent + " Posted On: " + str(si_items.posting_date) + \
				" Updated with CETSH = " + cetsh[0].name + "for Row# " + str(si_items.idx))
		else:
			frappe.db.set_value("Sales Invoice Item", si_items.name, "cetsh_number", "NA")
			print ("Sales Invoice: " + si_items.parent + " Posted On: " + str(si_items.posting_date) + \
				" Updated with CETSH = NA for Row# " + str(si_items.idx))
