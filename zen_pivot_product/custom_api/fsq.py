import frappe
import html2text


@frappe.whitelist()
def get_fsq_suppport(user_name):
    try:
        fsq_support_list = []
        get_fsq = frappe.db.get_all("Frequent Support Questions",{"disabled":0},["*"],order_by='idx ASC')
        for fsq in get_fsq:
            customer_group = frappe.db.get_value("Customer", {"custom_user": user_name}, "customer_group")
            if customer_group == fsq.customer_group:
                fsq_support = {
                    "id":fsq.name,
                    "name":fsq.name,
                    "customer_group":fsq.customer_group,
                    "fsq_question":fsq.fsq,
                    "fsq_description":html2text.html2text(fsq.description or "").strip()
                }
                fsq_support_list.append(fsq_support)
            else:
                fsq_support_list = []    
        return {"status":True,"fsq_support":fsq_support_list}        
    except Exception as e:
        return {"status":False,"message":e}