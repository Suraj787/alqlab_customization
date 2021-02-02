from __future__ import unicode_literals
import frappe
from frappe import _

def get_data():
	config =  [
		{
			"label": _("Purchasing"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Material Order",
					"onboard": 1,
					"dependencies": ["Item"],
				},
			]
		},

	]

	return config