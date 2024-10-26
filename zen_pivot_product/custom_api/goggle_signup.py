import frappe
import base64
from deck_review.custom import get_domain_name
from frappe.utils import now, getdate, today, format_date, add_days


@frappe.whitelist()
def create_google_signup(user_name, email, user_type, deck_id, profile_image, file_name, file_type, coupon_code,company_name):
    try:
        if coupon_code:
            coupon_check = validate_coupon_code(coupon_code)
            if not coupon_check.get("status"):
                return coupon_check

            if frappe.db.exists("User", {'name': email, 'enabled': 1}):
                return {"status": True, "message": "Register Successful", "userinfo": get_user_details(email)}
            
            new_user = frappe.new_doc("User")
            new_user.update({
                'email': email,
                'first_name': user_name,
                'send_welcome_email': 0,
            })
            new_user.append('roles', {'role': user_type})
            new_user.save(ignore_permissions=True)
            frappe.db.commit()

            if profile_image:
                attach_image_to_doctype(new_user.name, "User", profile_image, file_name, file_type)

            if deck_id:
                frappe.db.set_value("Deck Review", deck_id, "user_idemail", email)
                get_deck_name = frappe.get_doc("Deck Review", deck_id)
                log_notification(user_name, get_deck_name.deck_name)

            new_customer = frappe.new_doc("Customer")
            new_customer.update({
                'customer_name': user_name,
                'customer_group': user_type,
                'custom_user': email,
                'custom_company_name':company_name
            })
            new_customer.save(ignore_permissions=True)
            frappe.db.commit()

            if profile_image:
                attach_image_to_doctype(new_customer.name, "Customer", profile_image, file_name, file_type)
            
            if coupon_code:
                create_coupon_code_log(email,user_name, coupon_code)
            return {"status": True, "message": "Register Successful", "userinfo": get_user_details(email)}
        else:
            if frappe.db.exists("User Coupon Entry",{"user":email}):
                return {"status": True, "message": "Register Successful", "userinfo": get_user_details(email)}
            else:
                return {"status": False, "message": "Coupon Code Not Created Please select Coupon code ", "userinfo":[]}
    except Exception as e:
        return {"status": False, "message": str(e)}

def validate_coupon_code(coupon_code):
    """Validate the coupon code without creating an entry"""
    try:
        valid_coupon_code = frappe.get_doc("Product Coupon Code", coupon_code)

        if getdate(today()) < valid_coupon_code.valid_start_date:
            return {"status": False, "message": f"Coupon not valid until {format_date(valid_coupon_code.valid_start_date)}"}

        elif getdate(today()) > valid_coupon_code.valid_end_date:
            return {"status": False, "message": "Coupon code has expired"}

        return {"status": True, "message": "Coupon is valid"}

    except Exception as e:
        return {"status": False, "message": str(e)}

def create_coupon_code_log(email, user_name,coupon_code):
    """Create the coupon code entry after user creation"""
    try:
        end_date = add_days(getdate(today()), 9)
        new_coupon_entry = frappe.new_doc("User Coupon Entry")
        new_coupon_entry.update({
            'user': email,
            'first_name': user_name,
            'coupon_code': coupon_code,
            'start_date': getdate(today()),
            'end_date': end_date
        })
        new_coupon_entry.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("User Coupon Entry", new_coupon_entry.name, 'owner', email)

        return {"status": True, "message": "Coupon successfully applied"}

    except Exception as e:
        return {"status": False, "message": str(e)}


def get_user_details(email):
    try:
        coupon_code_expired = ""
        get_user = frappe.get_doc("User", email)
        if not get_user:
            return {"status": False, "message": "User not found"}

        user_image = get_user.user_image or ""
        image_url = get_domain_name() + user_image if user_image else ""
        customer_details = frappe.get_value("Customer", {"custom_user": email}, ['customer_group', 'custom_view_status','custom_company_name'])

        coupon_entry = frappe.db.get_value("User Coupon Entry",{"user": email},["start_date", "end_date"],)
        if coupon_entry:
            start_date, end_date = coupon_entry
            if getdate(today()) > getdate(end_date):
                coupon_code_expired = False
            else:
                coupon_code_expired = True

        user_details = {
            "user_email": get_user.name,
            "user_name": get_user.first_name,
            "user_type": customer_details[0] if customer_details else "",
            "image_url": image_url,
            "view_status": bool(customer_details[1]) if customer_details else False,
            "company_name":customer_details[2],
            "subscription_status":coupon_code_expired,
            "subscription_expiry_date":format_date(coupon_entry[1])
        }

        return user_details
    except Exception as e:
        return {"status": False, "message": str(e)}

def attach_image_to_doctype(doc_name, doctype, profile_image, file_name, file_type):
    """Helper function to attach profile image to a specified Doctype and return a list of files"""
    try:
        new_file = frappe.new_doc('File')
        new_file.update({
            'file_name': f"{file_name.replace(' ', '_')}.{file_type}",
            'content': base64.b64decode(profile_image),
            'attached_to_doctype': doctype,
            'attached_to_name': doc_name,
            'attached_to_field': "image" if doctype == "Customer" else "user_image",
            'is_private': 0
        })
        new_file.save(ignore_permissions=True)
        frappe.db.commit()

        file_list = [{
            "doctype": doctype,
            "name": doc_name,
            "file_url": new_file.file_url
        }]
        image_field = 'image' if doctype == 'Customer' else 'user_image'
        frappe.db.set_value(doctype, doc_name, image_field, new_file.file_url)

        return file_list
    except Exception as e:
        frappe.log_error(f"Error attaching image: {e}", "attach_image_to_doctype_error")
        return []


def log_notification(user_name, deck_name):
    try:
        new_notification_log = frappe.new_doc("Notification Log")
        new_notification_log.update({
            'subject': "Deck Uploaded",
            'type': "Alert",
            'for_user': user_name,
            'email_content': f"Your Deck {deck_name} was Created"
        })
        new_notification_log.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Notification Log", new_notification_log.name, 'owner', user_name)
    except Exception as e:
        frappe.log_error(f"Notification log error: {e}", "log_notification_error")
