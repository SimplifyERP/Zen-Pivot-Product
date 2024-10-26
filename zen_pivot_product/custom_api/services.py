import frappe
import html2text
from deck_review.custom import get_domain_name
from datetime import datetime
from frappe.utils import now, getdate, today, format_date,format_time
import base64


@frappe.whitelist()
def get_our_services(user_name):
    try:
        status = ""
        message = ""
        service_list_append = []
        document_url = ""
        customer_group = frappe.db.get_value("Customer", {"custom_user": user_name}, "customer_group")
        if customer_group == "Entrepreneur":
            our_services = frappe.db.get_all(
                "Our Services",
                filters={"disabled": 0, "customer_group": customer_group},
                fields=["*"],
                order_by='idx ASC'
            )
            for service in our_services:
                service_list = {
                    "id": service.name,
                    "name": service.name or "",
                    "image_url": (get_domain_name() + service.service_image) if service.service_image else "",
                    "service_name": service.service_name,
                    "service_price": service.service_price,
                    "pricing_format": "{:,.0f}".format(service.service_price),
                    "customer_group": service.customer_group or "",
                    "description": html2text.html2text(service.description or "").strip(),
                    "our_service_documents":[]
                }
                our_service_documents = frappe.db.get_all("Our Services Documents",{'parent':service.name},["document_name","document_type","document"],order_by='idx ASC')
                for service_document in our_service_documents:
                    if service_document.document:
                        document_url = get_domain_name() + service_document.document
                    else:
                        document_url = ""    
                    service_list["our_service_documents"].append({
                        "document_name":service_document.document_name,
                        "document_type":service_document.document_type,
                        "document_url":document_url
                    })
                service_list_append.append(service_list)
                status = True
                message = "Service List"
        else:
            status = False
            message = "User is not Valid Customer group"        
        return {"status": status, "message": message, "our_services": service_list_append,"my_services":get_my_services_overall(user_name)}
    except Exception as e:
        return {"status": False, "message": str(e)}


def get_my_services_overall(user_name):
    try:
        my_services_list = []
        doc_upload_status = False
        process_status = False
        get_my_service = frappe.db.get_all("My Services",{"user":user_name},["*"],order_by='idx ASC')
        for service in get_my_service:
            get_service = frappe.get_doc("Our Services",service.our_services)
            get_sales_invoice = frappe.db.get_value("Sales Invoice",{"customer":service.full_name},["name"])
            get_invoice = frappe.db.get_value("File",{"attached_to_doctype":"Sales Invoice","attached_to_name":get_sales_invoice},["file_url"])
            if get_service.service_image:
                image_url = get_domain_name() + get_service.service_image
            else:
                image_url = ""   

            my_services = {
                "id":service.name,
                "name":service.name,
                "our_service_id":get_service.name,
                "service_image":image_url,
                "service_invoice":get_domain_name() + get_invoice or "",
                "service_name":get_service.service_name,
                "service_price":get_service.service_price,
                "pricing_format": "{:,.0f}".format(get_service.service_price),
                "customer_group": get_service.customer_group or "",
                "description": html2text.html2text(get_service.description or "").strip(), 
                "my_service_payment_status":service.payment_status,
                "my_service_payment_date":format_date(service.payment_date),
                "payment_invoice":"",
                "our_service_documents":[],
                "user_documents":[],
                "process_steps":[]
            }

            our_service_documents = frappe.db.get_all("Our Services Documents",{'parent':get_service.name},["*"],order_by='idx ASC')
            for service_document in our_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["our_service_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                })
            
            my_service_documents = frappe.db.get_all("My Service Documents",{'parent':service.name},["*"],order_by='idx ASC')
            for service_document in my_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["user_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                })

            process_steps = frappe.db.get_all("My Services Process Steps",{'parent':service.name},["*"],order_by='idx ASC')
            for process in process_steps:
                if process.status == "Completed":
                    process_status = True
                else:
                    process_status = False
                if process.doc_upload == 1:
                    doc_upload_status = True
                else:
                    doc_upload_status = False
                my_services["process_steps"].append({
                    "steps":process.steps,
                    "tat":process.tat,
                    "current_status":process.status,
                    "step_status":process_status,
					"doc_status":doc_upload_status
                })     
            my_services_list.append(my_services)
        return my_services_list   
    except Exception as e:
        return e


@frappe.whitelist()
def create_my_services(user_name,service_id,payment_transaction_id,amount):
    try:
        status = ""
        message = ""
        doc_upload_status = False
        process_status = False
        customer_group = frappe.db.get_value("Customer", {"custom_user": user_name}, "customer_group")
        if not customer_group:
            return {"status": False, "message": "Customer Not Created", "our_services": []}

        get_service = frappe.get_doc("Our Services",service_id)
        if get_service: 
            process_steps = frappe.db.get_all("Our Services Process Steps",{"parent":service_id},["steps","tat","status"],order_by='idx ASC')   
            new_my_services = frappe.new_doc("My Services")
            new_my_services.user = user_name
            new_my_services.our_services = service_id
            for process in process_steps:
                new_my_services.append("process_steps",{
                    "steps":process.steps,
                    "tat":process.tat,
                    "status":process.status,
                })
            new_my_services.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("My Services",new_my_services.name,'owner',user_name)


            my_service_payment = frappe.new_doc("My Service Payment")
            my_service_payment.user = user_name
            my_service_payment.payment_transaction_id = payment_transaction_id
            my_service_payment.payment_date = getdate(today())
            my_service_payment.payment_status = "Paid"
            my_service_payment.service_id = service_id
            my_service_payment.my_service_id = new_my_services.name
            my_service_payment.paid_amount = amount
            my_service_payment.save(ignore_permissions=True)
            my_service_payment.submit()
            frappe.db.commit()
            frappe.db.set_value("My Service Payment",my_service_payment.name,'owner',user_name)

            new_notification_log = frappe.new_doc("Notification Log")
            new_notification_log.subject = "My Services"
            new_notification_log.type = "Alert"
            new_notification_log.for_user = user_name
            new_notification_log.email_content = "Your Service {} for was Created".format(new_my_services.service_name)
            new_notification_log.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Notification Log",new_notification_log.name,'owner',user_name)

            get_my_services = frappe.get_doc("My Services",new_my_services.name)
            get_sales_invoice = frappe.db.get_value("Sales Invoice",{"customer":get_my_services.full_name},["name"])
            get_invoice = frappe.db.get_value("File",{"attached_to_doctype":"Sales Invoice","attached_to_name":get_sales_invoice},["file_url"])
            
            if get_service.service_image:
                image_url = get_domain_name() + get_service.service_image
            else:
                image_url = ""   

            my_services = {
                "id":get_my_services.name,
                "name":get_my_services.name,
                "our_service_id":get_service.name,
                "service_image":image_url,
                "service_invoice":get_domain_name() + get_invoice or "",
                "service_name":get_service.service_name,
                "service_price":get_service.service_price,
                "pricing_format": "{:,.0f}".format(get_service.service_price),
                "customer_group": get_service.customer_group or "",
                "description": html2text.html2text(get_service.description or "").strip(), 
                "my_service_payment_status":get_my_services.payment_status,
                "my_service_payment_date":format_date(get_my_services.payment_date),
                "payment_invoice":"",
                "our_service_documents":[],
                "user_documents":[],
                "process_steps":[]
            }

            our_service_documents = frappe.db.get_all("Our Services Documents",{'parent':get_service.name},["*"],order_by='idx ASC')
            for service_document in our_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["our_service_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                })
            
            my_service_documents = frappe.db.get_all("My Service Documents",{'parent':get_my_services.name},["*"],order_by='idx ASC')
            for service_document in my_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["user_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                }) 

            process_steps = frappe.db.get_all("My Services Process Steps",{'parent':get_my_services.name},["*"],order_by='idx ASC')
            for process in process_steps:
                if process.status == "Completed":
                    process_status = True
                else:
                    process_status = False
                if process.doc_upload == 1:
                    doc_upload_status = True
                else:
                    doc_upload_status = False
                my_services["process_steps"].append({
                    "steps":process.steps,
                    "tat":process.tat,
                    "current_status":process.status,
                    "step_status":process_status,
					"doc_status":doc_upload_status
                })       

            status = True
            message = "My Service Created"
        else:
            status = False
            message = "Service ID Not Found"

        return {"status":status,"message":message,"my_services":my_services}
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def get_my_service_single(my_service_id):
    try:
        status = ""
        message = ""
        doc_upload_status = False
        process_status = False
        get_my_service = frappe.get_doc("My Services",my_service_id)
        if get_my_service:
            get_service = frappe.get_doc("Our Services",get_my_service.our_services)
            get_sales_invoice = frappe.db.get_value("Sales Invoice",{"customer":get_my_service.full_name},["name"])
            get_invoice = frappe.db.get_value("File",{"attached_to_doctype":"Sales Invoice","attached_to_name":get_sales_invoice},["file_url"])
            if get_service.service_image:
                image_url = get_domain_name() + get_service.service_image
            else:
                image_url = ""   

            my_services = {
                "id":get_my_service.name,
                "name":get_my_service.name,
                "our_service_id":get_service.name,
                "service_image":image_url,
                "service_invoice":get_domain_name() + get_invoice or "",
                "service_name":get_service.service_name,
                "service_price":get_service.service_price,
                "pricing_format": "{:,.0f}".format(get_service.service_price),
                "customer_group": get_service.customer_group or "",
                "description": html2text.html2text(get_service.description or "").strip(), 
                "my_service_payment_status":get_my_service.payment_status,
                "my_service_payment_date":format_date(get_my_service.payment_date),
                "payment_invoice":"",
                "our_service_documents":[],
                "user_documents":[],
                "process_steps":[]
            }

            our_service_documents = frappe.db.get_all("Our Services Documents",{'parent':get_service.name},["*"],order_by='idx ASC')
            for service_document in our_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["our_service_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                })
            
            my_service_documents = frappe.db.get_all("My Service Documents",{'parent':get_my_service.name},["*"],order_by='idx ASC')
            for service_document in my_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["user_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                })

            process_steps = frappe.db.get_all("My Services Process Steps",{'parent':get_my_service.name},["*"],order_by='idx ASC')
            for process in process_steps:
                if process.status == "Completed":
                    process_status = True
                else:
                    process_status = False
                if process.doc_upload == 1:
                    doc_upload_status = True
                else:
                    doc_upload_status = False
                my_services["process_steps"].append({
                    "steps":process.steps,
                    "tat":process.tat,
                    "current_status":process.status,
                    "step_status":process_status,
					"doc_status":doc_upload_status
                })    
            status = True
            message = "My Service"
        else:
            status = False
            message = "My Service Not Found"
        return {"status":status,"message":message,"my_service":my_services}    
    except Exception as e:
        return {"status":False,"message":e}



@frappe.whitelist()
def get_my_services(user_name):
    try:
        my_services_list = []
        doc_upload_status = False
        process_status = False
        get_my_service = frappe.db.get_all("My Services",{"user":user_name},["*"],order_by='idx ASC')
        for service in get_my_service:
            get_service = frappe.get_doc("Our Services",service.our_services)
            get_sales_invoice = frappe.db.get_value("Sales Invoice",{"customer":service.full_name},["name"])
            get_invoice = frappe.db.get_value("File",{"attached_to_doctype":"Sales Invoice","attached_to_name":get_sales_invoice},["file_url"])
            if get_service.service_image:
                image_url = get_domain_name() + get_service.service_image
            else:
                image_url = ""   

            my_services = {
                "id":service.name,
                "name":service.name,
                "our_service_id":get_service.name,
                "service_image":image_url,
                "service_invoice":get_domain_name() + get_invoice or "",
                "service_name":get_service.service_name,
                "service_price":get_service.service_price,
                "pricing_format": "{:,.0f}".format(get_service.service_price),
                "customer_group": get_service.customer_group or "",
                "description": html2text.html2text(get_service.description or "").strip(), 
                "my_service_payment_status":service.payment_status,
                "my_service_payment_date":format_date(service.payment_date),
                "payment_invoice":"",
                "our_service_documents":[],
                "user_documents":[],
                "process_steps":[]
            }

            our_service_documents = frappe.db.get_all("Our Services Documents",{'parent':get_service.name},["*"],order_by='idx ASC')
            for service_document in our_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["our_service_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                })
            
            my_service_documents = frappe.db.get_all("My Service Documents",{'parent':service.name},["*"],order_by='idx ASC')
            for service_document in my_service_documents:
                if service_document.document:
                    document_url = get_domain_name() + service_document.document
                else:
                    document_url = ""    
                my_services["user_documents"].append({
                    "document_name":service_document.document_name,
                    "document_type":service_document.document_type,
                    "document_url":document_url
                })

            process_steps = frappe.db.get_all("My Services Process Steps",{'parent':service.name},["*"],order_by='idx ASC')
            for process in process_steps:
                if process.status == "Completed":
                    process_status = True
                else:
                    process_status = False
                if process.doc_upload == 1:
                    doc_upload_status = True
                else:
                    doc_upload_status = False
                my_services["process_steps"].append({
                    "steps":process.steps,
                    "tat":process.tat,
                    "current_status":process.status,
                    "step_status":process_status,
					"doc_status":doc_upload_status
                })     
            my_services_list.append(my_services)
        return {"status":True,"my_services":my_services_list}    
    except Exception as e:
        return {"status":False,"message":e}   
    

    
@frappe.whitelist()
def my_service_doc_upload(user_name,my_service_id,upload_doc):
    try:
        get_my_service = frappe.get_doc("My Services",my_service_id)
        for service in upload_doc:
            file_name_inside = service.get("file_name")
            file_type = service.get("file_type")
            attach_converted_url = base64.b64decode(service.get("file"))
            new_file_inside = frappe.new_doc('File')
            new_file_inside.file_name = f"{file_name_inside.replace(' ', '_')}.{file_type}"
            new_file_inside.content = attach_converted_url
            new_file_inside.attached_to_doctype = "My Services"
            new_file_inside.attached_to_name = get_my_service.name
            new_file_inside.attached_to_field = "attach" 
            new_file_inside.is_private = 0
            new_file_inside.save(ignore_permissions=True)
            frappe.db.commit()

            get_my_service.append("service_documents",{
                "document_name":service.get("file_name"),
                "document_type":service.get("file_type"),
                "document":new_file_inside.file_url
            })
        get_my_service.save(ignore_permissions=True)
        frappe.db.commit()  
        frappe.db.set_value("My Services",get_my_service.name,'owner',user_name)  
        return {"status":True,"message":"doc uploaded"}
    except Exception as e:
        return {"status":False,"message":e}