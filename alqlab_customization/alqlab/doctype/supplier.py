import frappe,json
from erpnext.selling.doctype.customer.customer import make_contact,make_address

@frappe.whitelist()
def create_address_and_contact(doc,method):
	create_contact(doc)
	create_address(doc)

def create_contact(doc):
	if doc.get('mobile_no') or doc.get('email_id'):
		make_contact(doc)


def create_address(doc):
	if doc.get('address_line1'):
		make_address(doc)
