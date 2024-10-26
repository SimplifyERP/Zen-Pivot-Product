import frappe
import base64
from deck_review.custom import get_domain_name
import json

#create a new vault
@frappe.whitelist()
def create_new_valut(user_name,vault_name,description,upload_doc):
    try:
        status = ""
        message = ""
        valut_list = []
        if frappe.db.exists("User",user_name):
            new_vault = frappe.new_doc("Vault")
            new_vault.user = user_name
            new_vault.vault_name = vault_name
            new_vault.description = description
            new_vault.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Vault",new_vault.name,'owner',user_name)

            new_notification_log = frappe.new_doc("Notification Log")
            new_notification_log.subject = "Vault"
            new_notification_log.type = "Alert"
            new_notification_log.for_user = user_name
            new_notification_log.email_content = "Your Vault {} for was Created".format(new_vault.vault_name)
            new_notification_log.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Notification Log",new_notification_log.name,'owner',user_name)
            
            decode_json_doc = json.loads(upload_doc)
            if not decode_json_doc == []:
                for file in decode_json_doc:
                    file_name = file.get("file_name")
                    file_type = file.get("file_type")
                    file_content = file.get("file")
                    decoded_content = base64.b64decode(file_content)

                    new_file_inside = frappe.new_doc('File')
                    new_file_inside.file_name = file_name
                    new_file_inside.content = decoded_content
                    new_file_inside.attached_to_doctype = "Vault"
                    new_file_inside.attached_to_name = new_vault.name
                    new_file_inside.attached_to_field = "file" 
                    new_file_inside.is_private = 0
                    new_file_inside.save(ignore_permissions=True)
                    frappe.db.commit()
                    
                    doc_upload = frappe.get_doc("Vault",new_vault.name)
                    doc_upload.append('file_upload', {
                        "file_name":file_name,
                        "file_type":file_type,
                        "file":new_file_inside.file_url
                    })
                    doc_upload.save(ignore_permissions=True)
                    frappe.db.commit() 

                get_vault = frappe.get_doc("Vault",new_vault.name)
                valut = {
                    "id":get_vault.name,
                    "name":get_vault.name,
                    "user":get_vault.user,
                    "vault_name":get_vault.vault_name,
                    "description":get_vault.description,
                    "file_upload":[]
                }
                get_documents = frappe.db.get_all("Vault Table",{'parent':get_vault.name,"disabled":0},['name','file_name','file_type','file'],order_by='idx ASC')
                for documents in get_documents:
                    if documents.file:
                        doc_url = get_domain_name() + documents.file
                    else:
                        doc_url = "" 
                    valut["file_upload"].append({
                        "doc_id":documents.name,
                        "file_name":documents.file_name or "",
                        "file_type":documents.file_type,
                        "file": doc_url,
                    })  
                valut_list.append(valut)              
                status = True
                message = "Vault Created Successfully"
            else:
                status = False
                message = "Please Upload Files"    
        else:
            status = False
            message = "User not Found"   
        return {"status":status,"message":message,"vault_details":valut_list}     
    except Exception as e:
        return {"status":False,"message":e}
    
#get overall vault list against user
@frappe.whitelist()
def get_vault_list(user_name):
    try:
        valut_list = []
        get_vault = frappe.db.get_all("Vault",{"disabled":0,"user":user_name},["*"], order_by='idx ASC')
        for vault in get_vault:
            valut = {
                "id":vault.name,
                "name":vault.name,
                "user":vault.user,
                "vault_name":vault.vault_name,
                "description":vault.description,
                "file_upload":[]
            }
            get_documents = frappe.db.get_all("Vault Table",{'parent':vault.name,"disabled":0},['name','file_name','file_type','file'],order_by='idx ASC')
            for documents in get_documents:
                if documents.file:
                    doc_url = get_domain_name() + documents.file
                else:
                    doc_url = "" 
                valut["file_upload"].append({
                    "doc_id":documents.name,
                    "file_name":documents.file_name or "",
                    "file_type":documents.file_type,
                    "file": doc_url,
                })  
            valut_list.append(valut)
        return {"status":True,"vault_details":valut_list}
    except Exception as e:
        return {"status":False,"messagse":e}
    
#update the vault
@frappe.whitelist()
def update_vault(user_name,vault_id,vault_name,description):
    try:
        status = ""
        message = ""
        valut_list = []
        if frappe.db.exists("Vault",vault_id):
            get_vault = frappe.get_doc("Vault",vault_id)
            get_vault.vault_name = vault_name
            get_vault.description = description
            get_vault.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Vault",vault_id,'owner',user_name)

            get_vault = frappe.get_doc("Vault",vault_id)
            valut = {
                "id":get_vault.name,
                "name":get_vault.name,
                "user":get_vault.user,
                "vault_name":get_vault.vault_name,
                "description":get_vault.description,
                "file_upload":[]
            }
            get_documents = frappe.db.get_all("Vault Table",{'parent':get_vault.name,"disabled":0},['name','file_name','file_type','file'],order_by='idx ASC')
            for documents in get_documents:
                if documents.file:
                    doc_url = get_domain_name() + documents.file
                else:
                    doc_url = "" 
                valut["file_upload"].append({
                    "doc_id":documents.name,
                    "file_name":documents.file_name or "",
                    "file_type":documents.file_type,
                    "file": doc_url,
                })  
            valut_list.append(valut)              
            status = True
            message = "Vault Updated"
        else:
            status = False
            message = "Vault ID not Found"
        return {"status":status,"message":message,"vault_details":valut_list}
    except Exception as e:
        return {"status":False,"message":e}
    
#create a new file in already exists vault
@frappe.whitelist()
def create_new_file(user_name,vault_id,file_name,file_type,file):
    try:
        valut_list = []
        status = ""
        message = ""
        decoded_content = base64.b64decode(file)
        new_file_inside = frappe.new_doc('File')
        new_file_inside.file_name = file_name
        new_file_inside.content = decoded_content
        new_file_inside.attached_to_doctype = "Vault"
        new_file_inside.attached_to_name = vault_id
        new_file_inside.attached_to_field = "file" 
        new_file_inside.is_private = 0
        new_file_inside.save(ignore_permissions=True)
        frappe.db.commit()
                
        doc_upload = frappe.get_doc("Vault",vault_id)
        doc_upload.append('file_upload', {
            "file_name":file_name,
            "file_type":file_type,
            "file":new_file_inside.file_url
        })
        doc_upload.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Vault",vault_id,'owner',user_name)

        get_vault = frappe.get_doc("Vault",vault_id)
        valut = {
            "id":get_vault.name,
            "name":get_vault.name,
            "user":get_vault.user,
            "vault_name":get_vault.vault_name,
            "description":get_vault.description,
            "file_upload":[]
        }
        get_documents = frappe.db.get_all("Vault Table",{'parent':get_vault.name,"disabled":0},['name','file_name','file_type','file'],order_by='idx ASC')
        for documents in get_documents:
            if documents.file:
                doc_url = get_domain_name() + documents.file
            else:
                doc_url = "" 
            valut["file_upload"].append({
                "doc_id":documents.name,
                "file_name":documents.file_name or "",
                "file_type":documents.file_type,
                "file": doc_url,
            })  
        valut_list.append(valut)              
        status = True
        message = "File Uploaded"
        return {"status":status,"message":message,"vault_details":valut_list}    
    except Exception as e:
        return {"status":False,"message":e}


@frappe.whitelist()
def vault_invite_people():
    try:
        image_url = ""
        invite_people_list = []
        get_investors = frappe.db.get_all("Customer",{"customer_group":"Investor"},["name","custom_user","customer_name","image"])
        for investors in get_investors:
            if investors.image:
                image_url = get_domain_name() + investors.image
            else:
                image_url = ""    
            invite_people = {
                "id":investors.name,
                "name":investors.name,
                "email_id":investors.custom_user,
                "full_name":investors.customer_name,
                "image":image_url
            }
            invite_people_list.append(invite_people)
        return {"status":True,"invite_people":invite_people_list}
    except Exception as e:
        return {"status":False,"messsage":e}


#share the vault
@frappe.whitelist()
def share_vault(user_name,vault_id,invite_people,share_link):
    try:
        vault_share = ""
        status = ""
        message = ""
        get_customer = frappe.db.get_value("Customer",{"custom_user":user_name},["name"])
        if get_customer:
            if frappe.db.exists("Vault",{"name":vault_id}):
                vault_share = "Success"
            else:
                vault_share = ""    

            decode_json_doc = json.loads(invite_people)
            if not decode_json_doc == []:
                get_vault = frappe.get_doc("Vault",vault_id)
                for vault in decode_json_doc:
                    get_vault.append("invite_peoples",{
                        "email_id":vault.get("email_id"),
                        "view_status":vault.get("view_status")
                    })
                get_vault.save(ignore_permissions=True)
                frappe.db.commit()    
                frappe.db.set_value("Vault",vault_id,'owner',user_name)

                share_valut = {
                    "vault_share":vault_share,
                    "share_link":share_link
                }
                
                status = True
                message = "Vault Shared"
            else:
                status = False
                message = "Invite Peoples is Empty"    
        else:
            share_valut = []
            status = False
            message = "Customer Not Found"    
        return {"status":status,"message":message,"vault_share":share_valut}    
    except Exception as e:
        return {"status":False,"message":e}

    

@frappe.whitelist()
def share_file(user_name,vault_id,invite_people,file_id,share_link):
    try:
        file_share = ""
        status = ""
        message = ""
        get_customer = frappe.db.get_value("Customer",{"custom_user":user_name},["name"])
        if get_customer:
            if frappe.db.exists("Vault Table",{"name":file_id}):
                file_share = "Success"
            else:
                file_share = ""    
            
            decode_json_doc = json.loads(invite_people)
            if not decode_json_doc == []:
                get_vault = frappe.get_doc("Vault",vault_id)
                for vault in decode_json_doc:
                    get_vault.append("invite_peoples",{
                        "email_id":vault.get("email_id"),
                        "view_status":vault.get("view_status")
                    })
                get_vault.save(ignore_permissions=True)
                frappe.db.commit()    
                frappe.db.set_value("Vault",vault_id,'owner',user_name)

                share_file = {
                    "file_share":file_share,
                    "share_link":share_link
                }

                status = True
                message = "File Shared"
            else:
                status = False
                message = "Invite Peoples is Empty"    
        else:
            status = False
            message = "Customer Not Found"    
        return {"status":status,"message":message,"file_share":share_file}    
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def get_per_vault_details(vault_id):
    try:
        get_vault = frappe.get_doc("Vault",vault_id)
        valut = {
            "id":get_vault.name,
            "name":get_vault.name,
            "user":get_vault.user,
            "vault_name":get_vault.vault_name,
            "description":get_vault.description,
            "file_upload":[]
        }
        get_documents = frappe.db.get_all("Vault Table",{'parent':get_vault.name,"disabled":0},['name','file_name','file_type','file'],order_by='idx ASC')
        for documents in get_documents:
            if documents.file:
                doc_url = get_domain_name() + documents.file
            else:
                doc_url = "" 
            valut["file_upload"].append({
                "doc_id":documents.name,
                "file_name":documents.file_name or "",
                "file_type":documents.file_type,
                "file": doc_url,
            })  
        return {"status":True,"vault_details":valut }
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def delete_vault(user_name,vault_id,delete):
    try:
        get_vault = frappe.get_doc("Vault",vault_id)
        get_vault.disabled = delete
        get_vault.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Vault",vault_id,'owner',user_name)
        return{"status":True,"message":"Vault Deleted"}
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def delete_file(user_name,vault_id,file_id,delete):
    try:
        get_vault = frappe.get_doc("Vault",vault_id)
        for vault in get_vault.file_upload:
            if vault.name == file_id:
                vault.disabled = delete
        get_vault.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Vault",vault_id,'owner',user_name)
        return{"status":True,"message":"File Deleted in Vault"}
    except Exception as e:
        return {"status":False,"message":e}    