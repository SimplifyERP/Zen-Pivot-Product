import frappe
import json
from frappe.utils import now, getdate, today, format_date,format_time


@frappe.whitelist()
def get_notification_details():
    try:
        notification_details_list = []
        get_notification = frappe.get_doc("Product Notification Settings","notification_table")
        notificaion_table = frappe.db.get_all("Product Notification Settings Table",{'parent':get_notification.name},["notification_type","description"],order_by='idx ASC')
        for notification in notificaion_table:
            notification_details = {
                "notification_type":notification.notification_type,
                "description":notification.description,
                "notification_enable":False
            }
            notification_details_list.append(notification_details)
        return {"status":True,"notification_details":notification_details_list}
    except Exception as e:
        return {"status":False,"message":e}
    

@frappe.whitelist()
def get_user_notifications(user_name):
    try:
        notification_log_list = []
        notification_logs = frappe.db.get_all("Notification Log",{"for_user":user_name},["*"],order_by='idx ASC')
        for notification in notification_logs:
            email_content = notification.email_content
            try:
                cleaned_string = json.loads(email_content)
            except json.JSONDecodeError:
                cleaned_string = email_content

            cleaned_string = cleaned_string.strip('"')
            notification = {
                "id":notification.name,
                "name":notification.name,
                "service_name":notification.subject,
                "service_message":cleaned_string,
                "notification_time":notification.creation.strftime("%I:%M %p"),
                "notification_date":format_date(notification.creation)
                
            }
            notification_log_list.append(notification)
        return {"status":True,"message":notification_log_list}
    except Exception as e:
        return {"status":False,"message":e}
