from frappe import _

def get_data():
	return [
		{
			"label": _("Rohit Reports"),
			"icon": "icon-paper-clip",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Modified Purchase Register",
					"doctype": "Purchase Invoice",
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Modified Sales Register",
					"doctype": "Sales Invoice",
				},
			]
		}
	]
