import frappe
from frappe.utils.password import check_password, get_decrypted_password
from deck_review.custom import get_domain_name
from frappe.utils import getdate, today,format_date


@frappe.whitelist(allow_guest=True)
def user_login(email,password,deck_id):
    view_status = ""
    image_url = ""
    status = ""
    message = ""
    customer_group = ""
    user_details = []
    try:
        user = frappe.get_doc("User",email)
        if user.name:
            if user and check_password(user.name, password):

                coupon_entry = frappe.db.get_value(
                    "User Coupon Entry",
                    {"user": email},
                    ["start_date", "end_date"],
                )

                if coupon_entry:
                    start_date, end_date = coupon_entry
                    if getdate(today()) > getdate(end_date):
                        coupon_code_expired = False
                        coupon_expiry_date = format_date(coupon_entry[1])
                    else:
                        coupon_code_expired = True   
                        coupon_expiry_date = format_date(coupon_entry[1])
                
                get_user_type = frappe.db.get_value("Customer",{"custom_user":email},["customer_group","custom_view_status","custom_company_name"])
                if get_user_type:
                    customer_group = get_user_type[0]
                else:
                    customer_group = ""    
                if deck_id:
                    frappe.db.set_value("Deck Review",deck_id,"user_idemail",email)
                
                if user.user_image:
                    image_url = get_domain_name() + user.user_image
                else:
                    image_url = ""   

                if get_user_type[1] == 1:
                    view_status = True
                else:
                    view_status = False  

                user_details = {
                    "user_email":user.name,
                    "user_name":user.first_name,
                    "user_type":customer_group,
                    "image_url":image_url,
                    "view_status":view_status,
                    "company_name":get_user_type[2],
                    "subscription_status":coupon_code_expired,
                    "subscription_expiry_date":coupon_expiry_date
                }
                status = True
                message = "Login Successful"
            else:
                status = False
                message = "please contact support team" 
        else:
            status = False
            message = "please contact support team"        
        return {"status": status, "message": message, "userinfo":user_details}
    except Exception as e:
        return {"status": False, "message": e} 