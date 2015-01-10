// Copyright (c) 2013, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["ST Return Purchase"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": get_today()
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname":"letter_head",
			"label": "Letter Head",
			"fieldtype": "Link",
			"options": "Letter Head"
		},
		{
			"fieldname":"tax_type",
			"label": "Tax Type",
			"fieldtype": "Select",
			"options": "Excise\nSales Tax\nService Tax"
		},
		{
			"fieldname":"invoice_wise",
			"label": "Invoice Wise",
			"fieldtype": "Check"
		},
		{
			"fieldname":"tax_wise",
			"label": "Tax Wise",
			"fieldtype": "Check"
		}
	]
}
