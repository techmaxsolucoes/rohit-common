from frappe import _

def get_data():
    return [
        {
            "label": _("Settings"),
            "items": [
                {
                    "type": "doctype",
                    "name": _("Rohit Settings"),
                },
            ]
        },
        {
            "label": _("Core"),
            "items": [
                {
                    "type": "doctype",
                    "name": _("Country"),
                },
                {
                    "type": "doctype",
                    "name": _("State"),
                },
            ]
        },
    ]