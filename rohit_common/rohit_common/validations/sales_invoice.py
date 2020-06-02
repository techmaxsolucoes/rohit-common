# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint
	
def validate(doc,method):
	ship_pincode = frappe.db.get_value("Address", doc.shipping_address_name ,"pincode")
	bill_pincode = frappe.db.get_value("Address", doc.customer_address ,"pincode")
	ship_gstin = frappe.db.get_value("Address", doc.shipping_address_name ,"gstin")
	bill_gstin = frappe.db.get_value("Address", doc.customer_address ,"gstin")
	bill_state = frappe.db.get_value("Address", doc.customer_address, "state_rigpl")
	ship_country = frappe.db.get_value("Address", doc.shipping_address_name, "country")
	template_doc = frappe.get_doc("Sales Taxes and Charges Template", doc.taxes_and_charges)

	if ship_pincode is None:
		frappe.throw(("Shipping Pincode is Mandatory or NA, please correct it in Shipping Address {0}").\
			format(frappe.get_desk_link('Address', doc.shipping_address_name)))

	if bill_pincode is None:
		frappe.throw(("Billing Pincode is Mandatory or NA, please correct it in Billing Address {0}").\
			format(frappe.get_desk_link('Address', doc.shipping_address_name)))

	doc.shipping_address_gstin = ship_gstin
	doc.billing_address_gstin = bill_gstin
	
	for items in doc.items:
		custom_tariff = frappe.db.get_value("Item", items.item_code, "customs_tariff_number")
		if custom_tariff:
			if len(custom_tariff) == 8:
				items.gst_hsn_code = custom_tariff 
			else:
				frappe.throw(("Item Code {0} in line# {1} has a Custom Tariff {2} which not  \
					8 digit, please get the Custom Tariff corrected").\
					format(items.item_code, items.idx, custom_tariff))
		else:
			frappe.throw(("Item Code {0} in line# {1} does not have linked Customs \
				Tariff in Item Master").format(items.item_code, items.idx))
	
	#Check if Shipping State is Same as Template State then check if the tax template is LOCAL
	#Else if the States are different then the template should NOT BE LOCAL
	if bill_state == template_doc.state and template_doc.is_export == 0:
		if template_doc.is_local_sales != 1:
			frappe.throw(("Selected Tax {0} is NOT LOCAL Tax but Billing Address is \
				in Same State {1}, hence either change Billing Address or Change the \
				Selected Tax").format(doc.taxes_and_charges, bill_state))
	elif ship_country == 'India' and bill_state != template_doc.state:
		if template_doc.is_local_sales == 1:
			frappe.throw(("Selected Tax {0} is LOCAL Tax but Billing Address is \
				in Different State {1}, hence either change Billing Address or Change the \
				Selected Tax").format(doc.taxes_and_charges, bill_state))
	elif ship_country != 'India': #Case of EXPORTS
		if template_doc.is_export != 1:
			frappe.throw(("Selected Tax {0} is for Indian Sales but Billing Address is \
				in Different Country {1}, hence either change Billing Address or Change the \
				Selected Tax").format(doc.taxes_and_charges, ship_country))
	#lastly check the child taxes table are in sync with the template
	check_taxes_integrity(doc, method, template_doc)


def check_taxes_integrity(doc,method, template):
	if doc.taxes:
		for tax in doc.taxes:
			check = 0
			for temp in template.taxes:
				if tax.idx == temp.idx and check == 0:
					check = 1
					if tax.charge_type != temp.charge_type or tax.row_id != temp.row_id or \
						tax.account_head != temp.account_head or tax.included_in_print_rate \
						!= temp.included_in_print_rate or tax.rate != temp.rate:
							frappe.throw(("Selected Tax {0}'s table does not match with tax table \
								of Invoice# {1}. Check Row # {2} or reload Taxes").\
								format(doc.taxes_and_charges, doc.name, tax.idx))
			if check == 0:
				frappe.throw(("Selected Tax {0}'s table does not match with tax table \
					of Invoice# {1}. Check Row # {2} or reload Taxes").\
					format(doc.taxes_and_charges, doc.name, tax.idx))
	else:
		frappe.throw(("Empty Tax Table is not Allowed for Sales Invoice {0}").format(doc.name))

