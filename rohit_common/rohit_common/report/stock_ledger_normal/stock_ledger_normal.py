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
		{
			"label": "Date",
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 80
		},
		{
			"label": "Time",
			"fieldname": "time",
			"fieldtype": "Time",
			"width": 70
		},
		{
			"label": "Item",
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 130
		},
		{
			"label": "Description",
			"fieldname": "description",
			"width": 250
		},
		{
			"label": "Qty",
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 60
		},
		{
			"label": "Balance",
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 90
		},
		{
			"label": "Warehouse",
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 120
		},
		{
			"label": "Voucher No",
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 130
		},
		{
			"label": "Voucher Type",
			"fieldname": "voucher_type",
			"width": 140
		},
		{
			"label": "Customer or Supplier Name",
			"fieldname": "cust_name",
			"fieldtype": "Dynamic Link",
			"options": "master_type",
			"width": 150
		},
		{
			"label": "Name",
			"fieldname": "name",
			"width": 100
		},
		{
			"label": "Master Type",
			"fieldname": "master_type",
			"width": 50
		},
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