import frappe
from deck_review.custom import get_domain_name
from frappe.utils import now, getdate, today, format_date,format_time,add_days,datetime


@frappe.whitelist()
def deck_sign_up(user_type, user_name, email, password, deck_id,coupon_code,company_name):
    try:
        coupon_check = validate_coupon_code(user_name, coupon_code, email)
        if not coupon_check.get("status"):
            return coupon_check

        if frappe.db.exists("User", {'name': email, 'enabled': 1}):
            # return get_user_details(email)
            return {"status": True, "message": "Register Successful", "userinfo": get_user_details(email)}

        user_details = create_new_user_and_customer(user_type, user_name, email, password, deck_id, company_name)        
        log_coupon_entry(user_name, coupon_code, email)

        return {"status": True, "message": "Registration Successful", "userinfo": user_details}
    except Exception as e:
        return {"status": False, "message":e}

def validate_coupon_code(email,coupon_code,user_name):
    try:
        valid_coupon_code = frappe.get_doc("Product Coupon Code",coupon_code)
        if getdate(today()) < valid_coupon_code.valid_start_date:
            return {"status":False,"message": f"Coupon code not valid before {format_date(valid_coupon_code.valid_start_date)}"}
        elif getdate(today()) > valid_coupon_code.valid_end_date:
            return {"status": False, "message": "Coupon code has expired"}
        
        if frappe.db.exists("User Coupon Entry", {"user": email, "coupon_code": coupon_code}):
            return {"status": False, "message": "Coupon code already used"}
        
        return {"status": True, "message": "Coupon valid"}
    except Exception as e:
        return {"status":False,"message":e}
    
def create_new_user_and_customer(user_type,user_name,email,password,deck_id,company_name):
    try:
        new_user = frappe.new_doc("User")
        new_user.update({
            'email': email,
            'first_name': user_name,
            'new_password': password,
            'send_welcome_email': 0,
        })
        new_user.append('roles', {'role': user_type})
        new_user.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("User",new_user.name,'owner',email)

        if deck_id:
            frappe.db.set_value("Deck Review",deck_id,"user_idemail",email)
            get_deck_name = frappe.get_doc("Deck Review", deck_id)
            log_notification(email, get_deck_name.deck_name)

        new_customer = frappe.new_doc("Customer")
        new_customer.update({
            'customer_name': user_name,
            'customer_group': user_type,
            'custom_user': email,
            'custom_current_password': password,
            "custom_company_name":company_name
        })
        new_customer.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Customer",new_customer.name,'owner',email)

        return get_user_details(email)
    except Exception as e:
        return {"status":False,"message":e}

def log_coupon_entry(user_name, coupon_code, email):
    try:
        end_date = add_days(getdate(today()), 9)
        new_coupon_entry = frappe.new_doc("User Coupon Entry")
        new_coupon_entry.update({
            'user': email,
            "full_name": user_name,
            'coupon_code': coupon_code,
            'start_date': getdate(today()),
            'end_date': end_date
        })
        new_coupon_entry.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("User Coupon Entry", new_coupon_entry.name, 'owner', email)

        return {"status": True, "message": "Coupon successfully applied"}
    except Exception as e:
        return {"status": False, "message": e}

def get_user_details(email):
    try:
        get_user = frappe.get_doc("User", email)
        if not get_user:
            return {"status": False, "message": "User not found"}

        user_image = get_user.user_image or ""
        image_url = get_domain_name() + user_image if user_image else ""
        customer_details = frappe.get_value("Customer", {"custom_user": email}, ['customer_group', 'custom_view_status',"custom_company_name"])

        user_details = {
            "user_email": get_user.name,
            "user_name": get_user.first_name,
            "user_type": customer_details[0] if customer_details else "",
            "image_url": image_url,
            "view_status": bool(customer_details[1]) if customer_details else False,
            "company_name":customer_details[2],
            "subscription_status":False,
            "subscription_expiry_date":""
        }

        return user_details
    except Exception as e:
        return {"status": False, "message": e}

def log_notification(email, deck_name):
    try:
        new_notification_log = frappe.new_doc("Notification Log")
        new_notification_log.subject = "Deck Uploaded"
        new_notification_log.type = "Alert"
        new_notification_log.for_user = email
        new_notification_log.email_content = "Your Deck {} was Created".format(deck_name)
        new_notification_log.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Notification Log",new_notification_log.name,'owner',email)
        return {"status":True,"message":"success"}
    except Exception as e:
        return {"status":False,"message":e}


