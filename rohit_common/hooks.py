#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

app_name = "rohit_common"
app_title = "Rohit ERPNext Extensions (Common)"
app_publisher = "Rohit Industries Ltd."
app_description = "Rohit ERPNext Extensions (Common)"
app_icon = "icon-paper-clip"
app_color = "#007AFF"
app_email = "aditya@rigpl.com"
app_url = "https://github.com/adityaduggal/rohit_common"
app_version = "0.0.1"
fixtures = ["Custom Field"]
hide_in_installer = True

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/rohit_common/css/rohit_common.css"
# app_include_js = "/assets/rohit_common/js/rohit_common.js"

# include js, css files in header of web template
# web_include_css = "/assets/rohit_common/css/rohit_common.css"
# web_include_js = "/assets/rohit_common/js/rohit_common.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#   "Role": "home_page"
# }

# Installation
# ------------

# before_install = "rohit_common.install.before_install"
# after_install = "rohit_common.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rohit_common.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#   "Event": "frappe.core.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#     "File": "rohit_common.rohit_common.validations.file.has_permission"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Address": {
        "autoname": "rohit_common.rohit_common.validations.address.autoname",
        "validate": "rohit_common.rohit_common.validations.address.validate"
    },
    "Asset": {
        "validate": "rohit_common.rohit_common.validations.asset.validate",
        "autoname": "rohit_common.rohit_common.validations.asset.autoname"
    },
    "Asset Category": {
        "validate": "rohit_common.rohit_common.validations.asset_category.validate"
    },
    "Contact": {
        "autoname": "rohit_common.rohit_common.validations.contact.autoname",
        "validate": "rohit_common.rohit_common.validations.contact.validate"
    },
    "Customer": {
        "autoname": "rohit_common.rohit_common.validations.customer.autoname",
        "validate": "rohit_common.rohit_common.validations.customer.validate"
    },
    "DocShare": {
        "validate": "rohit_common.rohit_common.validations.docshare.validate",
        "on_trash": "rohit_common.rohit_common.validations.docshare.on_trash"
    },
    "File": {
        "before_insert": "rohit_common.rohit_common.validations.file.before_insert",
        "validate": "rohit_common.rohit_common.validations.file.validate",
        "on_trash": "rohit_common.rohit_common.validations.file.on_trash"
    },
    "Payment Terms Template": {
        "validate": "rohit_common.rohit_common.validations.payment_terms_template.validate"
    },
    "Sales Invoice": {
        "validate": "rohit_common.rohit_common.validations.sales_invoice.validate",
        "on_update_after_submit": "rohit_common.rohit_common.validations.sales_invoice.on_update",
        "on_submit": "rohit_common.rohit_common.validations.sales_invoice.on_submit"
    },
    "Sales Taxes and Charges Template": {
        "validate": "rohit_common.rohit_common.validations.stc_template.validate"
    },
    "Purchase Invoice": {
        "validate": "rohit_common.rohit_common.validations.purchase_invoice.validate"
    },
    "Supplier": {
        "autoname": "rohit_common.rohit_common.validations.supplier.autoname",
        "validate": "rohit_common.rohit_common.validations.supplier.validate"
    },
    "User": {
        "validate": "rohit_common.rohit_common.validations.user.validate"
    },
    #   "*": {
    #       "on_update": "method",
    #       "on_cancel": "method",
    #       "on_trash": "method"
    #   }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        "10 2 * * *": [
            "rohit_common.rohit_common.scheduled_tasks.auto_update_gstin_status.enqueue_gstin_update"
            # Runs everyday at 2:10 AM
        ],
    },
    "all": [
        "rohit_common.rohit_common.scheduled_tasks.auto_refresh_gstin_auth_code.execute"
    ],
    "daily": [
        "rohit_common.rohit_common.scheduled_tasks.auto_update_from_erp.update_export_invoices"
       ],
    "hourly": [
        "rohit_common.rohit_common.scheduled_tasks.delete_unneeded_files.check_correct_folders",
        "rohit_common.utils.background_doc_processing.enqueue_bg"
    ],
    "weekly_long": [
        "rohit_common.rohit_common.scheduled_tasks.auto_delete_version.enqueue_deletion",
        "rohit_common.rohit_common.scheduled_tasks.delete_unneeded_files.execute"
    ],
    "monthly": [
        "rohit_common.rohit_common.scheduled_tasks.email_queue_delete.execute"
    ]
}

# Testing
# -------

# before_tests = "rohit_common.install.before_tests"
