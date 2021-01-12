// Copyright (c) 2016, Rohit Industries Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["File Attachment Analysis RIGPL"] = {
	"filters": [
		{
			"fieldname":"summary_dt",
			"label": "Summary Doctype Wise",
			"fieldtype": "Check",
			"reqd": 0,
			"default":1
		},
		{
			"fieldname":"summary_fol",
			"label": "Summary Folder Wise",
			"fieldtype": "Check",
			"reqd": 0,
			"default":0
		},
		{
			"fieldname":"is_folder",
			"label": "Is Folder",
			"fieldtype": "Check",
			"reqd": 0,
			"default":0
		},
		{
			"fieldname":"archive",
			"label": "Important for Archive",
			"fieldtype": "Check",
			"reqd": 0,
			"default":0
		},
		{
			"fieldname":"deletion",
			"label": "Marked for Deletion",
			"fieldtype": "Check",
			"reqd": 0,
			"default":0
		},
		{
			"fieldname":"no_parent",
			"label": "No Parent",
			"fieldtype": "Check",
			"reqd": 0,
			"default":0
		},
		{
			"fieldname":"on_server",
			"label": "Available on Server",
			"fieldtype": "Select",
			"reqd": 0,
			"options": "\nYes\nNo"
		},
		{
			"fieldname":"private",
			"label": "Private or Public",
			"fieldtype": "Select",
			"options": "\nAll\nOnly Private\nOnly Public",
			"reqd": 1,
			"default": "All"
		},
		{
			"fieldname":"doctype",
			"label": "Attached to Doctype",
			"fieldtype": "Link",
			"options": "DocType",
			"reqd": 0,
			"get_query": function(){ return {'filters': [['DocType', 'istable','!=', 1]]}}
		},
		{
			"fieldname":"dt_types",
			"label": "Attached to Doctypes",
			"fieldtype": "Select",
			"options": "\nAll\nNone",
		},
		{
			"fieldname":"folder",
			"label": "Folder",
			"fieldtype": "Link",
			"options": "File",
			"get_query": function(){ return {'filters': [['File', 'is_folder','=', 1]]}}
		},
	]
}
