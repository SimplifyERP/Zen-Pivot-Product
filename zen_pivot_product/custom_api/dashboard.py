import frappe
from deck_review.custom import get_domain_name
import html2text
from frappe.exceptions import DoesNotExistError


@frappe.whitelist()
def get_lastest_deck(user_name):
    try:
        deck_status = ""
        deck_response = ""
        slide_image_list = []
        summary_details_list = []
        user_last_deck = []

        try:
            get_deck = frappe.db.get_value("Deck Review",{"owner": user_name},["name"],order_by="creation desc")
            get_deck_list = frappe.get_doc("Deck Review",get_deck)
        except DoesNotExistError:
            get_deck = None 

        if get_deck: 
            if get_deck_list.not_a_pitch_deck == 0:
                deck_response = get_deck_list.no_deck_text or ""
                deck_status = False
                slide_images = frappe.db.get_all("Deck Slides", filters={"parent": get_deck}, fields=["slide_image"], order_by="idx asc")
                slide_data_response = frappe.db.get_all("Deck LLM Response", filters={"parent": get_deck}, fields=["slide_no", "title", "feedback","suggestion"], order_by="idx asc")
                for slide_img, slide_data in zip(slide_images, slide_data_response):
                    image_url = get_domain_name() + slide_img.slide_image

                    llm_response = {
                        "slide_image": image_url,
                        "slide_no": slide_data.slide_no or "",
                        "title": slide_data.title or "",
                        "feedback":slide_data.feedback or "",
                        "suggestion": slide_data.suggestion or ""
                    }
                    slide_image_list.append(llm_response)

                summary_details = {
                    "overall_rating": ("(100%): " + get_deck_list.overall_rating) or "",
                    "team_exp": get_deck_list.team_experience or "",
                    "market_potential": get_deck_list.market_potential or "",
                    "flow_and_clarity": get_deck_list.product_market_fit or "",
                    "most_promising_aspects": get_deck_list.most_promising_aspects or "",
                    "areas_for_improvement": get_deck_list.areas_for_improvement or "",
                    "recommendations": get_deck_list.recommendations or ""
                }

                summary_details_list.append(summary_details)    

                user_last_deck = {
                    "deck_details": {
                        "id": get_deck_list.name,
                        "name": get_deck_list.name,
                        "user": get_deck_list.user_idemail,
                        "deck_name":get_deck_list.deck_name
                    },
                    "slide_details": slide_image_list,
                    "summary_details": summary_details
                }
            
            else:
                deck_response = get_deck_list.no_deck_text or ""
                deck_status = True
                summary_details_list = []    

            services = get_our_services(user_name)
        else:
            services = get_our_services(user_name)  
            
        return {"status":True,"deck_status":deck_status,"deck_response":deck_response,"user_last_deck":user_last_deck,"our_services":services} 
    except Exception as e:
        return {"status":False,"message":e}


def get_our_services(user_name):
    service_list = []
    get_customer_group = frappe.db.get_value("Customer",{"custom_user":user_name},["customer_group"])
    if get_customer_group:
        services = frappe.db.get_all("Our Services",filters={"disabled":0,"customer_group": get_customer_group},fields=["*"],order_by="name asc",limit=3)
        for service in services:
            formatted_description = html2text.html2text(service.description or "").strip()
            formated_currency = "{:,.0f}".format(service.service_price)
            service_list.append({
                "id": service.name,
                "name": service.name or "",
                "service_name":service.service_name,
                "service_price":service.service_price or "",
                "pricing_format":formated_currency or "",
                "customer_group": service.customer_group or "",
                "description": formatted_description or ""
            })
    return service_list
      