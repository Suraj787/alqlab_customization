# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies,pune and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class MaterialOrder(Document):
	def on_submit(self):
		if self.purchaser:
			todo=frappe.new_doc('ToDo')
			todo.description=self.material_request_type
			todo.reference_type='Material Order'
			todo.reference_name=self.name
			todo.owner=self.purchaser
			todo.save()

			ds=frappe.new_doc('DocShare')
			ds.description=self.material_request_type
			ds.share_doctype='Material Order'
			ds.share_name=self.name
			ds.user=self.purchaser
			ds.read=1
			ds.save()


@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):

	doclist = get_mapped_doc("Material Order", source_name, 	{
		"Material Order": {
			"doctype": "Purchase Order",
		},
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_supplier_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc("Material Order", source_name, {
		"Material Order": {
			"doctype": "Supplier Quotation",
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	doclist = get_mapped_doc("Material Order", source_name, {
		"Material Order": {
			"doctype": "Purchase Invoice",
		}
	}, target_doc)

	return doclist
	
	
