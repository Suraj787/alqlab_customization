# from __future__ import unicode_literals
# import frappe
# import json
# from frappe import _
# from frappe.model.document import Document
# from frappe import _, scrub, ValidationError
# from frappe.utils import flt, nowdate, get_url
# from erpnext.accounts.party import get_party_account, get_party_bank_account
# from erpnext.accounts.utils import get_account_currency
# from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry, get_company_defaults
# from frappe.integrations.utils import get_payment_gateway_controller
# from frappe.utils.background_jobs import enqueue
# from erpnext.erpnext_integrations.stripe_integration import create_stripe_subscription
# from erpnext.accounts.doctype.subscription_plan.subscription_plan import get_plan_rate
# from erpnext.controllers.accounts_controller import AccountsController, get_supplier_block_status
# from erpnext.accounts.utils import get_outstanding_invoices, get_account_currency, get_balance_on
# from six import string_types, iteritems
							

# @frappe.whitelist()
# def get_outstanding_reference_documents(args):

# 	if isinstance(args, string_types):
# 		args = json.loads(args)

# 	if args.get('party_type') == 'Member':
# 		return

# 	# confirm that Supplier is not blocked
# 	if args.get('party_type') == 'Supplier':
# 		supplier_status = get_supplier_block_status(args['party'])
# 		if supplier_status['on_hold']:
# 			if supplier_status['hold_type'] == 'All':
# 				return []
# 			elif supplier_status['hold_type'] == 'Payments':
# 				if not supplier_status['release_date'] or getdate(nowdate()) <= supplier_status['release_date']:
# 					return []

# 	party_account_currency = get_account_currency(args.get("party_account"))
# 	company_currency = frappe.get_cached_value('Company',  args.get("company"),  "default_currency")

# 	# Get negative outstanding sales /purchase invoices
# 	negative_outstanding_invoices = []
# 	if args.get("party_type") not in ["Student", "Employee"] and not args.get("voucher_no"):
# 		negative_outstanding_invoices = get_negative_outstanding_invoices(args.get("party_type"), args.get("party"),
# 			args.get("party_account"), args.get("company"), party_account_currency, company_currency)


# 	# Get positive outstanding sales /purchase invoices/ Fees
# 	condition = ""
# 	if args.get("voucher_type") and args.get("voucher_no"):
# 		condition = " and voucher_type={0} and voucher_no={1}".format(frappe.db.escape(args["voucher_type"]), frappe.db.escape(args["voucher_no"]))

# 	# Add cost center condition
# 	if args.get("cost_center"):
# 		condition += " and cost_center='%s'" % args.get("cost_center")

# 	date_fields_dict = {
# 		'posting_date': ['from_posting_date', 'to_posting_date'],
# 		'due_date': ['from_due_date', 'to_due_date']
# 	}

# 	for fieldname, date_fields in date_fields_dict.items():
# 		if args.get(date_fields[0]) and args.get(date_fields[1]):
# 			condition += " and {0} between '{1}' and '{2}'".format(fieldname,
# 				args.get(date_fields[0]), args.get(date_fields[1]))

# 	if args.get("company"):
# 		condition += " and company = {0}".format(frappe.db.escape(args.get("company")))
# 	# print(args.get("party_type"), args.get("party"),args.get("party_account"),'###',args,'$$',condition)
# 	outstanding_invoices = get_outstanding_invoices(args.get("party_type"), args.get("party"),
# 		args.get("party_account"), filters=args, condition=condition)

# 	for d in outstanding_invoices:
# 		d["exchange_rate"] = 1
# 		if party_account_currency != company_currency:
# 			if d.voucher_type in ("Sales Invoice", "Purchase Invoice", "Expense Claim"):
# 				d["exchange_rate"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "conversion_rate")
# 			elif d.voucher_targsype == "Journal Entry":
# 				d["exchange_rate"] = get_exchange_rate(
# 					party_account_currency,	company_currency, d.posting_date
# 				)
# 		if d.voucher_type in ("Purchase Invoice"):
# 			d["bill_no"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "bill_no")

# 	# Get all SO / PO which are not fully billed or aginst which full advance not paid
# 	orders_to_be_billed = []
# 	if (args.get("party_type") != "Student"):
# 		orders_to_be_billed =  get_orders_to_be_billed(args.get("posting_date"),args.get("party_type"),
# 			args.get("party"), args.get("company"), party_account_currency, company_currency, filters=args)
# 	# print(outstanding_invoices)
# 	data = negative_outstanding_invoices + outstanding_invoices + orders_to_be_billed
	
# 	if not data:
# 		frappe.msgprint(_("No outstanding invoices found for the {0} {1} which qualify the filters you have specified.")
# 			.format(args.get("party_type").lower(), frappe.bold(args.get("party"))))
	
# 	new_data=[]
# 	project=frappe.db.get_value(args.get('ref_doctype'),args.get('ref_docname'),'project')
# 	cost_center=frappe.db.get_value(args.get('ref_doctype'),args.get('ref_docname'),'cost_center')	
# 	for d in data:
# 		d.update({'project':'','cost_center':''})
# 		if project:
# 			d.update({'project':project})
# 		# new_data.append(d)	
# 		if cost_center:
# 			d.update({'cost_center':cost_center})	
# 		new_data.append(d)
# 	return new_data
	

# def get_orders_to_be_billed(posting_date, party_type, party,
# 	company, party_account_currency, company_currency, cost_center=None, filters=None):
# 	if party_type == "Customer":
# 		voucher_type = 'Sales Order'
# 	elif party_type == "Supplier":
# 		voucher_type = 'Purchase Order'
# 	elif party_type == "Employee":
# 		voucher_type = None

# 	# Add cost center condition
# 	if voucher_type:
# 		doc = frappe.get_doc({"doctype": voucher_type})
# 		condition = ""
# 		if doc and hasattr(doc, 'cost_center'):
# 			condition = " and cost_center='%s'" % cost_center

# 	orders = []
# 	if voucher_type:
# 		if party_account_currency == company_currency:
# 			grand_total_field = "base_grand_total"
# 			rounded_total_field = "base_rounded_total"
# 		else:
# 			grand_total_field = "grand_total"
# 			rounded_total_field = "rounded_total"

# 		orders = frappe.db.sql("""
# 			select
# 				name as voucher_no,
# 				if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) as invoice_amount,
# 				(if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) - advance_paid) as outstanding_amount,
# 				transaction_date as posting_date
# 			from
# 				`tab{voucher_type}`
# 			where
# 				{party_type} = %s
# 				and docstatus = 1
# 				and company = %s
# 				and ifnull(status, "") != "Closed"
# 				and if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) > advance_paid
# 				and abs(100 - per_billed) > 0.01
# 				{condition}
# 			order by
# 				transaction_date, name
# 		""".format(**{
# 			"rounded_total_field": rounded_total_field,
# 			"grand_total_field": grand_total_field,
# 			"voucher_type": voucher_type,
# 			"party_type": scrub(party_type),
# 			"condition": condition
# 		}), (party, company), as_dict=True)

# 	order_list = []
# 	for d in orders:
# 		if not (flt(d.outstanding_amount) >= flt(filters.get("outstanding_amt_greater_than"))
# 			and flt(d.outstanding_amount) <= flt(filters.get("outstanding_amt_less_than"))):
# 			continue

# 		d["voucher_type"] = voucher_type
# 		# This assumes that the exchange rate required is the one in the SO
# 		d["exchange_rate"] = get_exchange_rate(party_account_currency, company_currency, posting_date)
# 		order_list.append(d)

# 	return order_list

# def get_negative_outstanding_invoices(party_type, party, party_account,
# 	company, party_account_currency, company_currency, cost_center=None):
# 	voucher_type = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"
# 	supplier_condition = ""
# 	if voucher_type == "Purchase Invoice":
# 		supplier_condition = "and (release_date is null or release_date <= CURDATE())"
# 	if party_account_currency == company_currency:
# 		grand_total_field = "base_grand_total"
# 		rounded_total_field = "base_rounded_total"
# 	else:
# 		grand_total_field = "grand_total"
# 		rounded_total_field = "rounded_total"

# 	return frappe.db.sql("""
# 		select
# 			"{voucher_type}" as voucher_type, name as voucher_no,
# 			if({rounded_total_field}, {rounded_total_field}, {grand_total_field}) as invoice_amount,
# 			outstanding_amount, posting_date,
# 			due_date, conversion_rate as exchange_rate
# 		from
# 			`tab{voucher_type}`
# 		where
# 			{party_type} = %s and {party_account} = %s and docstatus = 1 and
# 			company = %s and outstanding_amount < 0
# 			{supplier_condition}
# 		order by
# 			posting_date, name
# 		""".format(**{
# 			"supplier_condition": supplier_condition,
# 			"rounded_total_field": rounded_total_field,
# 			"grand_total_field": grand_total_field,
# 			"voucher_type": voucher_type,
# 			"party_type": scrub(party_type),
# 			"party_account": "debit_to" if party_type == "Customer" else "credit_to",
# 			"cost_center": cost_center
# 		}), (party, party_account, company), as_dict=True)


# @frappe.whitelist()
# def get_party_details(company, party_type, party, date, cost_center=None):
# 	bank_account = ''
# 	if not frappe.db.exists(party_type, party):
# 		frappe.throw(_("Invalid {0}: {1}").format(party_type, party))

# 	party_account = get_party_account(party_type, party, company)

# 	account_currency = get_account_currency(party_account)
# 	account_balance = get_balance_on(party_account, date, cost_center=cost_center)
# 	_party_name = "title" if party_type in ("Student", "Shareholder") else party_type.lower() + "_name"
# 	party_name = frappe.db.get_value(party_type, party, _party_name)
# 	party_balance = get_balance_on(party_type=party_type, party=party, cost_center=cost_center)
# 	if party_type in ["Customer", "Supplier"]:
# 		bank_account = get_party_bank_account(party_type, party)

# 	return {
# 		"party_account": party_account,
# 		"party_name": party_name,
# 		"party_account_currency": account_currency,
# 		"party_balance": party_balance,
# 		"account_balance": account_balance,
# 		"bank_account": bank_account
# 	}


# @frappe.whitelist()
# def get_account_details(account, date, cost_center=None):
# 	frappe.has_permission('Payment Entry', throw=True)

# 	# to check if the passed account is accessible under reference doctype Payment Entry
# 	account_list = frappe.get_list('Account', {
# 		'name': account
# 	}, reference_doctype='Payment Entry', limit=1)

# 	# There might be some user permissions which will allow account under certain doctypes
# 	# except for Payment Entry, only in such case we should throw permission error
# 	if not account_list:
# 		frappe.throw(_('Account: {0} is not permitted under Payment Entry').format(account))

# 	account_balance = get_balance_on(account, date, cost_center=cost_center,
# 		ignore_account_permission=True)

# 	return frappe._dict({
# 		"account_currency": get_account_currency(account),
# 		"account_balance": account_balance,
# 		"account_type": frappe.db.get_value("Account", account, "account_type")
# 	})


# @frappe.whitelist()
# def get_company_defaults(company):
# 	fields = ["write_off_account", "exchange_gain_loss_account", "cost_center"]
# 	ret = frappe.get_cached_value('Company',  company,  fields, as_dict=1)

# 	for fieldname in fields:
# 		if not ret[fieldname]:
# 			frappe.throw(_("Please set default {0} in Company {1}").format(frappe.get_meta("Company").get_label(fieldname), company))

# 	return ret


# def get_outstanding_on_journal_entry(name):
# 	res = frappe.db.sql(
# 			'SELECT '
# 			'CASE WHEN party_type IN ("Customer", "Student") '
# 			'THEN ifnull(sum(debit_in_account_currency - credit_in_account_currency), 0) '
# 			'ELSE ifnull(sum(credit_in_account_currency - debit_in_account_currency), 0) '
# 			'END as outstanding_amount '
# 			'FROM `tabGL Entry` WHERE (voucher_no=%s OR against_voucher=%s) '
# 			'AND party_type IS NOT NULL '
# 			'AND party_type != ""',
# 			(name, name), as_dict=1
# 		)

# 	outstanding_amount = res[0].get('outstanding_amount', 0) if res else 0
	

# 	return outstanding_amount


# @frappe.whitelist()
# def get_reference_details(reference_doctype, reference_name, party_account_currency):
# 	total_amount = outstanding_amount = exchange_rate = bill_no = None
# 	ref_doc = frappe.get_doc(reference_doctype, reference_name)
# 	company_currency = ref_doc.get("company_currency") or erpnext.get_company_currency(ref_doc.company)
	
# 	if reference_doctype == "Fees":
# 		total_amount = ref_doc.get("grand_total")
# 		exchange_rate = 1
# 		outstanding_amount = ref_doc.get("outstanding_amount")
# 	elif reference_doctype == "Journal Entry" and ref_doc.docstatus == 1:
# 		total_amount = ref_doc.get("total_amount")
# 		if ref_doc.multi_currency:
# 			exchange_rate = get_exchange_rate(party_account_currency, company_currency, ref_doc.posting_date)
# 		else:
# 			exchange_rate = 1
# 			outstanding_amount = get_outstanding_on_journal_entry(reference_name)
# 	elif reference_doctype != "Journal Entry":
# 		if party_account_currency == company_currency:
# 			if ref_doc.doctype == "Expense Claim":
# 				total_amount = ref_doc.total_sanctioned_amount
# 			elif ref_doc.doctype == "Employee Advance":
# 				total_amount = ref_doc.advance_amount
# 			else:
# 				total_amount = ref_doc.base_grand_total
# 			exchange_rate = 1
# 		else:
# 			total_amount = ref_doc.grand_total

# 			# Get the exchange rate from the original ref doc
# 			# or get it based on the posting date of the ref doc
# 			exchange_rate = ref_doc.get("conversion_rate") or \
# 				get_exchange_rate(party_account_currency, company_currency, ref_doc.posting_date)

# 		if reference_doctype in ("Sales Invoice", "Purchase Invoice"):
# 			outstanding_amount = ref_doc.get("outstanding_amount")
# 			bill_no = ref_doc.get("bill_no")
# 		elif reference_doctype == "Expense Claim":
# 			outstanding_amount = flt(ref_doc.get("total_sanctioned_amount")) \
# 				- flt(ref_doc.get("total_amount+reimbursed")) - flt(ref_doc.get("total_advance_amount"))
# 		elif reference_doctype == "Employee Advance":
# 			outstanding_amount = ref_doc.advance_amount - flt(ref_doc.paid_amount)
# 		else:
# 			outstanding_amount = flt(total_amount) - flt(ref_doc.advance_paid)
# 	else:
# 		# Get the exchange rate based on the posting date of the ref doc
# 		exchange_rate = get_exchange_rate(party_account_currency,
# 			company_currency, ref_doc.posting_date)

# 	return frappe._dict({
# 		"due_date": ref_doc.get("due_date"),
# 		"total_amount": total_amount,
# 		"outstanding_amount": outstanding_amount,
# 		"exchange_rate": exchange_rate,
# 		"bill_no": bill_no
# 	})


# @frappe.whitelist()
# def get_party_and_account_balance(company, date, paid_from=None, paid_to=None, ptype=None, pty=None, cost_center=None):
# 	return frappe._dict({
# 		"party_balance": get_balance_on(party_type=ptype, party=pty, cost_center=cost_center),
# 		"paid_from_account_balance": get_balance_on(paid_from, date, cost_center=cost_center),
# 		"paid_to_account_balance": get_balance_on(paid_to, date=date, cost_center=cost_center)
# 	})
