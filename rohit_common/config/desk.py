from frappe import _

def get_data():
    return [
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": _("File Attachment Analysis RIGPL"),
                    "label": _("File Attachments"),
                    "doctype": "File",
                },
            ]
        }
    ]