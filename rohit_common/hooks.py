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
#	"Role": "home_page"
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
# 	"Event": "frappe.core.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.core.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Address": {
		"validate": "rohit_common.rohit_common.validations.address.validate"
		},
	"Asset": {
		"validate": "rohit_common.rohit_common.validations.asset.validate",
		"autoname": "rohit_common.rohit_common.validations.asset.autoname"
	},
	"Asset Category": {
		"validate": "rohit_common.rohit_common.validations.asset_category.validate"
	},
	"Sales Invoice": {
		"validate": "rohit_common.rohit_common.validations.sales_invoice.validate"
		},
	"Purchase Invoice": {
		"validate": "rohit_common.rohit_common.validations.purchase_invoice.validate"
		},
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"rohit_common.tasks.all"
# 	],
# 	"daily": [
# 		"rohit_common.tasks.daily"
# 	],
# 	"hourly": [
# 		"rohit_common.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rohit_common.tasks.weekly"
# 	],
 	"monthly": [
 		"rohit_common.rohit_common.scheduled_tasks.email_queue_delete.execute",
 		"rohit_common.rohit_common.scheduled_tasks.prepared_report_delete.execute"
	]
 }

# Testing
# -------

# before_tests = "rohit_common.install.before_tests"

