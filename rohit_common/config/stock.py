from frappe import _

def get_data():
    return[
        {
            "label": _("Stock Reports"),
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": _("Stock Ledger Normal"),
                    "label": _("Custom Stock Ledger for RIGPL"),
                    "doctype": "Stock Ledger Entry",
                },
            ]
        }
    ]