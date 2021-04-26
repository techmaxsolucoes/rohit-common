// Copyright (c) 2016, Rohit Industries Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Backend Database Analysis RIGPL"] = {
	"filters": [
		{
			"fieldname":"all_tables",
			"label": "All DB Size",
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname":"dt",
			"label": "DocType",
			"fieldtype": "Link",
			"options": "DocType",
			"get_query": function(){ return {'filters': [['DocType', 'issingle','=', 0]]}}
		},
	]
};
