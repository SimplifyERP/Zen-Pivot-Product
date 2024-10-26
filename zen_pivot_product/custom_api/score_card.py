import frappe
import base64
from deck_review.custom import get_domain_name


@frappe.whitelist()
def process_score_card_image(user_name,file_name,file_type,score_card_image):
    try:
        """ Get the score card image upload in Score Card Image Doctype and return as image details """
        if score_card_image:
            """ convert the score card image in base 64 to upload in file list """
            convert_image_base64 = base64.b64decode(score_card_image)

            score_card_image = frappe.new_doc("Score Card Image")
            score_card_image.user = user_name
            score_card_image.file_name = file_name
            score_card_image.file_type = file_type
            score_card_image.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Score Card Image",score_card_image.name,'owner',user_name)

            """ create a new file list for the converted base 64 image"""
            new_file_inside = frappe.new_doc('File')
            new_file_inside.file_name = f"{file_name.replace(' ', '_')}.{file_type}"
            new_file_inside.content = convert_image_base64
            new_file_inside.attached_to_doctype = "Score Card Image"
            new_file_inside.attached_to_name = score_card_image.name
            new_file_inside.attached_to_field = "file"
            new_file_inside.is_private = 0
            new_file_inside.save(ignore_permissions=True)
            frappe.db.commit()                   
            frappe.db.set_value("Score Card Image",score_card_image.name,'file',new_file_inside.file_url)

            """ Get Score Card Image Details """
            get_score_card_image = frappe.get_doc("Score Card Image",score_card_image.name)

            """ Giving the json format to api score card details """
            score_card_details = {
                "id":get_score_card_image.name,
                "name":get_score_card_image.name,
                "user_name":get_score_card_image.user,
                "file_name":get_score_card_image.file_name,
                "file_type":get_score_card_image.file_type,
                "file":(get_domain_name() + get_score_card_image.file) or ""
            }
        return {"status":True,"score_card_details":score_card_details}    
    except Exception as e:
        return {"status":False,"message":e}