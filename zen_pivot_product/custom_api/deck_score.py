import frappe
from deck_review.custom import get_domain_name


@frappe.whitelist()
def get_deck_score(deck_id):
    try:
        image_url = ""
        get_deck = frappe.get_doc("Deck Review",deck_id)
        user_deck = {
            "id": get_deck.name,
            "name": get_deck.name,
            "user": get_deck.user_idemail or "",
            "deal_name":get_deck.deal_name or "",
            "slide_details":[],
            "overall_rating": "(100%): " + get_deck.overall_rating or "",
            "team_exp": get_deck.team_experience or "",
            "market_potential": get_deck.market_potential or "",
            "flow_and_clarity": get_deck.flow_and_clarity or "",
            "most_promising_aspects": get_deck.most_promising_aspects or "",
            "areas_for_improvement": get_deck.areas_for_improvement or "",
            "recommendations": get_deck.recommendations or ""
        }
        slide_images = frappe.db.get_all("Deck Slides", filters={"parent": get_deck.name}, fields=["slide_image"], order_by="idx asc")
        slide_data_response = frappe.db.get_all("Deck LLM Response", filters={"parent": get_deck.name}, fields=["slide_no", "title", "feedback","suggestion"], order_by="idx asc")
        for slide_img, slide_data in zip(slide_images, slide_data_response):
            slide_image = slide_img.slide_image
            if slide_image:
                image_url = get_domain_name() + slide_img.slide_image
            else:
                image_url = ""
            user_deck["slide_details"].append({
                "slide_no": slide_data.slide_no,
                "slide_image": image_url,
                "title": slide_data.title,
                "feedback":slide_data.feedback,
                "suggestion": slide_data.suggestion
            })   
        return {"status":True,"deck_score":user_deck}  
    except Exception as e:
        return {"status":False,"message":e}