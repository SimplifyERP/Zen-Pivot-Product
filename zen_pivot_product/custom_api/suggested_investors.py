import frappe
import html2text
from deck_review.custom import get_domain_name


@frappe.whitelist()
def get_suggested_investors(deck_id):
    try:
        image_url = ""

        get_deck = frappe.get_doc("Deck Review", deck_id)
        matching_investors = []
        investor_data = []
        
        # Iterate through each matched industry in the deck
        for deck in get_deck.matched_industry:
            # SQL query to get matching investors, with limit, ascending order, and disabled condition
            investors = frappe.db.sql(""" SELECT DISTINCT investor.parent FROM `tabInvestor Database` AS investor_db JOIN `tabIndustry Child` AS investor 
                ON investor.parent = investor_db.name WHERE investor.industry = %s AND investor_db.disabled = 0 ORDER BY investor.parent ASC LIMIT 30
                """, (deck.industry,), as_dict=True)

            for investor in investors:
                investor_doc = frappe.get_doc("Investor Database", investor['parent'])

                # Format investor data
                formatted_description = html2text.html2text(investor_doc.description or "").strip()
                get_country = frappe.db.get_all("Country Child", {'parent': investor_doc.name}, ["country"], order_by='idx ASC')
                get_funding_stages = frappe.db.get_all("Stage of Funding Child", {'parent': investor_doc.name}, ["funding_stages"], order_by='idx ASC')
                get_other_locations = frappe.db.get_all("Other Locations", {'parent': investor_doc.name}, ["other_locations"], order_by='idx ASC')
                get_limited_partners = frappe.db.get_all("Limited Partners Child", {'parent': investor_doc.name}, ["limited_partners"], order_by='idx ASC')
                get_industry = frappe.db.get_all("Industry Child", {'parent': investor_doc.name}, ["industry"], order_by='idx ASC')

                # Handling the image URL
                if investor_doc.company_image:
                    image_url = get_domain_name() + investor_doc.company_image
                else:
                    image_url = ""

                # Building investor dictionary
                investor_db = {
                    "id": investor_doc.name,
                    "name": investor_doc.name,
                    "image": image_url,
                    "investor_name": investor_doc.investor_name or "",
                    "investor_type": investor_doc.investor_type__firm_type_ or "",
                    "email": investor_doc.email or "",
                    "telephone": investor_doc.telephone or "",
                    "fax": investor_doc.fax or "",
                    "city": investor_doc.city or "",
                    "address": investor_doc.investor_address or "",
                    "zip_code": investor_doc.zip_code or "",
                    "website": investor_doc.website or "",
                    "in_india_since": investor_doc.in_india_since or "",
                    "management": investor_doc.management or "",
                    "linkedin": investor_doc.linkedin or "",
                    "focus_and_capital_source": investor_doc.focus_and_capital_source or "",   
                    "assets_under_managementus": investor_doc.assets_under_managementus or "",
                    "dry_powderus": investor_doc.dry_powderus or "",
                    "additional_info": investor_doc.additional_info or "",
                    "number_of_funds": investor_doc.number_of_funds or "",
                    "description": formatted_description or "",
                    "country_wise": get_country or [],
                    "funding_stages": get_funding_stages or [],
                    "other_location": get_other_locations or [],
                    "limited_partners": get_limited_partners or [],
                    "industryexisting_investments": get_industry or [],
                    "portfolio": []
                }

                # Retrieving and formatting portfolio data
                get_portfolio = frappe.db.get_all("Portfolio", {'parent': investor_doc.name}, ["company_name", "industry_name", "sector", "sub_sector", "deal_period", "amount_cr", "amount_m", "exit_status"], order_by='idx ASC')
                for portfolio in get_portfolio:
                    formatted_currency_m = "{:,.0f}".format(portfolio.amount_m) if portfolio.amount_m else ""
                    formatted_currency_cr = "{:,.0f}".format(portfolio.amount_cr) if portfolio.amount_cr else ""
                    investor_db["portfolio"].append({
                        "company_name": portfolio.company_name or "",
                        "industry_name": portfolio.industry_name or "",
                        "sector_wise": portfolio.sector or "",
                        "sub_sector": portfolio.sub_sector or "",
                        "deal_period": portfolio.deal_period or "",
                        "format_amount_cr": formatted_currency_cr,
                        "amount_cr": portfolio.amount_cr or "",
                        "format_amount_m": formatted_currency_m,
                        "amount_m": portfolio.amount_m or "",
                        "exit_status": portfolio.exit_status or "" 
                    })
                investor_data.append(investor_db)            
        return {"status": True, "message": investor_data}
    
    except Exception as e:
        return {"status": False, "message": str(e)}
