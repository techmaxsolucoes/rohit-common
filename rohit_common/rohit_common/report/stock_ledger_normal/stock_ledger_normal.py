# Copyright (c) 2013, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_sl_entries(filters)

	return columns, data

def get_columns():


	return [
		"Date:Date:80", "Time:Time:70" ,"Item:Link/Item:130", "Description::250",
		"Qty:Float:60", "Balance:Float:90", "Warehouse::120", "Voucher No:Dynamic Link/Voucher Type:130", 
		"Voucher Type::140", "Customer or Supplier Name:Dynamic Link/Master Type:150","Name::100", "Master Type::50"
	]

def get_sl_entries(filters):
	conditions, conditions_item = get_conditions(filters)

	data = frappe.db.sql("""SELECT sle.posting_date, sle.posting_time, sle.item_code, it.description,
		sle.actual_qty, sle.qty_after_transaction, sle.warehouse, sle.voucher_no, sle.voucher_type,
		'X', sle.name, 'X' 
		FROM `tabStock Ledger Entry` sle, `tabItem` it
		WHERE sle.is_cancelled = "No" AND sle.item_code = it.name %s %s
		ORDER BY sle.posting_date DESC, sle.posting_time DESC, sle.name DESC"""
		% (conditions, conditions_item), as_list=1)

	for d in data:
		if d[8] in ('Delivery Note', 'Sales Invoice'):
			dn_doc = frappe.get_doc(d[8], d[7])
			d[9] = dn_doc.customer
			d[11] = 'Customer'
		
		elif d[8] in ('Purchase Receipt', 'Purchase Invoice'):
			dn_doc = frappe.get_doc(d[8], d[7])
			d[9] = dn_doc.supplier
			d[11] = 'Supplier'
		else:
			d[9] = None
			d[11] = None

	return data
def get_conditions(filters):
	conditions = ""
	conditions_item = ""

	if filters.get("item"):
		conditions += " AND sle.item_code = '%s'" % filters["item"]
		conditions_item += " AND it.name = '%s'" % filters["item"]

	if filters.get("warehouse"):
		conditions += " AND sle.warehouse = '%s'" % filters["warehouse"]

	if filters.get("from_date"):
		conditions += " AND sle.posting_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " AND sle.posting_date <= '%s'" % filters["to_date"]

	return conditions, conditions_item