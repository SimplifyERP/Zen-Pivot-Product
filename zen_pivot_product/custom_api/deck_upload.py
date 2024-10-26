import frappe
import base64
from deck_review.custom import get_domain_name
import json
from pdf_on_submit.attach_pdf import execute



@frappe.whitelist()
def upload_deck_pdf(deck_name,deck_doc):
    try:
        convert_deck_doc_base_64 = base64.b64decode(deck_doc)
        #creating a new doc in deck review
        new_deck = frappe.new_doc("Deck Review")
        new_deck.deck_name = deck_name
        new_deck.get_deck = 1
        new_deck.save(ignore_permissions=True)
        frappe.db.commit()
        #upload deck in file list using api
        file_type = "pdf"
        new_file_inside = frappe.new_doc('File')
        new_file_inside.file_name = f"{deck_name.replace(' ', '_')}.{file_type}"
        new_file_inside.content = convert_deck_doc_base_64
        new_file_inside.attached_to_doctype = "Deck Review"
        new_file_inside.attached_to_name = new_deck.name
        new_file_inside.attached_to_field = "deck_upload"
        new_file_inside.is_private = 0
        new_file_inside.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Deck Review",new_deck.name,'deck_upload',new_file_inside.file_url)
        return {"status":True,"message":"Deck Uploaded","deck_id":new_deck.name}
    except Exception as e:
        return {"status":False,"message":e}
    

@frappe.whitelist()
def get_slide_images(doc_name):
    try:
        deck_status = ""
        pdf_url = []
        slide_image = []
        summary_details_list = []
        slide_images = frappe.db.get_all("Deck Slides", filters={"parent": doc_name}, fields=["slide_image"], order_by="idx asc")
        slide_data_response = frappe.db.get_all("Deck LLM Response", filters={"parent": doc_name}, fields=["slide_no", "title", "feedback","suggestion"], order_by="idx asc")
        get_summary_details = frappe.get_doc("Deck Review",doc_name)
        if get_summary_details.not_a_pitch_deck == 0:
            deck_response = ""
            deck_status = False
            
            # Combine slide images with corresponding slide data
            for slide_img, slide_data in zip(slide_images, slide_data_response):
                image_url = get_domain_name() + slide_img.slide_image
                
                llm_response = {
                    "slide_image": image_url,
                    "slide_no": slide_data.slide_no,
                    "title": slide_data.title,
                    "feedback":slide_data.feedback,
                    "suggestion": slide_data.suggestion
                }
                
                slide_image.append(llm_response)  

            # get_summary_details = frappe.get_doc("Deck Review",doc_name)
            summary_details = {
                "overall_rating": "(100%): " + get_summary_details.overall_rating,
                "team_exp":get_summary_details.team_experience,
                "market_potential":get_summary_details.market_potential,
                "flow_and_clarity":get_summary_details.product_market_fit,
                "most_promising_aspects":get_summary_details.most_promising_aspects,
                "areas_for_improvement":get_summary_details.areas_for_improvement,
                "recommendations":get_summary_details.recommendations
            }     
            summary_details_list.append(summary_details)
            pdf_url = get_current_deck_pdf(get_summary_details.name)
        else:
            deck_response = get_summary_details.no_deck_text or ""
            deck_status = True
            summary_details_list = []    
            pdf_url = []
        return {"status":True,"deck_status":deck_status,"deck_response":deck_response,"deck_details":slide_image,"summary_details":summary_details_list,"deck_pdf_url":pdf_url}
    except Exception as e:
        return {"status":False,"message":e}

""" Get the Deck Review PDF to show in UI """
def get_current_deck_pdf(deck_id):
    pdf_url = ""
    try:  
        get_deck_details = frappe.get_doc("Deck Review",deck_id)
        get_file_list = frappe.db.get_all("File",{"attached_to_doctype":"Deck Review","attached_to_name":get_deck_details.name},["*"])
        for file in get_file_list:
            file_name = file.file_name
            if "Deck-Review" ==  file_name.split("-", 1)[0] + "-" + file_name.split("-", 2)[1]:
                pdf_url = get_domain_name() + file.file_url
            else:
                pdf_url = ""
            return pdf_url
    except Exception as e:
        return pdf_url


@frappe.whitelist()
def get_dashboard_data(user_name):
    try:
        deck_status = ""
        deck_response = "" 
        deck_details_list = []
        get_deck_review = frappe.db.get_all("Deck Review",{"user_idemail":user_name},["*"])
        for deck in get_deck_review:
            deck_image = frappe.db.get_value("Deck Slides",{"parent": deck.name},["slide_image"],order_by="idx asc")
            if deck_image:
                image_url = get_domain_name() + deck_image
            else:
                image_url = ""

            if deck.not_a_pitch_deck == 1:
                deck_status = True
                deck_response = deck.no_deck_text
            else:
                deck_status = False   
                deck_response = "" 
              
            deck_details = {
                "id":deck.name,
                "name":deck.name,
                "deck_name":deck.deck_name,
                "deck_profile_image":image_url,
                "deck_status":deck_status,
                "deck_response":deck_response
            }
            deck_details_list.append(deck_details)      
        return {"status":True,"deck_details":deck_details_list}
    except Exception as e:
        return {"status":False,"message":e}
    

@frappe.whitelist()
def update_user_feedback(deck_id,deck_response_details):
    try:
        response_details_json = json.loads(deck_response_details)
        get_deck_review = frappe.get_doc("Deck Review",deck_id)
        for response_table in get_deck_review.get("llm_response_slide_wise"):
            child_slide_no = response_table.slide_no
            for deck in response_details_json:
                deck_slide_no = deck.get("slide_no")
                if child_slide_no == deck_slide_no:
                    response_table.user_feedback = deck.get("user_feedback")
                    response_table.like = deck.get("like")
                    response_table.dislike = deck.get("dislike")
                    response_table.user_feedback_status = deck.get("user_feedback_status")
        get_deck_review.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status":True,"message": "Feedback updated successfully"}            
    except Exception as e:
        return {"status":False,"message":e}
    

@frappe.whitelist()
def upload_deck_in_dashboard(user_name,deck_name,deck_doc):
    try:
        convert_deck_doc_base_64 = base64.b64decode(deck_doc)
        #creating a new doc in deck review
        new_deck = frappe.new_doc("Deck Review")
        new_deck.deck_name = deck_name
        new_deck.get_deck = 1
        new_deck.user_idemail = user_name
        new_deck.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Deck Review",new_deck.name,'owner',user_name)
        #upload deck in file list using api
        file_type = "pdf"
        new_file_inside = frappe.new_doc('File')
        new_file_inside.file_name = f"{deck_name.replace(' ', '_')}.{file_type}"
        new_file_inside.content = convert_deck_doc_base_64
        new_file_inside.attached_to_doctype = "Deck Review"
        new_file_inside.attached_to_name = new_deck.name
        new_file_inside.attached_to_field = "deck_upload"
        new_file_inside.is_private = 0
        new_file_inside.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Deck Review",new_deck.name,'deck_upload',new_file_inside.file_url)
        return {"status":True,"message":"Deck Uploaded","deck_id":new_deck.name}
    except Exception as e:
        return {"status":False,"message":e}
    

@frappe.whitelist()
def get_pdf_and_download_count(doc_name,pdf_downlad_count):
    try:
        pdf_url = ""

        get_pdf_count = frappe.get_doc("Deck Review",doc_name)
        sum_pdf_count = (get_pdf_count.deck_pdf_dowload_count or 0) + (pdf_downlad_count)
        frappe.db.set_value("Deck Review",doc_name,"deck_pdf_dowload_count",sum_pdf_count)

        get_deck_pdf = frappe.db.get_value("File",{"attached_to_doctype":"Deck Review","attached_to_name":doc_name},["file_url"])
        if get_deck_pdf:
            pdf_url = get_domain_name() + get_deck_pdf
        else:
            pdf_url = ""
        return {"status":True,"deck_pdf_url":pdf_url}    
    except Exception as e:  
        return {"status":False,"message":e}


@frappe.whitelist()
def get_deck_pdf(deck_id):
    try:
        pdf_url = ""
        doctype ="Deck Review"
        name = deck_id
        print_format = "Pitch Deck Report"
        execute(doctype,name,print_format)

        get_deck_details = frappe.get_doc("Deck Review",deck_id)
        
        get_file_list = frappe.db.get_all("File",{"attached_to_doctype":"Deck Review","attached_to_name":get_deck_details.name},["*"])
        for file in get_file_list:
            file_name = file.file_name
            if "Deck-Review" ==  file_name.split("-", 1)[0] + "-" + file_name.split("-", 2)[1]:
                pdf_url = get_domain_name() + file.file_url
            else:
                pdf_url = ""
            return {"status":True,"deck_pdf":pdf_url}
    except Exception as e:
        return {"status":False,"message":e}












# @frappe.whitelist()
# def get_recommended_startups():
#     try:
#         user_last_deck = []
#         image_url = ""
#         get_decks = frappe.db.get_all("Deck Review",{"docstatus":"Approved"},["*"],order_by="idx asc")
#         for deck in get_decks:
#             user_deck = {
#                 "id": deck.name,
#                 "name": deck.name,
#                 "user": deck.user_idemail or "",
#                 "deal_name":deck.deal_name or "",
#                 "slide_details":[],
#                 "overall_rating": "(100%): " + deck.overall_rating or "",
#                 "team_exp": deck.team_experience or "",
#                 "market_potential": deck.market_potential or "",
#                 "flow_and_clarity": deck.flow_and_clarity or "",
#                 "most_promising_aspects": deck.most_promising_aspects or "",
#                 "areas_for_improvement": deck.areas_for_improvement or "",
#                 "recommendations": deck.recommendations or ""
#             }

#             slide_images = frappe.db.get_all("Deck Slides", filters={"parent": deck.name}, fields=["slide_image"], order_by="idx asc")
#             slide_data_response = frappe.db.get_all("Deck LLM Response", filters={"parent": deck.name}, fields=["slide_no", "title", "feedback","suggestion"], order_by="idx asc")
#             for slide_img, slide_data in zip(slide_images, slide_data_response):
#                 slide_image = slide_img.slide_image
#                 if slide_image:
#                     image_url = get_domain_name() + slide_img.slide_image
#                 else:
#                     image_url = ""
#                 user_deck["slide_details"].append({
#                     "slide_no": slide_data.slide_no,
#                     "slide_image": image_url,
#                     "title": slide_data.title,
#                     "feedback":slide_data.feedback,
#                     "suggestion": slide_data.suggestion
#                 })
#             user_last_deck.append(user_deck)  
#         return {"status":True,"user_last_deck":user_last_deck} 
#     except Exception as e:
#         return {"status":False,"message":e}