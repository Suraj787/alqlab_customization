# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies,pune and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def validate(doc,method):
    
    if doc.material_order_:
        frappe.db.set_value('Material Order',doc.material_order_,"workflow_state","Completed")
