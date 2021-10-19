from . import __version__ as app_version

app_name = "ecommerce_integrations"
app_title = "Ecommerce Integrations"
app_publisher = "Frappe"
app_description = "Ecommerce integrations for ERPNext"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "developers@frappe.io"
app_license = "GNU GPL v3.0"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ecommerce_integrations/css/ecommerce_integrations.css"
# app_include_js = "/assets/ecommerce_integrations/js/ecommerce_integrations.js"

# include js, css files in header of web template
# web_include_css = "/assets/ecommerce_integrations/css/ecommerce_integrations.css"
# web_include_js = "/assets/ecommerce_integrations/js/ecommerce_integrations.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ecommerce_integrations/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Shopify Settings": "public/js/shopify/old_settings.js",
	"Sales Order": "public/js/unicommerce/sales_order.js",
	"Sales Invoice": "public/js/unicommerce/sales_invoice.js",
	"Item": "public/js/unicommerce/item.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "ecommerce_integrations.install.before_install"
# after_install = "ecommerce_integrations.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ecommerce_integrations.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		"after_insert": "ecommerce_integrations.shopify.product.upload_erpnext_item",
		"on_update": "ecommerce_integrations.shopify.product.upload_erpnext_item",
		"validate": [
			"ecommerce_integrations.utils.taxation.validate_tax_template",
			"ecommerce_integrations.unicommerce.product.validate_item",
		],
	},
	"Sales Order": {
		"on_update_after_submit": "ecommerce_integrations.unicommerce.order.update_shipping_info",
		"on_cancel": "ecommerce_integrations.unicommerce.status_updater.ignore_pick_list_on_sales_order_cancel",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": ["ecommerce_integrations.shopify.inventory.update_inventory_on_shopify"],
	"daily": [],
	"daily_long": [
		"ecommerce_integrations.zenoti.doctype.zenoti_settings.zenoti_settings.sync_stocks"
	],
	"hourly": ["ecommerce_integrations.shopify.order.sync_old_orders"],
	"hourly_long": [
		"ecommerce_integrations.zenoti.doctype.zenoti_settings.zenoti_settings.sync_invoices",
		"ecommerce_integrations.unicommerce.product.upload_new_items",
		"ecommerce_integrations.unicommerce.status_updater.update_sales_order_status",
		"ecommerce_integrations.unicommerce.status_updater.update_shipping_package_status",
	],
	"weekly": [],
	"monthly": [],
	"cron": {
		# Every five minutes
		"*/5 * * * *": [
			"ecommerce_integrations.unicommerce.order.sync_new_orders",
			"ecommerce_integrations.unicommerce.inventory.update_inventory_on_unicommerce",
		],
	},
}


# bootinfo - hide old doctypes
extend_bootinfo = "ecommerce_integrations.boot.boot_session"

# Testing
# -------

before_tests = "ecommerce_integrations.utils.before_test.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ecommerce_integrations.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ecommerce_integrations.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]
