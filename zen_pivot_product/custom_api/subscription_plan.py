import frappe
import html2text
from frappe.utils import now, getdate, today, format_date,format_time


#getting the subscription plan details and get the item description
@frappe.whitelist()
def subscription_plan_details(user_name):
    try:
        status = ""
        message = ""
        current_plan_purchase = False
        subscription_plan_list = []
        get_customer_group = frappe.db.get_value("Customer",{"custom_user":user_name},["customer_group"])
        if get_customer_group:
            get_subscription_plan = frappe.db.get_all("Product Subscription Plan",filters={"customer_group":get_customer_group},fields=["*"], order_by="idx ASC")
            for subscription in get_subscription_plan:
                last_payment = frappe.db.get_value('Product Payment',{"user":user_name},["plan_name"])
                if last_payment == subscription.name:
                    current_plan_purchase = True
                else:
                    current_plan_purchase = False 
                subscription_plan = {
                    "id":subscription.name,
                    "name":subscription.name,
                    "customer_group":subscription.customer_group,
                    "current_plan_purchase":current_plan_purchase,
                    "recommended_plan_status":False,
                    "plan_name":subscription.name,
                    "actual_plan_price":subscription.actual_plan_price,
                    "format_actual_plan_price":"{:,.0f}".format(subscription.actual_plan_price),
                    "offer_status":subscription.offer_price_status,
                    "offer_price":subscription.offer_price,
                    "format_offer_price":"{:,.0f}".format(subscription.offer_price),
                    "features":[]
                }
                get_features = frappe.db.get_all("Features Table",{'parent':subscription.name},["plan_features"],order_by='idx ASC')
                for feature in get_features:
                    subscription_plan["features"].append({
                        "plan_feature":feature.plan_features
                    })
                subscription_plan_list.append(subscription_plan)

                status = True
                message = "Subscription Plan"
        else:
            status = False
            message = "Customer not found"
        return {"status":status,"message":message,"subscription_plan_details":subscription_plan_list}            
    except Exception as e:
        return {"status":False,"message":e}
    

@frappe.whitelist()
def create_product_payment(user_name,plan_id,plan_amount,paid_amount,payment_id,payment_status):
    try:
        new_purchase = frappe.new_doc("Product Payment")
        new_purchase.user = user_name
        new_purchase.plan_name = plan_id
        new_purchase.plan_amount = plan_amount
        new_purchase.paid_amount = paid_amount
        new_purchase.payment_id = payment_id
        new_purchase.payment_status = payment_status
        new_purchase.save(ignore_permissions=True)
        new_purchase.submit()
        frappe.db.commit()
        frappe.db.set_value("Product Payment",new_purchase.name,'owner',user_name)

        new_notification_log = frappe.new_doc("Notification Log")
        new_notification_log.subject = "Subscription"
        new_notification_log.type = "Alert"
        new_notification_log.for_user = user_name
        new_notification_log.email_content = "Your Subscription {} for was Created".format(new_purchase.plan_name)
        new_notification_log.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Notification Log",new_notification_log.name,'owner',user_name)

        get_invoice = frappe.db.get_value("Sales Invoice",{"custom_product_payment":new_purchase.name},["name"])
        invoice = {
            "id":new_purchase.name,
            "name":new_purchase.name,
            "invoice_url":""
        }
        return {"status":True,"message":"Payment Created","invoice":invoice}        
    except Exception as e:
        return {"status":False,"message":e}
 

@frappe.whitelist()
def get_payment_details(user_name):
    try:
        payment_details = {
            "current_plan":get_current_plan(user_name),
            "all_payments":get_all_payments(user_name),
            "success_payment":get_success_payments(user_name),
            "failed_payment":get_failed_payments(user_name)
        }
        return {"status":True,"subscription_payment_details":payment_details}     
    except Exception as e:
        return {"status":False,"message":e}

def get_current_plan(user_name):
    try:
        current_plan = frappe.db.get_value('Product Payment',{"user":user_name},["name"])
        current_plan_data = frappe.get_doc("Product Payment",current_plan)
        get_plan_details = frappe.get_doc("Product Subscription Plan",current_plan_data.plan_name)
        subscription_plan = {
            "id":current_plan_data.name,
            "name":current_plan_data.name,
            "customer_group":get_plan_details.customer_group,
            "current_plan_purchase":True,
            "recommended_plan_status":False,
            "plan_name":current_plan_data.name,
            "actual_plan_price":get_plan_details.actual_plan_price,
            "format_actual_plan_price":"{:,.0f}".format(get_plan_details.actual_plan_price),
            "offer_status":get_plan_details.offer_price_status,
            "offer_price":get_plan_details.offer_price,
            "format_offer_price":"{:,.0f}".format(get_plan_details.offer_price),
            "features":[]
        }
        get_features = frappe.db.get_all("Features Table",{'parent':get_plan_details.name},["plan_features"],order_by='idx ASC')
        for feature in get_features:
            subscription_plan["features"].append({
                "plan_feature":feature.plan_features
            })
        return subscription_plan
    except Exception as e:
        return e


def get_all_payments(user_name):
    try:
        get_payments = frappe.db.get_all("Product Payment",{"user":user_name,"docstatus":1},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":payments.name,
            "name":payments.name,
            "amount":payments.paid_amount,
            "pricing_format": "{:,.0f}".format(payments.paid_amount),
            "payment_status":payments.payment_status, 
            "time": payments.creation.strftime("%I:%M %p") ,
            "date":format_date(payments.plan_purchase_date),
            "plan_name":payments.plan_name
            }
            for payments in get_payments
        ]
        return crm_list
    except Exception as e:
        return e
    
def get_success_payments(user_name):
    try:
        get_payments = frappe.db.get_all("Product Payment",{"user":user_name,"docstatus":1,"payment_status":"Paid"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":payments.name,
            "name":payments.name,
            "amount":payments.paid_amount,
            "pricing_format": "{:,.0f}".format(payments.paid_amount),
            "payment_status": "Success", 
            "time": payments.creation.strftime("%I:%M %p") ,
            "date":format_date(payments.plan_purchase_date),
            "plan_name":payments.plan_name
            }
            for payments in get_payments
        ]
        return crm_list
    except Exception as e:
        return e

    
def get_failed_payments(user_name):
    try:
        get_payments = frappe.db.get_all("Product Payment",{"user":user_name,"docstatus":1,"payment_status":"Failed"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":payments.name,
            "name":payments.name,
            "amount":payments.paid_amount,
            "pricing_format": "{:,.0f}".format(payments.paid_amount),
            "payment_status": "Failed", 
            "time": payments.creation.strftime("%I:%M %p") ,
            "date":format_date(payments.plan_purchase_date),
            "plan_name":payments.plan_name
            }
            for payments in get_payments
        ]
        return crm_list
    except Exception as e:
        return e    