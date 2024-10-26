import frappe
import base64
from deck_review.custom import get_domain_name


@frappe.whitelist()
def get_profile_information(user_name):
    try:
        status = ""
        message = ""
        image_url = ""
        profile_information_list = []
        company_information_list = []
        get_customer_id = frappe.db.exists("Customer",{"custom_user":user_name})
        if get_customer_id:
            get_customer_data = frappe.get_doc("Customer",get_customer_id)
            if get_customer_data.customer_primary_address:
                get_customer_address = frappe.get_doc("Address",get_customer_data.customer_primary_address)
            else:
                get_customer_address = None 
            if get_customer_data.image:
                image_url = get_domain_name() + get_customer_data.image
            else:
                image_url = ""     
            user_profile = {
                "id": get_customer_data.name,
                "name": get_customer_data.name,
                "profile_image":image_url,
                "full_name": get_customer_data.customer_name,
                "gender": get_customer_data.custom_gender_information or "",
                "mobile_no": get_customer_data.custom_mobile_number or "",
                "mail_id": get_customer_data.custom_mail_id or "",
                "linkedin": get_customer_data.custom_linkedin or "",
                "about": get_customer_data.custom_about or "",
            }
            profile_information_list.append(user_profile)
            user_company = {
                "id": get_customer_data.name,
                "name": get_customer_data.name,
                "address_id": get_customer_address.name if get_customer_address else "",
                "company_name": get_customer_data.custom_company_name or "",
                "position": get_customer_data.custom_position or "",
                "sector": get_customer_data.custom_sector or "",
                "mail_id": get_customer_data.custom_company_mail_id or "",
                "address": get_customer_address.address_line1 if get_customer_address else "",
                "city": get_customer_address.city if get_customer_address else "",
                "country": get_customer_address.country if get_customer_address else "",
                "state": get_customer_address.state if get_customer_address else "",
                "pincode": get_customer_address.pincode if get_customer_address else "",
                "website": get_customer_data.website or "",
                "company_about": get_customer_data.custom_about_company or ""
            }
            company_information_list.append(user_company)
            status = True
            message = "Profile"
        else:
            status = False
            message = "Customer Not Found"    
        return {"status":status,"message":message,"profile_information":profile_information_list,"company_information":company_information_list}    
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def set_profile_image(user_name,profile_image,file_name,file_type):
    try:
        view_status = ""
        status = ""
        message = ""
        image_url = ""
        convert_image_base64 = base64.b64decode(profile_image)
        get_customer = frappe.db.get_value("Customer",{"custom_user":user_name},["name"])
        if get_customer:
            get_user = frappe.get_doc("User",user_name)
            if profile_image:

                #for user image updated
                new_file_inside = frappe.new_doc('File')
                new_file_inside.file_name = f"{file_name.replace(' ', '_')}.{file_type}"
                new_file_inside.content = convert_image_base64
                new_file_inside.attached_to_doctype = "User"
                new_file_inside.attached_to_name = get_user.name
                new_file_inside.attached_to_field = "user_image"
                new_file_inside.is_private = 0
                new_file_inside.save(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value("User",get_user.name,'user_image',new_file_inside.file_url)
                frappe.db.set_value("User",get_user.name,'owner',user_name)

                #for customer image updated
                new_file_inside = frappe.new_doc('File')
                new_file_inside.file_name = f"{file_name.replace(' ', '_')}.{file_type}"
                new_file_inside.content = convert_image_base64
                new_file_inside.attached_to_doctype = "Customer"
                new_file_inside.attached_to_name = get_customer
                new_file_inside.attached_to_field = "image"
                new_file_inside.is_private = 0
                new_file_inside.save(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value("Customer",get_customer,'image',new_file_inside.file_url)
                frappe.db.set_value("Customer",get_customer,'owner',user_name)

            else:
                frappe.db.set_value("User",get_user.name,'user_image',"")
                frappe.db.set_value("User",get_user.name,'owner',user_name)  

                frappe.db.set_value("Customer",get_customer,'image',"")
                frappe.db.set_value("Customer",get_customer,'owner',user_name)  

            updated_customer = frappe.get_doc("Customer",get_customer) 
            get_user = frappe.get_doc("User",user_name)
            if updated_customer.image:
                image_url = get_domain_name() + updated_customer.image
            else:
                image_url = ""    
            if updated_customer.custom_view_status == 1:
                view_status = True
            else:
                view_status = False  
            get_profile_image = {
                "user_email":get_user.name,
                "user_name":get_user.full_name,
                "user_type":updated_customer.customer_group,
                "image_url":image_url,
                "view_status":view_status,
                "company_name":updated_customer.custom_company_name
            }
            status = True
            message = "Profile Image Updated"    
        else:
            status = False
            message = "Customer Not Found"   
        return {"status":status,"message":message,"userinfo":get_profile_image}         
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def profile_edit(user_name,full_name,gender,mobile_no,mail_id,linkedin):
    try:
        status = ""
        message = ""
        profile_list = []
        get_customer_id = frappe.db.exists("Customer",{"custom_user":user_name})
        if get_customer_id:
            get_customer = frappe.get_doc("Customer",get_customer_id)
            get_customer.customer_name = full_name
            get_customer.custom_full_name = full_name
            get_customer.custom_gender_information = gender
            get_customer.custom_mobile_number = mobile_no
            get_customer.custom_mail_id = mail_id
            get_customer.custom_linkedin = linkedin
            get_customer.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Customer",get_customer.name,'owner',user_name)

            #update user full name
            get_user = frappe.get_doc("User",user_name)
            get_user.full_name = full_name
            get_user.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("User",get_user.name,'owner',user_name)

            get_customer_data = frappe.get_doc("Customer",get_customer.name)
            user_profile = {
                "id":get_customer_data.name,
                "name":get_customer_data.name,
                "full_name":get_customer_data.custom_full_name,
                "gender":get_customer_data.custom_gender_information,
                "mobile_no":get_customer_data.custom_mobile_number,
                "mail_id":get_customer_data.custom_mail_id,
                "linkedin":get_customer_data.custom_linkedin
            }
            profile_list.append(user_profile)
            status = True
            message = "Profile Updated"
        else:
            status = False
            message = "Customer Not Found"    
        return {"status":status,"message":message,"profile":profile_list}
    except Exception as e:
        return {"status":False,"message":e}
    
@frappe.whitelist()
def profile_edit_about(user_name,about):
    try:
        status = ""
        message = ""
        about_list = []
        get_customer_id = frappe.db.exists("Customer",{"custom_user":user_name})
        if get_customer_id:
            get_customer = frappe.get_doc("Customer",get_customer_id)
            get_customer.custom_about = about
            get_customer.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Customer",get_customer.name,'owner',user_name)

            get_customer_data = frappe.get_doc("Customer",get_customer.name)
            user_profile_about = {
                "id":get_customer_data.name,
                "name":get_customer_data.name,
                "about":get_customer_data.custom_about
            }
            about_list.append(user_profile_about)
            status = True
            message = "Profile Updated"
        else:
            status = False
            message = "Customer Not Found"    
        return {"status":status,"message":message,"profile_about":about_list}    
    except Exception as e:
        return {"status":False,"messsage":e}
    

@frappe.whitelist()
def edit_company_inforamtion(user_name,company_name,position,sector,mail_id,address_id,address,city,country,state,pincode,website):
    try:
        status = ""
        message = ""
        company_list = []
        get_customer_id = frappe.db.exists("Customer",{"custom_user":user_name})
        if get_customer_id:
            if not address_id:
                new_address = frappe.new_doc("Address")
                new_address.address_title = company_name
                new_address.address_type = "Office"
                new_address.address_line1 = address
                new_address.city = city
                new_address.country = country
                new_address.state = state
                new_address.pincode = pincode
                new_address.email_id = mail_id
                new_address_child_table = new_address.append("links",{})
                new_address_child_table.link_doctype = "Customer"
                new_address_child_table.link_name = get_customer_id
                new_address.insert(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value("Address",new_address.name,'owner',user_name)
                primary_address = new_address.name
            else:
                get_address = frappe.get_doc("Address",address_id)
                get_address.address_title = company_name
                get_address.address_type = "Office"
                get_address.address_line1 = address
                get_address.city = city
                get_address.country = country
                get_address.state = state
                get_address.pincode = pincode
                get_address.email_id = mail_id
                get_address.save(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value("Address",get_address.name,'owner',user_name)
                primary_address = get_address.name

            get_customer = frappe.get_doc("Customer",get_customer_id)
            get_customer.custom_company_name = company_name
            get_customer.custom_position = position
            get_customer.custom_sector = sector
            get_customer.custom_company_mail_id = mail_id
            get_customer.customer_primary_address = primary_address
            get_customer.website = website
            get_customer.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Customer",get_customer.name,'owner',user_name)

            get_customer_data = frappe.get_doc("Customer",get_customer.name)
            get_customer_address = frappe.get_doc("Address",get_customer_data.customer_primary_address)
            company_information = {
                "id":get_customer_data.name,
                "name":get_customer_data.name,
                "address_id":get_customer_address.name,
                "company_name":get_customer_data.custom_company_name,
                "position":get_customer_data.custom_position,
                "sector":get_customer_data.custom_sector,
                "mail_id":get_customer_data.custom_company_mail_id,
                "address":get_customer_address.address_line1,
                "city":get_customer_address.city,
                "country":get_customer_address.country,
                "state":get_customer_address.state,
                "pincode":get_customer_address.pincode,
                "website":get_customer_data.website,
            }
            company_list.append(company_information)
            status = True
            message = "Company Information Updated"
        else:
            status = False
            message = "Customer Not Found"    
        return {"status":status,"message":message,"company_information":company_list}  
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def edit_about_company(user_name,about_company):
    try:
        status = ""
        message = ""
        about_list = []
        get_customer_id = frappe.db.exists("Customer",{"custom_user":user_name})
        if get_customer_id:
            get_customer = frappe.get_doc("Customer",get_customer_id)
            get_customer.custom_about_company = about_company
            get_customer.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Customer",get_customer.name,'owner',user_name)

            get_customer_data = frappe.get_doc("Customer",get_customer.name)
            user_company_about = {
                "id":get_customer_data.name,
                "name":get_customer_data.name,
                "company_about":get_customer_data.custom_about_company
            }
            about_list.append(user_company_about)
            status = True
            message = "Profile Updated"
        else:
            status = False
            message = "Customer Not Found"    
        return {"status":status,"message":message,"about_company":about_list}
    except Exception as e:
        return {"status":False,"message":e}      

@frappe.whitelist()
def change_user_password(user_name,current_password,new_password):
    try:
        status = ""
        message = ""
        check_password = frappe.db.get_value("Customer",{"custom_user":user_name},["custom_current_password"])
        if check_password == current_password:
            
            #change password in user doctype
            change_user_password = frappe.get_doc("User",user_name)
            change_user_password.new_password = new_password
            change_user_password.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("User",user_name,'owner',user_name)

            #change password in Customer Doctype
            get_customer = frappe.db.get_value("Customer",{"custom_user":user_name},["name"])
            set_password = frappe.get_doc("Customer",get_customer)
            set_password.custom_current_password = new_password
            set_password.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Customer",set_password.name,'owner',user_name)

            status = True
            message = "Password Changed"
        else:
            status = False
            message = "Current Password not Match"
        return {"status":status,"message":message}    
    except Exception as e:
        return {"status":False,"message":e}
    
@frappe.whitelist()
def update_user_view_status(user_name,view_status):
    try:
        image_url = ""
        get_customer = frappe.db.get_value("Customer",{"custom_user":user_name},["name"])

        frappe.db.set_value("Customer",get_customer,"custom_view_status",view_status)

        update_customer = frappe.get_doc("Customer",get_customer)

        if update_customer.image:
            image_url = get_domain_name() + update_customer.image
        else:
            image_url = "" 
        
        if update_customer.custom_view_status == 1:
            view_status = True
        else:
            view_status = False  

        user_details = {
            "user_email":update_customer.custom_user,
            "user_name":update_customer.name,
            "user_type":update_customer.customer_group,
            "image_url":image_url,
            "view_status":view_status,
            "company_name":update_customer.custom_company_name
        }
        return {"status":True,"message":"success","userinfo":user_details}
    except Exception as e:
        return {"status":False,"message":e}