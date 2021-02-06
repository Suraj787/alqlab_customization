// Copyright (c) 2021, bizmap technologies,pune and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Order', {
	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			frm.add_custom_button(__('Purchase Order'), function() {
				frappe.model.open_mapped_doc({
					method: "alqlab_customization.alqlab.doctype.material_order.material_order.make_purchase_order",
					frm: frm,
				});
			}, __('Create'))
			frm.add_custom_button(__('Supplier Quotation'), function() {
				frappe.model.open_mapped_doc({
					method: "alqlab_customization.alqlab.doctype.material_order.material_order.make_supplier_quotation",
					frm: frm
				})
			}, __('Create'))
		}
	}
});
