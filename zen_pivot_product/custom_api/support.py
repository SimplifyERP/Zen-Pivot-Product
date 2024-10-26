import frappe
import base64
import json
import html2text


@frappe.whitelist()
def create_support_ticket(user_name,ticket_type,message,upload_file):
    try:
        new_support_ticket = frappe.new_doc("HD Ticket")
        new_support_ticket.subject = "Customer Support"
        new_support_ticket.raised_by = user_name
        new_support_ticket.ticket_type = ticket_type
        new_support_ticket.description = message
        new_support_ticket.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("HD Ticket",new_support_ticket.name,'owner',user_name)

        new_notification_log = frappe.new_doc("Notification Log")
        new_notification_log.subject = "Support Ticket"
        new_notification_log.type = "Alert"
        new_notification_log.for_user = user_name
        new_notification_log.email_content = "Your Support Ticket {} for was Created".format(ticket_type)
        new_notification_log.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Notification Log",new_notification_log.name,'owner',user_name)

        decode_json_doc = json.loads(upload_file)
        if not decode_json_doc == []:
            for file in decode_json_doc:
                convert_image_base64 = base64.b64decode(file.get("file"))
                file_name_inside = file.get("file_name")
                new_file_inside = frappe.new_doc('File')
                new_file_inside.file_name = file_name_inside
                new_file_inside.file_type = file.get("file_type")
                new_file_inside.content = convert_image_base64
                new_file_inside.attached_to_doctype = "HD Ticket"
                new_file_inside.attached_to_name = new_support_ticket.name
                new_file_inside.is_private = 0
                new_file_inside.save(ignore_permissions=True)
                frappe.db.commit()
        return {"status":True,"message":"Support Created"}
    except Exception as e:
        return {"status":False,"message":e}
    
@frappe.whitelist()
def get_support_ticket(user_name):
    try:
        support_ticket_list = []
        support_ticket = frappe.db.get_all("HD Ticket",{"raised_by":user_name},["*"],order_by='idx ASC')
        for support in support_ticket:
            ticket = {
                "id":support.name,
                "name":support.name,
                "subject":support.subject,
                "ticket_status":support.status,
                "ticket_type":support.ticket_type,
                "description":html2text.html2text(support.description or "").strip()
                }
            support_ticket_list.append(ticket)
        return {"status":True,"support_ticket":support_ticket_list}    
    except Exception as e:
        return {"status":False,"message":e}