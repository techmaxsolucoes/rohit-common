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
		"Customer:Link/Customer:200", "Sale Type::150", "TIN# on Master::100",
		"Net Total:Currency:100", "Net Total Before Sales Tax:Currency:100", "Sales Tax %age:Percent:50",
		"Total Sales Tax Amount:Currency:100", "Grand Total:Currency:100"
	]

def get_invoices(filters):
	conditions = get_conditions(filters)
	
	query = """SELECT si.customer, si.taxes_and_charges, si.customer_address, sum(si.net_total),
	sum(si_tax.total), si_tax.rate, sum(si_tax.tax_amount), 
	sum(si.grand_total)
	FROM `tabSales Invoice` si, `tabSales Taxes and Charges` si_tax
	WHERE si.docstatus = 1 AND si_tax.parent = si.name 
	AND (select tax_type from `tabAccount` where 
	name = si_tax.account_head) REGEXP 'Sales Tax' %s
	GROUP BY si.customer, si.taxes_and_charges
	ORDER BY si.customer""" % conditions
	
	#frappe.msgprint (query)
	
	si= frappe.db.sql(query, as_list=1)
	tin = frappe.db.sql ("""SELECT name, customer, tin_no from `tabAddress` """, as_list=1)
	
	#frappe.msgprint(len(si))
	
	for i in range(0, len(si)):	
		si[i][4] = si[i][4]-si[i][6]
		for j in range(0,len(tin)):
			if si[i][2]==tin[j][0]:
				si[i][2]= tin[j][2]

	return si
	

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " and si.posting_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " and si.posting_date <= '%s'" % filters["to_date"]
	
	if filters.get("account"):
		conditions += " and si.debit_to = '%s'" % filters["account"]

	if filters.get("letter_head"):
		conditions += " and si.letter_head = '%s'" % filters["letter_head"]


	return conditions
