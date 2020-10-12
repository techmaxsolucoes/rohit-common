from frappe import _

def get_data():
    return[
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": _("Asset Analysis"),
                    "label": _("Asset Analysis for RIGPL"),
                    "doctype": "Asset Category",
                },
            ]
        }
    ]