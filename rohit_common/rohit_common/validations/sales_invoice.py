# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
	
def validate(doc,method):

	bill_tin =frappe.db.get_value("Address", doc.customer_address ,"tin_no")
	bill_excise =frappe.db.get_value("Address", doc.customer_address ,"excise_no")
	ship_tin =frappe.db.get_value("Address", doc.shipping_address_name ,"tin_no")
	ship_excise =frappe.db.get_value("Address", doc.shipping_address_name ,"excise_no")
	ship_gstin = frappe.db.get_value("Address", doc.shipping_address_name ,"gstin")
	bill_gstin = frappe.db.get_value("Address", doc.customer_address ,"gstin")
	ship_state = frappe.db.get_value("Address", doc.shipping_address_name, "state_rigpl")
	ship_country = frappe.db.get_value("Address", doc.shipping_address_name, "country")
	template_doc = frappe.get_doc("Sales Taxes and Charges Template", doc.taxes_and_charges)
	'''
	doc.ship_gstin = ship_gstin
	doc.bill_gstin = bill_gstin
	'''	
	
	#Check if Shipping State is Same as Template State then check if the tax template is LOCAL
	#Else if the States are different then the template should NOT BE LOCAL
	if ship_state == template_doc.state:
		if template_doc.is_local_sales != 1:
			frappe.throw(("Selected Tax {0} is NOT LOCAL Tax but Shipping Address is \
				in Same State {1}, hence either change Shipping Address or Change the \
				Selected Tax").format(doc.taxes_and_charges, ship_state))
	elif ship_country == 'India' and ship_state != template_doc.state:
		if template_doc.is_local_sales == 1:
			frappe.throw(("Selected Tax {0} is LOCAL Tax but Shipping Address is \
				in Different State {1}, hence either change Shipping Address or Change the \
				Selected Tax").format(doc.taxes_and_charges, ship_state))
	elif ship_country != 'India': #Case of EXPORTS
		if template_doc.state is not None:
			frappe.throw(("Selected Tax {0} is for Indian Sales but Shipping Address is \
				in Different Country {1}, hence either change Shipping Address or Change the \
				Selected Tax").format(doc.taxes_and_charges, ship_country))
