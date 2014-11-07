# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
	
def validate(doc,method):
	bill_tin =frappe.db.get_value("Address", doc.customer_address ,"tin_no")
	bill_excise =frappe.db.get_value("Address", doc.customer_address ,"excise_no")
	ship_tin =frappe.db.get_value("Address", doc.shipping_address_name ,"tin_no")
	ship_excise =frappe.db.get_value("Address", doc.shipping_address_name ,"excise_no")
	
	if (doc.tin_no != bill_tin):
		frappe.msgprint("TIN No does no match with Billing Address TIN No, please reload Billing Address", raise_exception=1)
	if (doc.excise_no != bill_excise):
		frappe.msgprint("Excise No does no match with Billing Address Excise No, please reload Billing Address", raise_exception=1)
	if (doc.shipping_tin_no != ship_tin):
		frappe.msgprint("TIN No does no match with Shipping Address TIN No, please reload Shipping Address", raise_exception=1)
	if (doc.shipping_excise_no != ship_excise):
		frappe.msgprint("Excise No does no match with Shipping Address Excise No, please reload Shipping Address", raise_exception=1)
