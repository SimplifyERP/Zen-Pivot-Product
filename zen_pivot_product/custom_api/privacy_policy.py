import frappe 

@frappe.whitelist()
def get_privacy_policy():
    try:
        privacy_policy =  frappe.db.get_single_value("Privacy Policy","privacy_policy_details") or ""
        # terms_of_use = frappe.db.get_single_value("Privacy Policy","terms_of_use") or ""
        return {"status":True,"privacy_policy":privacy_policy}
    except Exception as e:
        return {"status":False,"message":e}