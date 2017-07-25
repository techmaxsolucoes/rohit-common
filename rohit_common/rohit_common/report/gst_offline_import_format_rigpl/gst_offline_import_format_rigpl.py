# Copyright (c) 2013, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	return [
			_("GSTIN Customer") + "::150", _("Invoice Number") + ":Link/Sales Invoice:100",
			_("Invoice Date") + ":Date:80", _("Grand Total") + ":Currency:80",
			_("Place of Supply") + "::80", _("Net Total") + ":Currency:80",
			_("Type of Sale") + "::80", _("Customer") + ":Link/Customer:200",
			_("Ship Address") + ":Link/Address:200", 
			_("Tax") + ":Link/Sales Taxes and Charges Template:150"
		]

def get_data(filters):
	si_cond = get_conditions(filters)
	data = frappe.db.sql("""SELECT ad.gstin, si.name, si.posting_date, si.base_grand_total,
		si.base_net_total, si.customer, si.shipping_address_name, 
		si.taxes_and_charges
		FROM `tabSales Invoice` si, `tabAddress` ad
		WHERE ad.name = si.shipping_address_name AND si.docstatus = 1 %s
		ORDER BY si.posting_date, si.name""" %(si_cond), as_list=1)

	for d in data:
		tax_doc = frappe.get_doc("Sales Taxes and Charges Template", d[7])
		state_code = frappe.get_value("State", tax_doc.state, "state_code_numeric")
		d.insert(4, str(state_code) + "-" + str(tax_doc.state))
		if len(d[0]) == 15:
			d.insert(6,"B2B(4)")
		else:
			is_export = tax_doc.is_export
			if is_export == 1:
				d.insert(6,"EXP(6)")
			else:
				if d[3] > 250000:
					d.insert(6,"B2CL(5)")
				else:
					d.insert(6,"B2CS(7)")

	return data


def get_conditions(filters):
	si_cond = ""
	if filters.get("from_date"):
		si_cond += " AND si.posting_date >= '%s'" %filters["from_date"]

	if filters.get("to_date"):
		si_cond += " AND si.posting_date <= '%s'" %filters["to_date"]

	if filters.get("letter_head"):
		si_cond += " AND si.letter_head = '%s'" %filters["letter_head"]

	if filters.get("taxes"):
		si_cond += " AND si.taxes_and_charges = '%s'" %filters["taxes"]

	return si_cond