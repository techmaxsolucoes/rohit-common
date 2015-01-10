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
	columns = [
		"Supplier:Link/Supplier:200", "Purchase Type::180", "TIN# on Master::100",
		"Net Total::100", "Net Total Before Sales Tax::100", "Sales Tax %age::50",
		"Total Sales Tax Amount::100", "Grand Total::100", "ST % Calculated::50"
		]
	
	return columns

def get_invoices(filters):
	conditions = get_conditions(filters)

	query = """SELECT pi.supplier, pi.taxes_and_charges, pi.supplier_address, sum(DISTINCT(pi.net_total)),
	SUM(pi_tax.total - pi_tax.tax_amount), pi_tax.rate, sum(pi_tax.tax_amount), 
	sum(DISTINCT(pi.grand_total)), null
	FROM `tabPurchase Invoice` pi, `tabPurchase Taxes and Charges` pi_tax
	WHERE pi.docstatus = 1 AND pi_tax.parent = pi.name 
	AND (select tax_type from `tabAccount` where 
	name = pi_tax.account_head) REGEXP 'Sales Tax' %s
	GROUP BY pi.supplier, pi.taxes_and_charges
	ORDER BY pi.supplier""" % conditions

	query2 = """SELECT pi.supplier, pi.taxes_and_charges, pi.supplier_address, sum(DISTINCT(pi.net_total)),
	sum(DISTINCT(pi_tax.total)), null, null , sum(DISTINCT(pi.grand_total)), null
	FROM `tabPurchase Invoice` pi, `tabPurchase Taxes and Charges` pi_tax
	WHERE pi.docstatus = 1 AND pi_tax.parent = pi.name 
	AND (select tax_type from `tabAccount` where 
	name = pi_tax.account_head) REGEXP 'Sales Tax' %s
	GROUP BY pi.supplier, pi.supplier_address, pi.taxes_and_charges
	ORDER BY pi.supplier""" % conditions
	
	#frappe.msgprint (query)
	
	si= frappe.db.sql(query, as_list=1)
	tin = frappe.db.sql ("""SELECT name, supplier, tin_no from `tabAddress` """, as_list=1)
	
	#frappe.msgprint(len(si))
	
	#for i in range(0, len(si)):	
		#si[i][4] = si[i][4]-si[i][6]
		#si[i][8] = round((si[i][6]*100)/si[i][4],2)
		#for j in range(0,len(tin)):
		#	if si[i][2]==tin[j][0]:
		#		si[i][2]= tin[j][2]

	return si
	

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " and pi.posting_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " and pi.posting_date <= '%s'" % filters["to_date"]
	
	if filters.get("supplier"):
		conditions += " and pi.supplier = '%s'" % filters["supplier"]

	if filters.get("letter_head"):
		conditions += " and pi.letter_head = '%s'" % filters["letter_head"]


	return conditions
