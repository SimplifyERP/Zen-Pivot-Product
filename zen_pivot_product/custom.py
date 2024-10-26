import frappe
from urllib.parse import quote,urlparse
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry



def get_domain_name():
    site = frappe.get_site_path()
    if site == "./erp.deck.ai" :
        url = "http://127.0.0.1:8010"
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc
        return f"http://{domain_name}"
    elif site == "./core.zenpivot.in":
        url = "https://core.zenpivot.in/"
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc
        return f"https://{domain_name}"
    

@frappe.whitelist()
def create_payment_entry(doc,method):
    get_user = frappe.db.get_value("Customer",{"name":doc.customer},["custom_user"])
    if doc.custom_product_payment:
        dt = "Sales Invoice"
        dn = doc.name
        new_payment_entry = get_payment_entry(dt,dn)
        new_payment_entry.flags.ignore_mandatory = True
        new_payment_entry.posting_date = frappe.utils.nowdate()
        new_payment_entry.mode_of_payment = "Online Payment"
        new_payment_entry.payment_type = "Receive"
        new_payment_entry.party_type = "Customer"
        new_payment_entry.party = doc.customer
        new_payment_entry.paid_amount = doc.grand_total
        new_payment_entry.reference_no = doc.custom_product_payment
        new_payment_entry.received_amount = doc.grand_total
        new_payment_entry.target_exchange_rate = 1
        new_payment_entry.paid_from = "Debtors - ZP"
        new_payment_entry.paid_to = "Bank Account - ZP"
        new_payment_entry.reference_date = frappe.utils.nowdate()
        new_payment_entry.save(ignore_permissions=True)
        new_payment_entry.submit()
        frappe.db.commit()
        frappe.db.set_value("Payment Entry",new_payment_entry.name,'owner',get_user)
        frappe.db.set_value("Sales Invoice",doc.name,"status","Paid")
    elif doc.custom_my_services:
        dt = "Sales Invoice"
        dn = doc.name
        new_payment_entry = get_payment_entry(dt,dn)
        new_payment_entry.flags.ignore_mandatory = True
        new_payment_entry.posting_date = frappe.utils.nowdate()
        new_payment_entry.mode_of_payment = "Online Payment"
        new_payment_entry.payment_type = "Receive"
        new_payment_entry.party_type = "Customer"
        new_payment_entry.party = doc.customer
        new_payment_entry.paid_amount = doc.grand_total
        new_payment_entry.reference_no = doc.custom_my_services
        new_payment_entry.received_amount = doc.grand_total
        new_payment_entry.target_exchange_rate = 1
        new_payment_entry.paid_from = "Debtors - ZP"
        new_payment_entry.paid_to = "Bank Account - ZP"
        new_payment_entry.reference_date = frappe.utils.nowdate()
        new_payment_entry.save(ignore_permissions=True)
        new_payment_entry.submit()
        frappe.db.commit()
        frappe.db.set_value("Payment Entry",new_payment_entry.name,'owner',get_user)
        frappe.db.set_value("Sales Invoice",doc.name,"status","Paid")