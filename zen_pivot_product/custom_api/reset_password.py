import frappe
import random
from frappe.core.doctype.communication.email import make

@frappe.whitelist()
def send_otp_to_mail(email):
    try:
        status = ""
        message = ""
        if frappe.db.exists("User",email):
            reset_code = "{:04d}".format(random.randint(1, 9999))
            get_customer = frappe.db.get_value("Customer",{"custom_user":email},["name"])
            if get_customer:
                frappe.db.set_value("Customer",get_customer,"custom_reset_otp",reset_code)

                # Send the reset code to the user's email
                subject = "Your Password Reset Code"
                message = f"Your password reset code is: {reset_code}"
                
                make(
                    recipients=email,
                    subject=subject,
                    content=message,
                    send_email=True
                )
                status = True
                message = "Password Send Your Email"
            else:    
                status = False
                message = "Customer Not Created"
        else:
            status = False
            message = "User Not Created"    
        return {"status":status,"message":message}
    except Exception as e:
        return {"status":False,"message":e}
    
@frappe.whitelist()
def reset_password(email,otp,new_password):
    try:
        status = ""
        message = ""
        user_details = []
        user_email = ""
        customer_name = ""
        customer_user_type = ""
        if frappe.db.exists("User",email):
            get_customer = frappe.db.get_value("Customer",{"custom_user":email},["custom_reset_otp","name"])
            if get_customer[0] == int(otp):
                password_update = frappe.get_doc("User",email)
                password_update.new_password = new_password
                password_update.save(ignore_permissions=True)
                frappe.db.commit()
                
                get_user = frappe.get_doc("User",email)
                if get_user:
                    user_email = get_user.name
                    customer_name = get_user.first_name
                else:
                    user_email = ""
                    customer_name  = ""    
                
                get_customer_details = frappe.get_doc("Customer",get_customer[1])
                if get_customer_details:
                    customer_user_type = get_customer_details.customer_group
                else:
                    customer_user_type = ""    

                user_details = {
                    "user_email":user_email,
                    "user_name":customer_name,
                    "user_type":customer_user_type
                }
                status = True
                message = "Password Reset Sucessfully"
            else:
                status = False
                message = "OTP not Matched"    
        else:
            status = False
            message = "User Not Created"    
        return {"status":status,"message":message,"user_info":user_details}        
    except Exception as e:
        return {"status":False,"message":e}