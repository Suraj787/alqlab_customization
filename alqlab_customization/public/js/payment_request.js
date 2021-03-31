frappe.ui.form.on("Payment Request",{
    get_outstanding_invoice: function(frm) {
		const today = frappe.datetime.get_today();
		const fields = [
			{fieldtype:"Section Break", label: __("Posting Date")},
			{fieldtype:"Date", label: __("From Date"),
				fieldname:"from_posting_date", default:frappe.datetime.add_days(today, -30)},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_posting_date", default:today},
			{fieldtype:"Section Break", label: __("Due Date")},
			{fieldtype:"Date", label: __("From Date"), fieldname:"from_due_date"},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_due_date"},
			{fieldtype:"Section Break", label: __("Outstanding Amount")},
			{fieldtype:"Float", label: __("Greater Than Amount"),
				fieldname:"outstanding_amt_greater_than", default: 0},
			{fieldtype:"Column Break"},
			{fieldtype:"Float", label: __("Less Than Amount"), fieldname:"outstanding_amt_less_than"},
			{fieldtype:"Section Break"},
			{fieldtype:"Check", label: __("Allocate Payment Amount"), fieldname:"allocate_payment_amount", default:1},
		];

		frappe.prompt(fields, function(filters){
			frappe.flags.allocate_payment_amount = true;
			frm.events.validate_filters_data(frm, filters);
			frm.events.get_outstanding_documents(frm, filters);
		}, __("Filters"), __("Get Outstanding Documents"));
	},

	validate_filters_data:function(frm, filters){
		const fields = {
			'Posting Date': ['from_posting_date', 'to_posting_date'],
			'Due Date': ['from_posting_date', 'to_posting_date'],
			'Advance Amount': ['from_posting_date', 'to_posting_date'],
		};

		for (let key in fields) {
			let from_field = fields[key][0];
			let to_field = fields[key][1];

			if (filters[from_field] && !filters[to_field]) {
				frappe.throw(__("Error: {0} is mandatory field",[to_field.replace(/_/g, " ")]));
			} 
			else if (filters[from_field] && filters[from_field] > filters[to_field]) {
				frappe.throw(__("{0}: {1} must be less than {2}",[key, from_field.replace(/_/g, " "), to_field.replace(/_/g, " ")]));
			}
		}
	},

	get_outstanding_documents: function(frm, filters) {
		frm.clear_table("references");

		if(!frm.doc.party) {
			return;
		}

		frm.events.check_mandatory_to_fetch(frm);
		var company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;

		var args = {
			"posting_date": frm.doc.posting_date,
			"company": frm.doc.company,
			"party_type": frm.doc.party_type,
			"payment_type": frm.doc.payment_type,
			"party": frm.doc.party,
			"party_account": frm.doc.payment_type=="Receive" ? frm.doc.paid_from : frm.doc.paid_to,
			"cost_center": frm.doc.cost_center,
			"ref_doctype": frm.doc.reference_doctype,
			"ref_docname":frm.doc.reference_name
		}

		for (let key in filters) {
			args[key] = filters[key];
		}

		frappe.flags.allocate_payment_amount = filters['allocate_payment_amount'];

		return  frappe.call({ 
			method:"alqlab_customization.alqlab.doctype.payment_request.get_outstanding_reference_documents", 
            
			args: {
				args:args
			},
			callback: function(r, rt) {
				if(r.message) {
					var total_positive_outstanding = 0;
					var total_negative_outstanding = 0;

					$.each(r.message, function(i, d) {
						var c = frm.add_child("references");
						c.reference_doctype = d.voucher_type;
						c.reference_name = d.voucher_no;
						c.due_date = d.due_date
						c.total_amount = d.invoice_amount;
						c.outstanding_amount = d.outstanding_amount;
                        c.bill_no = d.bill_no;
                        c.project = d.project;
                        c.cost_center = d.cost_center;

						if(!in_list(["Sales Order", "Purchase Order", "Expense Claim", "Fees"], d.voucher_type)) {
							if(flt(d.outstanding_amount) > 0){
								total_positive_outstanding += flt(d.outstanding_amount);}
							else{
								total_negative_outstanding += Math.abs(flt(d.outstanding_amount)); }
						}

						var party_account_currency = frm.doc.payment_type=="Receive" ?
							frm.doc.paid_from_account_currency : frm.doc.paid_to_account_currency;

						if(party_account_currency != company_currency) {
							c.exchange_rate = d.exchange_rate;
						} else {
							c.exchange_rate = 1;
						}
						if (in_list(['Sales Invoice', 'Purchase Invoice', "Expense Claim", "Fees"], d.reference_doctype)){
							c.due_date = d.due_date;
						}
					});

					if(
						(frm.doc.payment_type=="Receive" && frm.doc.party_type=="Customer") ||
						(frm.doc.payment_type=="Pay" && frm.doc.party_type=="Supplier")  ||
						(frm.doc.payment_type=="Pay" && frm.doc.party_type=="Employee") ||
						(frm.doc.payment_type=="Receive" && frm.doc.party_type=="Student")
					) {
						if(total_positive_outstanding > total_negative_outstanding){
							if (!frm.doc.paid_amount){
								frm.set_value("paid_amount",total_positive_outstanding - total_negative_outstanding);
							}
						}		
					} 
					else if (total_negative_outstanding && total_positive_outstanding < total_negative_outstanding) {
						if (!frm.doc.received_amount){
							frm.set_value("received_amount", total_negative_outstanding - total_positive_outstanding);
						}
					}
				}

				frm.events.allocate_party_amount_against_ref_docs(frm,
					(frm.doc.payment_type=="Receive" ? frm.doc.paid_amount : frm.doc.received_amount));

			}
		});
	},
	check_mandatory_to_fetch: function(frm) {
		$.each(["Company", "Party Type", "Party", "payment_type"], function(i, field) {
			if(!frm.doc[frappe.model.scrub(field)]) {
				frappe.msgprint(__("Please select {0} first", [field]));
				return false;
			}

		});
	},
	allocate_party_amount_against_ref_docs: function(frm, paid_amount) {
		var total_positive_outstanding_including_order = 0;
		var total_negative_outstanding = 0;
		var total_deductions = frappe.utils.sum($.map(frm.doc.deductions || [],
			function(d) { return flt(d.amount) }));

		paid_amount -= total_deductions;

		$.each(frm.doc.references || [], function(i, row) {
			if(flt(row.outstanding_amount) > 0){
				total_positive_outstanding_including_order += flt(row.outstanding_amount); }
			else{
				total_negative_outstanding += Math.abs(flt(row.outstanding_amount)); }
		})

		var allocated_negative_outstanding = 0;
		if (
				(frm.doc.payment_type=="Receive" && frm.doc.party_type=="Customer") ||
				(frm.doc.payment_type=="Pay" && frm.doc.party_type=="Supplier") ||
				(frm.doc.payment_type=="Pay" && frm.doc.party_type=="Employee") ||
				(frm.doc.payment_type=="Receive" && frm.doc.party_type=="Student")
			) {
				if(total_positive_outstanding_including_order > paid_amount) {
					var remaining_outstanding = total_positive_outstanding_including_order - paid_amount;
					allocated_negative_outstanding = total_negative_outstanding < remaining_outstanding ?
						total_negative_outstanding : remaining_outstanding;
			}
		

			var allocated_positive_outstanding =  paid_amount + allocated_negative_outstanding;
		} else if (in_list(["Customer", "Supplier"], frm.doc.party_type)) {
			if(paid_amount > total_negative_outstanding) {
				if(total_negative_outstanding == 0) {
					frappe.msgprint(__("Cannot {0} {1} {2} without any negative outstanding invoice",
						[frm.doc.payment_type,
							(frm.doc.party_type=="Customer" ? "to" : "from"), frm.doc.party_type]));
					return false
				} else {
					frappe.msgprint(__("Paid Amount cannot be greater than total negative outstanding amount {0}", [total_negative_outstanding]));
					return false;
				}
			} else {
				allocated_positive_outstanding = total_negative_outstanding - paid_amount;
				allocated_negative_outstanding = paid_amount +
					(total_positive_outstanding_including_order < allocated_positive_outstanding ?
						total_positive_outstanding_including_order : allocated_positive_outstanding)
			}
		}

		$.each(frm.doc.payment_references || [], function(i, row) {
			row.allocated_amount = 0 //If allocate payment amount checkbox is unchecked, set zero to allocate amount
			if(frappe.flags.allocate_payment_amount != 0){
				if(row.outstanding_amount > 0 && allocated_positive_outstanding > 0) {
					if(row.outstanding_amount >= allocated_positive_outstanding) {
						row.allocated_amount = allocated_positive_outstanding;
					} else {
						row.allocated_amount = row.outstanding_amount;
					}

					allocated_positive_outstanding -= flt(row.allocated_amount);
				} else if (row.outstanding_amount < 0 && allocated_negative_outstanding) {
					if(Math.abs(row.outstanding_amount) >= allocated_negative_outstanding)
						row.allocated_amount = -1*allocated_negative_outstanding;
					else row.allocated_amount = row.outstanding_amount;

					allocated_negative_outstanding -= Math.abs(flt(row.allocated_amount));
				}
			}
		})

		frm.refresh_fields()
		frm.events.set_total_allocated_amount(frm);
	},
	set_total_allocated_amount: function(frm) {
		var total_allocated_amount = 0.0;
		var base_total_allocated_amount = 0.0;
		$.each(frm.doc.references || [], function(i, row) {
			if (row.allocated_amount) {
				total_allocated_amount += flt(row.allocated_amount);
				base_total_allocated_amount += flt(flt(row.allocated_amount)*flt(row.exchange_rate),
					precision("base_paid_amount"));
			}
		});
		frm.set_value("total_allocated_amount", Math.abs(total_allocated_amount));
		frm.set_value("base_total_allocated_amount", Math.abs(base_total_allocated_amount));

		frm.events.set_unallocated_amount(frm);
	},
	set_unallocated_amount: function(frm) {
		var unallocated_amount = 0;
		var total_deductions = frappe.utils.sum($.map(frm.doc.deductions || [],
			function(d) { return flt(d.amount) }));

		if(frm.doc.party) {
			if(frm.doc.payment_type == "Receive"
				&& frm.doc.base_total_allocated_amount < frm.doc.base_received_amount + total_deductions
				&& frm.doc.total_allocated_amount < frm.doc.paid_amount + (total_deductions / frm.doc.source_exchange_rate)) {
					unallocated_amount = (frm.doc.base_received_amount + total_deductions
						- frm.doc.base_total_allocated_amount) / frm.doc.source_exchange_rate;
			} else if (frm.doc.payment_type == "Pay"
				&& frm.doc.base_total_allocated_amount < frm.doc.base_paid_amount - total_deductions
				&& frm.doc.total_allocated_amount < frm.doc.received_amount + (total_deductions / frm.doc._target_exchange_rate)) {
					unallocated_amount = (frm.doc.base_paid_amount - (total_deductions
						+ frm.doc.base_total_allocated_amount)) / frm.doc._target_exchange_rate;
			}
		}
		frm.set_value("unallocated_amount", unallocated_amount);
		frm.trigger("set_difference_amount");
	},
	set_difference_amount: function(frm) {
		var difference_amount = 0;
		var base_unallocated_amount = flt(frm.doc.unallocated_amount) *
			(frm.doc.payment_type=="Receive" ? frm.doc.source_exchange_rate : frm.doc._target_exchange_rate);

		var base_party_amount = flt(frm.doc.base_total_allocated_amount) + base_unallocated_amount;

		if(frm.doc.payment_type == "Receive") {
			difference_amount = base_party_amount - flt(frm.doc.base_received_amount);
		} else if (frm.doc.payment_type == "Pay") {
			difference_amount = flt(frm.doc.base_paid_amount) - base_party_amount;
		} else {
			difference_amount = flt(frm.doc.base_paid_amount) - flt(frm.doc.base_received_amount);
		}

		var total_deductions = frappe.utils.sum($.map(frm.doc.deductions || [],
			function(d) { return flt(d.amount) }));

		frm.set_value("difference_amount", difference_amount - total_deductions);

		// frm.events.hide_unhide_fields(frm);
	},

	unallocated_amount: function(frm) {
		frm.trigger("set_difference_amount");
	},
	validate_reference_document: function(frm, row) {
		var _validate = function(i, row) {
			if (!row.reference_doctype) {
				return;
			}

			if(frm.doc.party_type=="Customer" &&
				!in_list(["Sales Order", "Sales Invoice", "Journal Entry"], row.reference_doctype)
			) {
				frappe.model.set_value(row.doctype, row.name, "reference_doctype", null);
				frappe.msgprint(__("Row #{0}: Reference Document Type must be one of Sales Order, Sales Invoice or Journal Entry", [row.idx]));
				return false;
			}

			if(frm.doc.party_type=="Supplier" &&
				!in_list(["Purchase Order", "Purchase Invoice", "Journal Entry"], row.reference_doctype)
			) {
				frappe.model.set_value(row.doctype, row.name, "against_voucher_type", null);
				frappe.msgprint(__("Row #{0}: Reference Document Type must be one of Purchase Order, Purchase Invoice or Journal Entry", [row.idx]));
				return false;
			}

			if(frm.doc.party_type=="Employee" &&
				!in_list(["Expense Claim", "Journal Entry"], row.reference_doctype)
			) {
				frappe.model.set_value(row.doctype, row.name, "against_voucher_type", null);
				frappe.msgprint(__("Row #{0}: Reference Document Type must be one of Expense Claim or Journal Entry", [row.idx]));
				return false;
			}
		}

		if (row) {
			_validate(0, row);
		} else {
			$.each(frm.doc.vouchers || [], _validate);
		}
	},


});


frappe.ui.form.on('Payment Request Reference', {
	reference_doctype: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frm.events.validate_reference_document(frm, row);
	},

	reference_name: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.reference_name && row.reference_doctype) {
			return frappe.call({
				method:'alqlab_customization.alqlab.doctype.payment_request.get_reference_details', 
                
				args: {
					reference_doctype: row.reference_doctype,
					reference_name: row.reference_name,
					party_account_currency: frm.doc.payment_type=="Receive" ?
						frm.doc.paid_from_account_currency : frm.doc.paid_to_account_currency
				},
				callback: function(r, rt) {
					if(r.message) {
						$.each(r.message, function(field, value) {
							frappe.model.set_value(cdt, cdn, field, value);
						})

						let allocated_amount = frm.doc.unallocated_amount > row.outstanding_amount ?
							row.outstanding_amount : frm.doc.unallocated_amount;

						frappe.model.set_value(cdt, cdn, 'allocated_amount', allocated_amount);
						frm.refresh_fields();
					}
				}
			})
		}
	},

	allocated_amount: function(frm) {
		frm.events.set_total_allocated_amount(frm);
	},

	references_remove: function(frm) {
		frm.events.set_total_allocated_amount(frm);
	}
	
})

frappe.ui.form.on('Payment Entry Deduction', {
	amount: function(frm) {
		frm.events.set_unallocated_amount(frm);
	},

	deductions_remove: function(frm) {
		frm.events.set_unallocated_amount(frm);
	}
})
frappe.ui.form.on('Payment Request', {
	cost_center: function(frm){
		if (frm.doc.posting_date && (frm.doc.paid_from||frm.doc.paid_to)) {
			return frappe.call({
				method:'alqlab_customization.alqlab.doctype.payment_request.get_party_and_account_balance', 

				args: {
					company: frm.doc.company,
					date: frm.doc.posting_date,
					paid_from: frm.doc.paid_from,
					paid_to: frm.doc.paid_to,
					ptype: frm.doc.party_type,
					pty: frm.doc.party,
					cost_center: frm.doc.cost_center
				},
				callback: function(r, rt) {
					if(r.message) {
						frappe.run_serially([
							() => {
								frm.set_value("paid_from_account_balance", r.message.paid_from_account_balance);
								frm.set_value("paid_to_account_balance", r.message.paid_to_account_balance);
								frm.set_value("party_balance", r.message.party_balance);
							},
							() => {
								if(frm.doc.payment_type != "Internal") {
									frm.clear_table("references");
								}
							}
						]);

					}
				}
			});
		}
	},
});


