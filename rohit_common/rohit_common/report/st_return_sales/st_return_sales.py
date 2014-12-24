# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_invoices(filters)
	return columns, data
	
def get_columns():
	return [
		"Customer:Link/Customer:130", "Sale Type::150", "TIN# on Master:Int:100",
		"Net Total:Currency:80", "Net Total Before Sales Tax:Currency:80", "Sales Tax %age:Float:30",
		"Total Sales Tax Amount:Currency:100", "Grand Total:Currency:100"
	]

def get_invoices(filters):
	conditions = get_conditions(filters)
	
	query = """SELECT si.customer, si.taxes_and_charges, null, sum(si.net_total),
	null,null,null,sum(si.grand_total)
	FROM `tabSales Invoice` si WHERE si.docstatus = 1 %s
	GROUP BY si.customer, si.taxes_and_charges
	ORDER BY si.customer""" % conditions
	
	#frappe.msgprint(query)
	
	si= frappe.db.sql(query, as_list=1)
	
	#tax_query = """sum(si_tax. """ %conditions

	return si
	

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " and si.posting_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " and si.posting_date <= '%s'" % filters["to_date"]
	
	if filters.get("account"):
		conditions += " and si.debit_to = '%s'" % filters["account"]


	return conditions
