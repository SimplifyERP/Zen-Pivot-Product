import frappe
import html2text
from deck_review.custom import get_domain_name
from datetime import datetime



@frappe.whitelist()
def get_investor_db():
    try:
        investor_status = ""
        get_investor = frappe.db.get_all("Investor Database",filters={"disabled":0,"company_image": ["is", "set"]},fields=["*"],order_by='idx ASC',limit=30)
        investor_data = []
        for investor in get_investor:
            if frappe.db.exists("Investor Shortlist",{"investor":investor.name}):
                investor_status = "Shortlist"
            else:
                investor_status = ""    
            formatted_description = html2text.html2text(investor.description or "").strip()
            get_funding_stages = frappe.db.get_all("Stage of Funding Child",{'parent':investor.name},["funding_stages"],order_by='idx ASC')
            get_other_locations = frappe.db.get_all("Other Locations",{'parent':investor.name},["other_locations"],order_by='idx ASC')
            get_industry = frappe.db.get_all("Industry Child",{'parent':investor.name},["industry"],order_by='idx ASC')
            investor_db = {
                "id":investor.name,
                "name":investor.name,
                "image":investor.company_image or "",
                "investor_name":investor.investor_name or "",
                "country_wise":investor.country or "",
                "investor_type":investor.investor_type__firm_type_ or "",
                "investor_status":investor_status,
                "email":investor.email or "",
                "telephone":investor.telephone or "",
                "fax":investor.fax or "",
                "city":investor.city or "",
                "address_line1":investor.address_line_1 or "",
                "address_line2":investor.address_line_2 or "",
                "zip_code":investor.zip_code or "",
                "website":investor.website or "",
                "in_india_since":investor.in_india_since or "",
                "management":investor.management or "",
                "linkedin":investor.linkedin or "",
                "focus_and_capital_source":investor.focus_and_capital_source or "",   
                "assets_under_managementus":investor.assets_under_managementus or "",
                "already_invested_managementus":investor.already_invested_managementus or "",
                "dry_powderus":investor.dry_powderus or "",
                "additional_info":investor.additional_info or "",
                "limited_partners":investor.limited_partners or "",
                "number_of_funds":investor.number_of_funds or "",
                "description": formatted_description or "",
                "funding_stages":get_funding_stages or [],
                "other_location":get_other_locations or [],
                "industryexisting_investments":get_industry or [],
                "portfolio":[]
            }
            get_portfolio = frappe.db.get_all("Portfolio",{'parent':investor.name},["company_name","industry_name","sector","sub_sector","deal_period","amount_cr","amount_m","exit_status"],order_by='idx ASC')
            for portfolio in get_portfolio:
                formated_currency_m = "{:,.0f}".format(portfolio.amount_m)
                formated_currency_cr = "{:,.0f}".format(portfolio.amount_cr)
                investor_db["portfolio"].append({
					"company_name":portfolio.company_name or "",
                    "industry_name":portfolio.industry_name or "",
                    "sector_wise":portfolio.sector or "",
                    "sub_sector":portfolio.sub_sector or "",
                    "deal_period":portfolio.deal_period or "",
                    "format_amount_cr":formated_currency_cr,
                    "amount_cr": portfolio.amount_cr or "",
                    "format_amount_m":formated_currency_m,
                    "amount_m":portfolio.amount_m or "",
                    "exit_status":portfolio.exit_status or "" 
				})
            investor_data.append(investor_db)
        return {"status": True,"investor_db": investor_data}
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def get_investor_db_particular(investor_id):
    try:
        investor_data = []
        get_investors_db = frappe.get_doc("Investor Database",investor_id)
        formatted_description = html2text.html2text(get_investors_db.description or "").strip()
        get_funding_stages = frappe.db.get_all("Stage of Funding Child",{'parent':get_investors_db.name},["funding_stages"],order_by='idx ASC')
        get_other_locations = frappe.db.get_all("Other Locations",{'parent':get_investors_db.name},["other_locations"],order_by='idx ASC')
        get_industry = frappe.db.get_all("Industry Child",{'parent':get_investors_db.name},["industry"],order_by='idx ASC')
        investor_db = {
            "id":get_investors_db.name,
            "name":get_investors_db.name,
            "image":get_investors_db.company_image or "",
            "investor_name":get_investors_db.investor_name or "",
            "country_wise":get_investors_db.country or "",
            "investor_type":get_investors_db.investor_type__firm_type_ or "",
            "email":get_investors_db.email or "",
            "telephone":get_investors_db.telephone or "",
            "fax":get_investors_db.fax or "",
            "city":get_investors_db.city or "",
            "address_line1":get_investors_db.address_line_1 or "",
            "address_line2":get_investors_db.address_line_2 or "",
            "zip_code":get_investors_db.zip_code or "",
            "website":get_investors_db.website or "",
            "in_india_since":get_investors_db.in_india_since or "",
            "management":get_investors_db.management or "",
            "linkedin":get_investors_db.linkedin or "",
            "focus_and_capital_source":get_investors_db.focus_and_capital_source or "",
            "assets_under_managementus":get_investors_db.assets_under_managementus or "",
            "already_invested_managementus":get_investors_db.already_invested_managementus or "",
            "dry_powderus":get_investors_db.dry_powderus or "",
            "additional_info":get_investors_db.additional_info or "",
            "limited_partners":get_investors_db.limited_partners or "",
            "number_of_funds":get_investors_db.number_of_funds or "",
            "description": formatted_description or "",
            "funding_stages":get_funding_stages or [],
            "other_location":get_other_locations or [],
            "industryexisting_investments":get_industry or [],
            "portfolio":[]
        }
        get_portfolio = frappe.db.get_all("Portfolio",{'parent':get_investors_db.name},["company_name","industry_name","sector","sub_sector","deal_period","amount_cr","amount_m","exit_status"],order_by='idx ASC')
        for portfolio in get_portfolio:
            formated_currency_m = "{:,.0f}".format(portfolio.amount_m)
            formated_currency_cr = "{:,.0f}".format(portfolio.amount_cr)
            investor_db["portfolio"].append({
                "company_name":portfolio.company_name or "",
                "industry_name":portfolio.industry_name or "",
                "sector_wise":portfolio.sector or "",
                "sub_sector":portfolio.sub_sector or "",
                "deal_period":portfolio.deal_period or "",
                "format_amount_cr":formated_currency_cr,
                "amount_cr": portfolio.amount_cr or "",
                "format_amount_m":formated_currency_m,
                "amount_m":portfolio.amount_m or "",
                "exit_status":portfolio.exit_status or "" 
            })
        investor_data.append(investor_db)
        return {"status":True,"investor_db": investor_data} 

    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def make_investor_to_crm(investor_id,user_name):
    try:
        if not frappe.db.exists("Investor Shortlist",{'user':user_name,'investor':investor_id}): 
            new_investor_favourite = frappe.new_doc("Investor Shortlist")
            new_investor_favourite.user = user_name
            new_investor_favourite.investor = investor_id
            new_investor_favourite.investor_status = "Shortlisted"
            new_investor_favourite.move_to_board = 1
            new_investor_favourite.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Investor Shortlist",new_investor_favourite.name,'owner',user_name)
        else:
            get_favourites = frappe.db.get_value("Investor Shortlist",{'user':user_name,'investor':investor_id},['name'])
            get_investor_favourite = frappe.get_doc("Investor Shortlist",get_favourites)
            get_investor_favourite.move_to_board = 1
            get_investor_favourite.disabled = 0
            get_investor_favourite.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Investor Shortlist",get_investor_favourite.name,'owner',user_name)
        return {"status":True,"message":"Investor Shortlisted"}    
    except Exception as e:
        return {"status":False,"message":e}


@frappe.whitelist()
def get_investors_board(user_name):
    try:
        board_crm = {
            "shortlisted":get_shortlist_investor(user_name),
            "contacted":get_contacted_investor(user_name),
            "pitched":get_pitched_investor(user_name),
            "won":get_won_investor(user_name),
        }
        return {"status":True,"investors_board":board_crm}     
    except Exception as e:
        return {"status":False,"message":e}


def get_shortlist_investor(user_name):
    try:
        investor_data = []
        get_investor_favourite = frappe.db.get_all("Investor Shortlist",{"user":user_name,"investor_status":"Shortlisted","disabled":0,"move_to_board":1},["*"],order_by='idx ASC')
        for investors in get_investor_favourite:
            get_investors_db = frappe.get_doc("Investor Database",investors.investor)
            formatted_description = html2text.html2text(get_investors_db.description or "").strip()
            get_funding_stages = frappe.db.get_all("Stage of Funding Child",{'parent':get_investors_db.name},["funding_stages"],order_by='idx ASC')
            get_other_locations = frappe.db.get_all("Other Locations",{'parent':get_investors_db.name},["other_locations"],order_by='idx ASC')
            get_industry = frappe.db.get_all("Industry Child",{'parent':get_investors_db.name},["industry"],order_by='idx ASC')
            investor_db = {
                "id":get_investors_db.name,
                "name":get_investors_db.name,
                "investor_fav_id":investors.name,
                "investor_status":investors.investor_status,
                "contactd_date":investors.contacted_date or "",
                "image":get_investors_db.company_image or "",
                "investor_name":get_investors_db.investor_name or "",
                "country_wise":get_investors_db.country or "",
                "investor_type":get_investors_db.investor_type__firm_type_ or "",
                "email":get_investors_db.email or "",
                "telephone":get_investors_db.telephone or "",
                "fax":get_investors_db.fax or "",
                "city":get_investors_db.city or "",
                "address_line1":get_investors_db.address_line_1 or "",
                "address_line2":get_investors_db.address_line_2 or "",
                "zip_code":get_investors_db.zip_code or "",
                "website":get_investors_db.website or "",
                "in_india_since":get_investors_db.in_india_since or "",
                "management":get_investors_db.management or "",
                "linkedin":get_investors_db.linkedin or "",
                "focus_and_capital_source":get_investors_db.focus_and_capital_source or "",
                "assets_under_managementus":get_investors_db.assets_under_managementus or "",
                "already_invested_managementus":get_investors_db.already_invested_managementus or "",
                "dry_powderus":get_investors_db.dry_powderus or "",
                "additional_info":get_investors_db.additional_info or "",
                "limited_partners":get_investors_db.limited_partners or "",
                "number_of_funds":get_investors_db.number_of_funds or "",
                "description": formatted_description or "",
                "notes":investors.notes or "",
                "funding_stages":get_funding_stages or [],
                "other_location":get_other_locations or [],
                "industryexisting_investments":get_industry or [],
                "portfolio":[]
            }
            get_portfolio = frappe.db.get_all("Portfolio",{'parent':get_investors_db.name},["company_name","industry_name","sector","sub_sector","deal_period","amount_cr","amount_m","exit_status"],order_by='idx ASC')
            for portfolio in get_portfolio:
                formated_currency_m = "{:,.0f}".format(portfolio.amount_m)
                formated_currency_cr = "{:,.0f}".format(portfolio.amount_cr)
                investor_db["portfolio"].append({
					"company_name":portfolio.company_name or "",
                    "industry_name":portfolio.industry_name or "",
                    "sector_wise":portfolio.sector or "",
                    "sub_sector":portfolio.sub_sector or "",
                    "deal_period":portfolio.deal_period or "",
                    "format_amount_cr":formated_currency_cr,
                    "amount_cr": portfolio.amount_cr or "",
                    "format_amount_m":formated_currency_m,
                    "amount_m":portfolio.amount_m or "",
                    "exit_status":portfolio.exit_status or "" 
				})
            investor_data.append(investor_db)
        return investor_data  
    except Exception as e:
        return e

def get_contacted_investor(user_name):
    try:
        investor_data = []
        get_investor_favourite = frappe.db.get_all("Investor Shortlist",{"user":user_name,"investor_status":"Contacted","disabled":0,"move_to_board":1},["*"],order_by='idx ASC')
        for investors in get_investor_favourite:
            get_investors_db = frappe.get_doc("Investor Database",investors.investor)
            formatted_description = html2text.html2text(get_investors_db.description or "").strip()
            get_funding_stages = frappe.db.get_all("Stage of Funding Child",{'parent':get_investors_db.name},["funding_stages"],order_by='idx ASC')
            get_other_locations = frappe.db.get_all("Other Locations",{'parent':get_investors_db.name},["other_locations"],order_by='idx ASC')
            get_industry = frappe.db.get_all("Industry Child",{'parent':get_investors_db.name},["industry"],order_by='idx ASC')   
            investor_db = {
                "id":get_investors_db.name,
                "name":get_investors_db.name,
                "investor_fav_id":investors.name,
                "investor_status":investors.investor_status,
                "contactd_date":investors.contacted_date or "",
                "image":get_investors_db.company_image or "",
                "investor_name":get_investors_db.investor_name or "",
                "country_wise":get_investors_db.country or "",
                "investor_type":get_investors_db.investor_type__firm_type_ or "",
                "email":get_investors_db.email or "",
                "telephone":get_investors_db.telephone or "",
                "fax":get_investors_db.fax or "",
                "city":get_investors_db.city or "",
                "address_line1":get_investors_db.address_line_1 or "",
                "address_line2":get_investors_db.address_line_2 or "",
                "zip_code":get_investors_db.zip_code or "",
                "website":get_investors_db.website or "",
                "in_india_since":get_investors_db.in_india_since or "",
                "management":get_investors_db.management or "",
                "linkedin":get_investors_db.linkedin or "",
                "focus_and_capital_source":get_investors_db.focus_and_capital_source or "",
                "assets_under_managementus":get_investors_db.assets_under_managementus or "",
                "already_invested_managementus":get_investors_db.already_invested_managementus or "",
                "dry_powderus":get_investors_db.dry_powderus or "",
                "additional_info":get_investors_db.additional_info or "",
                "limited_partners":get_investors_db.limited_partners or "",
                "number_of_funds":get_investors_db.number_of_funds or "",
                "description": formatted_description or "",
                "notes":investors.notes or "",
                "funding_stages":get_funding_stages or [],
                "other_location":get_other_locations or [],
                "industryexisting_investments":get_industry or [],
                "portfolio":[]
            }
            get_portfolio = frappe.db.get_all("Portfolio",{'parent':get_investors_db.name},["company_name","industry_name","sector","sub_sector","deal_period","amount_cr","amount_m","exit_status"],order_by='idx ASC')
            for portfolio in get_portfolio:
                formated_currency_m = "{:,.0f}".format(portfolio.amount_m)
                formated_currency_cr = "{:,.0f}".format(portfolio.amount_cr)
                investor_db["portfolio"].append({
					"company_name":portfolio.company_name or "",
                    "industry_name":portfolio.industry_name or "",
                    "sector_wise":portfolio.sector or "",
                    "sub_sector":portfolio.sub_sector or "",
                    "deal_period":portfolio.deal_period or "",
                    "format_amount_cr":formated_currency_cr,
                    "amount_cr": portfolio.amount_cr or "",
                    "format_amount_m":formated_currency_m,
                    "amount_m":portfolio.amount_m or "",
                    "exit_status":portfolio.exit_status or "" 
				})
            investor_data.append(investor_db)
        return investor_data  
    except Exception as e:
        return e    

def get_pitched_investor(user_name):
    try:
        investor_data = []
        get_investor_favourite = frappe.db.get_all("Investor Shortlist",{"user":user_name,"investor_status":"Pitched","disabled":0,"move_to_board":1},["*"],order_by='idx ASC')
        for investors in get_investor_favourite:
            get_investors_db = frappe.get_doc("Investor Database",investors.investor)
            formatted_description = html2text.html2text(get_investors_db.description or "").strip()
            get_funding_stages = frappe.db.get_all("Stage of Funding Child",{'parent':get_investors_db.name},["funding_stages"],order_by='idx ASC')
            get_other_locations = frappe.db.get_all("Other Locations",{'parent':get_investors_db.name},["other_locations"],order_by='idx ASC')
            get_industry = frappe.db.get_all("Industry Child",{'parent':get_investors_db.name},["industry"],order_by='idx ASC')
            investor_db = {
                "id":get_investors_db.name,
                "name":get_investors_db.name,
                "investor_fav_id":investors.name,
                "investor_status":investors.investor_status,
                "contactd_date":investors.contacted_date or "",
                "image":get_investors_db.company_image or "",
                "investor_name":get_investors_db.investor_name or "",
                "country_wise":get_investors_db.country or "",
                "investor_type":get_investors_db.investor_type__firm_type_ or "",
                "email":get_investors_db.email or "",
                "telephone":get_investors_db.telephone or "",
                "fax":get_investors_db.fax or "",
                "city":get_investors_db.city or "",
                "address_line1":get_investors_db.address_line_1 or "",
                "address_line2":get_investors_db.address_line_2 or "",
                "zip_code":get_investors_db.zip_code or "",
                "website":get_investors_db.website or "",
                "in_india_since":get_investors_db.in_india_since or "",
                "management":get_investors_db.management or "",
                "linkedin":get_investors_db.linkedin or "",
                "focus_and_capital_source":get_investors_db.focus_and_capital_source or "",
                "assets_under_managementus":get_investors_db.assets_under_managementus or "",
                "already_invested_managementus":get_investors_db.already_invested_managementus or "",
                "dry_powderus":get_investors_db.dry_powderus or "",
                "additional_info":get_investors_db.additional_info or "",
                "limited_partners":get_investors_db.limited_partners or "",
                "number_of_funds":get_investors_db.number_of_funds or "",
                "description": formatted_description or "",
                "notes":investors.notes or "",
                "funding_stages":get_funding_stages or [],
                "other_location":get_other_locations or [],
                "industryexisting_investments":get_industry or [],
                "portfolio":[]
            }
            get_portfolio = frappe.db.get_all("Portfolio",{'parent':get_investors_db.name},["company_name","industry_name","sector","sub_sector","deal_period","amount_cr","amount_m","exit_status"],order_by='idx ASC')
            for portfolio in get_portfolio:
                formated_currency_m = "{:,.0f}".format(portfolio.amount_m)
                formated_currency_cr = "{:,.0f}".format(portfolio.amount_cr)
                investor_db["portfolio"].append({
					"company_name":portfolio.company_name or "",
                    "industry_name":portfolio.industry_name or "",
                    "sector_wise":portfolio.sector or "",
                    "sub_sector":portfolio.sub_sector or "",
                    "deal_period":portfolio.deal_period or "",
                    "format_amount_cr":formated_currency_cr,
                    "amount_cr": portfolio.amount_cr or "",
                    "format_amount_m":formated_currency_m,
                    "amount_m":portfolio.amount_m or "",
                    "exit_status":portfolio.exit_status or "" 
				})
            investor_data.append(investor_db)
        return investor_data  
    except Exception as e:
        return e  

def get_won_investor(user_name):
    try:
        investor_data = []
        get_investor_favourite = frappe.db.get_all("Investor Shortlist",{"user":user_name,"investor_status":"Won","disabled":0,"move_to_board":1},["*"],order_by='idx ASC')
        for investors in get_investor_favourite:
            get_investors_db = frappe.get_doc("Investor Database",investors.investor)
            formatted_description = html2text.html2text(get_investors_db.description or "").strip()
            get_funding_stages = frappe.db.get_all("Stage of Funding Child",{'parent':get_investors_db.name},["funding_stages"],order_by='idx ASC')
            get_other_locations = frappe.db.get_all("Other Locations",{'parent':get_investors_db.name},["other_locations"],order_by='idx ASC')
            get_industry = frappe.db.get_all("Industry Child",{'parent':get_investors_db.name},["industry"],order_by='idx ASC') 
            investor_db = {
                "id":get_investors_db.name,
                "name":get_investors_db.name,
                "investor_fav_id":investors.name,
                "investor_status":investors.investor_status,
                "contactd_date":investors.contacted_date or "",
                "image":get_investors_db.company_image or "",
                "investor_name":get_investors_db.investor_name or "",
                "country_wise":get_investors_db.country or "",
                "investor_type":get_investors_db.investor_type__firm_type_ or "",
                "email":get_investors_db.email or "",
                "telephone":get_investors_db.telephone or "",
                "fax":get_investors_db.fax or "",
                "city":get_investors_db.city or "",
                "address_line1":get_investors_db.address_line_1 or "",
                "address_line2":get_investors_db.address_line_2 or "",
                "zip_code":get_investors_db.zip_code or "",
                "website":get_investors_db.website or "",
                "in_india_since":get_investors_db.in_india_since or "",
                "management":get_investors_db.management or "",
                "linkedin":get_investors_db.linkedin or "",
                "focus_and_capital_source":get_investors_db.focus_and_capital_source or "",
                "assets_under_managementus":get_investors_db.assets_under_managementus or "",
                "already_invested_managementus":get_investors_db.already_invested_managementus or "",
                "dry_powderus":get_investors_db.dry_powderus or "",
                "additional_info":get_investors_db.additional_info or "",
                "limited_partners":get_investors_db.limited_partners or "",
                "number_of_funds":get_investors_db.number_of_funds or "",
                "description": formatted_description or "",
                "notes":investors.notes or "",
                "funding_stages":get_funding_stages or [],
                "other_location":get_other_locations or [],
                "industryexisting_investments":get_industry or [],
                "portfolio":[]
            }
            get_portfolio = frappe.db.get_all("Portfolio",{'parent':get_investors_db.name},["company_name","industry_name","sector","sub_sector","deal_period","amount_cr","amount_m","exit_status"],order_by='idx ASC')
            for portfolio in get_portfolio:
                formated_currency_m = "{:,.0f}".format(portfolio.amount_m)
                formated_currency_cr = "{:,.0f}".format(portfolio.amount_cr)
                investor_db["portfolio"].append({
					"company_name":portfolio.company_name or "",
                    "industry_name":portfolio.industry_name or "",
                    "sector_wise":portfolio.sector or "",
                    "sub_sector":portfolio.sub_sector or "",
                    "deal_period":portfolio.deal_period or "",
                    "format_amount_cr":formated_currency_cr,
                    "amount_cr": portfolio.amount_cr or "",
                    "format_amount_m":formated_currency_m,
                    "amount_m":portfolio.amount_m or "",
                    "exit_status":portfolio.exit_status or "" 
				})
            investor_data.append(investor_db)
        return investor_data  
    except Exception as e:
        return e      

@frappe.whitelist()
def move_crm_status(user_name,investor_fav_id,moved_status):
    try:
        get_investor_fav = frappe.get_doc("Investor Shortlist",investor_fav_id)
        get_investor_fav.investor_status = moved_status
        get_investor_fav.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Investor Shortlist",get_investor_fav.name,'owner',user_name)
        return {"status":True,"message":"Status Moved"}
    except Exception as e:
        return {"status":False,"message":e}
    
@frappe.whitelist()
def edit_crm(user_name,investor_fav_id,contacted_date,notes):
    try:
        contaced_date_format = datetime.strptime(str(contacted_date), "%d-%m-%Y").date()
        get_shortlist_investor = frappe.get_doc("Investor Shortlist",investor_fav_id)
        get_shortlist_investor.contacted_date = contaced_date_format
        get_shortlist_investor.notes = notes
        get_shortlist_investor.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Investor Shortlist",get_shortlist_investor.name,'owner',user_name)
        return {"status":True,"message":"Notes Updated"}
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def delete_crm(user_name,investor_fav_id,delete):
    try:
        get_shortlist_investor = frappe.get_doc("Investor Shortlist",investor_fav_id)
        get_shortlist_investor.disabled = delete
        get_shortlist_investor.move_to_board = 0
        get_shortlist_investor.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Investor Shortlist",get_shortlist_investor.name,'owner',user_name)
        return {"status":True,"message":"Shortlist Investor Deleted"}
    except Exception as e:
        return {"status":False,"message":e}