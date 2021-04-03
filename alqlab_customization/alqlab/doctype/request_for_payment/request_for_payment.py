# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies,pune and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from six import string_types, iteritems

class RequestForPayment(Document):
	pass
	
@frappe.whitelist()
def get_outstanding_reference_documents(args):
	
	condition = ""
	data = []
	if isinstance(args, string_types):
		args = json.loads(args)
	if args.get("from_posting_date") and args.get("to_posting_date"):
		condition +="where posting_date between '{0}' and '{1}'".format(args.get("from_posting_date") , args.get("to_posting_date"))
		print(condition)
	if args.get("supplier"):
		condition +="and supplier = '{0}'".format(args.get("supplier"))


	data = frappe.db.sql("""select 
						name as purchase_invoice,
						project,
						posting_date,
						supplier,
						currency,
						grand_total,
						base_grand_total 
						from `tabPurchase Invoice` 
						{0}""".format(condition),as_dict = 1 )

	return data
