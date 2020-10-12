from frappe import _

def get_data():
    return [
        {
            "label": _("Accounts Receivable"),
            "items":[
                {
                    "type": "doctype",
                    "name": _("eWay Bill"),
                }
            ]
        },
        {
            "label": _("Taxes"),
            "items":[
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": _("Clear Tax Import Format"),
                    "doctype": "Purchase Invoice",
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": _("GST Offline Import Format RIGPL"),
                    "label": _("GST Offline Import to Cleartax"),
                    "doctype": "Sales Invoice",
                },
                {
                    "type": "doctype",
                    "name": _("GST Return Status"),
                },
                {
                    "type": "doctype",
                    "name": _("Pull eWay Bills"),
                },
            ]
        },
        {
            "label": _("Settings"),
            "items": [
                {
                    "type": "doctype",
                    "name": _("Rohit Settings"),
                },
                {
                    "type": "doctype",
                    "name": _("State"),
                },
                {
                    "type": "doctype",
                    "name": _("Transporters"),
                },
            ]
        }
    ]