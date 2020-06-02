// Copyright (c) 2016, Rohit Industries Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GST Offline Import Format RIGPL"] = {
	"filters": [
		{
			"fieldname":"type",
			"label": "Transaction Type",
			"fieldtype": "Select",
			"options": "\nSales Invoice\nPurchase Invoice",
			"reqd": 1,
			"default": "Sales Invoice",
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"reqd": 0,
			"options": "Customer",
		},
		{
			"fieldname":"supplier",
			"label": __("Supplie"),
			"fieldtype": "Link",
			"reqd": 0,
			"options": "Supplier",
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname":"letter_head",
			"label": __("Letter Head"),
			"fieldtype": "Link",
			"reqd": 0,
			"options": "Letter Head",
			"default": frappe.defaults.get_default("letter_head"),
		},
		{
			"fieldname":"taxes",
			"label": __("Tax"),
			"fieldtype": "Link",
			"options": "Sales Taxes and Charges Template",
		},
		{
			"fieldname":"item_wise",
			"label": __("Item Wise"),
			"fieldtype": "Check",
		},
		{
			"fieldname":"hsn",
			"label": __("HSN Wise"),
			"fieldtype": "Check",
		},
	]
}
