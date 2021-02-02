# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies,pune and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MaterialOrder(Document):
	def on_submit(self):
		if self.purchaser:
			todo=frappe.new_doc('ToDo')
			todo.description=self.material_request_type
			todo.reference_type='Material Order'
			todo.reference_name=self.name
			todo.owner=self.purchaser
			todo.save()
