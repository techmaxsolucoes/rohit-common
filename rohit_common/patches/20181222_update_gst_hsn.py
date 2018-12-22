# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def execute():
	sid_no_cetsh = frappe.db.sql("""SELECT name, item_code ,gst_hsn_code, cetsh_number FROM `tabSales Invoice Item` 
		WHERE cetsh_number IS NULL AND gst_hsn_code IS NULL 
		ORDER BY creation""", as_list=1)
	if sid_no_cetsh:
		for sid in sid_no_cetsh:
			sid_doc = frappe.get_doc("Sales Invoice Item", sid[0])
			cetsh_number = frappe.get_value("Item", sid[1], "customs_tariff_number")
			if cetsh_number:
				frappe.db.set_value("Sales Invoice Item", dnd[0], "cetsh_number", cetsh_number)
				frappe.db.set_value("Sales Invoice Item", dnd[0], "gst_hsn_code", cetsh_number)
				frappe.db.commit()
				print("Updated CETSH Number and GST HSN Code in Sales Invoice # " \
					+ sid_doc.parent + " Item No: " + str(sid_doc.idx))
			else:
				print("SI# " + sid_doc.parent + " Item Code: " + sid[1] + \
					" At Row No " + str(sid_doc.idx) + \
					" Does Not Have CETSH Number Linked")

	sid_list = frappe.db.sql("""SELECT name, gst_hsn_code, cetsh_number FROM `tabSales Invoice Item` 
		WHERE cetsh_number IS NOT NULL AND gst_hsn_code IS NULL 
		ORDER BY creation""", as_list=1)
	if sid_list:
		for sid in sid_list:
			cetsh_number = frappe.get_value("Sales Invoice Item", sid[0], "cetsh_number")
			sid_doc = frappe.get_doc("Sales Invoice Item", sid[0])
			frappe.db.set_value("Sales Invoice Item", sid[0], "gst_hsn_code", cetsh_number)
			frappe.db.commit()
			print("Updated GST HSN Code in SI # " + sid_doc.parent + " Item No: " + str(sid_doc.idx))