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

import urllib.request
import urllib.parse
  
import urllib.request
import urllib.parse
 
def getSurveys(apikey):
	data =  urllib.parse.urlencode({'apikey': apikey})
	data = data.encode('utf-8')
	request = urllib.request.Request("https://api.txtlocal.com/get_surveys/?")
	f = urllib.request.urlopen(request, data)
	fr = f.read()
	return(fr)
 

  
def execute():
	resp =  getSurveys('fq6I2ME8dXk-pn649Qk77fvlGV3nGwBYdzRVCmtohy')
	print (resp)
# 	resp= sendSMS('fq6I2ME8dXk-0Hq5bQ1DdtTJZSlF0AkzbHtwqfMEIy', 7709933728,
# 		'Jims Autos', 'Test with an ampersand (&) and a £5 note')
# 	print (resp)