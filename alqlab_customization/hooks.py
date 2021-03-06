# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "alqlab_customization"
app_title = "alqlab"
app_publisher = "bizmap technologies,pune"
app_description = "alqlab customization"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "suraj@bizmap.in"
app_license = "MIT"
app_logo_url = '/assets/alqlab_customization/images/forPR.png'

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/alqlab_customization/css/alqlab_customization.css"
app_include_js = "/assets/alqlab_customization/js/supplierQuickEntry.js"

# include js, css files in header of web template
# web_include_css = "/assets/alqlab_customization/css/alqlab_customization.css"
# web_include_js = "/assets/alqlab_customization/js/alqlab_customization.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
				"Payment Request":"public/js/payment_request.js"
}
# Home Pages
# ----------
# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "alqlab_customization.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "alqlab_customization.install.before_install"
# after_install = "alqlab_customization.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "alqlab_customization.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Supplier": {
		"on_update": "alqlab_customization.alqlab.doctype.supplier.create_address_and_contact",
	},
	"Purchase Invoice":{
		"validate":"alqlab_customization.alqlab.doctype.purchase_invoice.validate",
	}
	
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"alqlab_customization.tasks.all"
# 	],
# 	"daily": [
# 		"alqlab_customization.tasks.daily"
# 	],
# 	"hourly": [
# 		"alqlab_customization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"alqlab_customization.tasks.weekly"
# 	]
# 	"monthly": [
# 		"alqlab_customization.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "alqlab_customization.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "alqlab_customization.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "alqlab_customization.task.get_dashboard_data"
# }

