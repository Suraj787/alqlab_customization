// Copyright (c) 2021, bizmap technologies,pune and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request For Payment', {
	get_invoices: function(frm) {
			const today = frappe.datetime.get_today();
			const fields = [
				{fieldtype:"Date", label: __("From Date"),
					fieldname:"from_posting_date", default:frappe.datetime.add_days(today, -30)},
				{fieldtype:"Column Break"},
				{fieldtype:"Date", label: __("To Date"), fieldname:"to_posting_date", default:today},
				{fieldtype:"Section Break", label: __("Supplier")},
				{fieldtype:"Link", label: __("Supplier"), fieldname:"supplier",options:"Supplier"}
				];
	
			frappe.prompt(fields, function(filters){
				frappe.flags.allocate_payment_amount = true;
				frm.events.get_invoice_documents(frm, filters);
			}, __("Filters"), __("Get Invoices"));
		},

		
		get_invoice_documents: function(frm, filters) {
			frm.clear_table("purchase_invoice_table");
	
			
			var args = {
				"from_posting_date": frm.doc.from_posting_date,
				"supplier": frm.doc.supplier,
				"to_posting_date":frm.doc.to_posting_date
			}
	
			for (let key in filters) {
				args[key] = filters[key];
			}
			
			return  frappe.call({ 
				method:"alqlab_customization.alqlab.doctype.request_for_payment.request_for_payment.get_outstanding_reference_documents", 
				
				args: {
					args:args
				},
				callback: function(r, rt) {
					if(r.message) {
					

					var iqd_total = 0;
					var usd_total = 0;
	
						$.each(r.message, function(i, d) {
							var c = frm.add_child("purchase_invoice_table");
							c.purchase_invoice = d.purchase_invoice;
							c.posting_date = d.posting_date;
							c.supplier = d.supplier
							c.project = d.project;
							c.currency = d.currency;
							c.grand_total = d.grand_total
							console.log(d.grand_total);
							if (d.currency == 'IQD'){
								iqd_total = iqd_total + d.grand_total;

							}
							if(d.currency == 'USD'){
								usd_total = iqd_total + d.grand_total;


												}
							

						});
						frm.set_value("iqd_total",iqd_total);
						frm.set_value("usd_total",usd_total);
						frm.refresh_field("purchase_invoice_table");
					
						
					}
	
					
	
				}
			});
		},
		validate: function(frm){
			
			var iqd_total = 0;
			var usd_total = 0;

		var table = frm.doc.purchase_invoice_table;
		table.forEach(d => {
			if (d.currency == 'IQD'){
				iqd_total = parseFloat(iqd_total) + parseFloat(d.grand_total);
				}
			if(d.currency == 'USD'){
				usd_total = parseFloat(usd_total) + parseFloat(d.grand_total);
				
				}
			})
		
			frm.set_value("iqd_total",iqd_total);
			frm.set_value("usd_total",usd_total);
	}
	});
