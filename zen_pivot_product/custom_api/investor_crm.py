import frappe
from frappe.utils import now, getdate, today, format_date,format_time


@frappe.whitelist()
def get_recommended_investors():
    try:
        investor_crm = frappe.db.get_all("Investor CRM",{"disabled":0,"crm_shortlisted_delete":0},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":investor.name,
            "name":investor.name,
            "deck_id":investor.deck_id or "",
            "deal_name":investor.deal_name or "",
            "status":investor.crm_status or "",
            "applied_date":format_date(investor.applied_date) or "",
            "source_of_deal":investor.source_of_deal or "",
            "sector":investor.sector or "",
            "pitch_deck_link":investor.pitch_deck_link or "",
            "one_page_link":investor.one_page_link or "",
            "revenue":investor.revenue or "",
            "format_revenue":"{:,.0f}".format(investor.revenue) or "",
            "burn":investor.burn or "",
            "format_burn":"{:,.0f}".format(investor.burn) or "",
            "ask":investor.ask or "",
            }
            for investor in investor_crm
        ]
        return {"status":True,"investor_crm":crm_list}
    except Exception as e:
        return {"status":False,"message":e}


@frappe.whitelist()
def get_investor_crm_status_wise():
    try:
        investor_crm = {
            "deal":get_deal_crm(),
            "contacted":get_contacted_crm(),
            "evaluating":get_evaluating_crm(),
            "diligence":get_diligence_crm(),
            "investment_committee":get_investment_committee_crm(),
            "invested":get_invested_crm()
        }
        return {"status":True,"investors_board":investor_crm}     
    except Exception as e:
        return {"status":False,"message":e}

def get_deal_crm():
    try:
        investor_crm = frappe.db.get_all("Investor CRM",{"disabled":0,"crm_shortlisted_delete":0,"crm_status":"Deal"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":investor.name,
            "name":investor.name,
            "deck_id":investor.deck_id or "",
            "deal_name":investor.deal_name or "",
            "status":investor.crm_status or "",
            "applied_date":format_date(investor.applied_date) or "",
            "source_of_deal":investor.source_of_deal or "",
            "sector":investor.sector or "",
            "pitch_deck_link":investor.pitch_deck_link or "",
            "one_page_link":investor.one_page_link or "",
            "revenue":investor.revenue or "",
            "format_revenue":"{:,.0f}".format(investor.revenue) or "",
            "burn":investor.burn or "",
            "format_burn":"{:,.0f}".format(investor.burn) or "",
            "ask":investor.ask or "",
            }
            for investor in investor_crm
        ]
        return crm_list
    except Exception as e:
        return e

def get_contacted_crm():
    try:
        investor_crm = frappe.db.get_all("Investor CRM",{"disabled":0,"crm_shortlisted_delete":0,"crm_status":"Contacted"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":investor.name,
            "name":investor.name,
            "deck_id":investor.deck_id or "",
            "deal_name":investor.deal_name or "",
            "status":investor.crm_status or "",
            "applied_date":format_date(investor.applied_date) or "",
            "source_of_deal":investor.source_of_deal or "",
            "sector":investor.sector or "",
            "pitch_deck_link":investor.pitch_deck_link or "",
            "one_page_link":investor.one_page_link or "",
            "revenue":investor.revenue or "",
            "format_revenue":"{:,.0f}".format(investor.revenue) or "",
            "burn":investor.burn or "",
            "format_burn":"{:,.0f}".format(investor.burn) or "",
            "ask":investor.ask or "",
            }
            for investor in investor_crm
        ]
        return crm_list
    except Exception as e:
        return e

def get_evaluating_crm():
    try:
        investor_crm = frappe.db.get_all("Investor CRM",{"disabled":0,"crm_shortlisted_delete":0,"crm_status":"Evaluating"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":investor.name,
            "name":investor.name,
            "deck_id":investor.deck_id or "",
            "deal_name":investor.deal_name or "",
            "status":investor.crm_status or "",
            "applied_date":format_date(investor.applied_date) or "",
            "source_of_deal":investor.source_of_deal or "",
            "sector":investor.sector or "",
            "pitch_deck_link":investor.pitch_deck_link or "",
            "one_page_link":investor.one_page_link or "",
            "revenue":investor.revenue or "",
            "format_revenue":"{:,.0f}".format(investor.revenue) or "",
            "burn":investor.burn or "",
            "format_burn":"{:,.0f}".format(investor.burn) or "",
            "ask":investor.ask or "",
            }
            for investor in investor_crm
        ]
        return crm_list
    except Exception as e:
        return e    

def get_diligence_crm():
    try:
        investor_crm = frappe.db.get_all("Investor CRM",{"disabled":0,"crm_shortlisted_delete":0,"crm_status":"Diligence"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":investor.name,
            "name":investor.name,
            "deck_id":investor.deck_id or "",
            "deal_name":investor.deal_name or "",
            "status":investor.crm_status or "",
            "applied_date":format_date(investor.applied_date) or "",
            "source_of_deal":investor.source_of_deal or "",
            "sector":investor.sector or "",
            "pitch_deck_link":investor.pitch_deck_link or "",
            "one_page_link":investor.one_page_link or "",
            "revenue":investor.revenue or "",
            "format_revenue":"{:,.0f}".format(investor.revenue) or "",
            "burn":investor.burn or "",
            "format_burn":"{:,.0f}".format(investor.burn) or "",
            "ask":investor.ask or "",
            }
            for investor in investor_crm
        ]
        return crm_list
    except Exception as e:
        return e 

def get_investment_committee_crm():
    try:
        investor_crm = frappe.db.get_all("Investor CRM",{"disabled":0,"crm_shortlisted_delete":0,"crm_status":"Investment Committee"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":investor.name,
            "name":investor.name,
            "deck_id":investor.deck_id or "",
            "deal_name":investor.deal_name or "",
            "status":investor.crm_status or "",
            "applied_date":format_date(investor.applied_date) or "",
            "source_of_deal":investor.source_of_deal or "",
            "sector":investor.sector or "",
            "pitch_deck_link":investor.pitch_deck_link or "",
            "one_page_link":investor.one_page_link or "",
            "revenue":investor.revenue or "",
            "format_revenue":"{:,.0f}".format(investor.revenue) or "",
            "burn":investor.burn or "",
            "format_burn":"{:,.0f}".format(investor.burn) or "",
            "ask":investor.ask or "",
            }
            for investor in investor_crm
        ]
        return crm_list
    except Exception as e:
        return e

def get_invested_crm():
    try:
        investor_crm = frappe.db.get_all("Investor CRM",{"disabled":0,"crm_shortlisted_delete":0,"crm_status":"Invested"},["*"], order_by='idx ASC')
        crm_list = [
            {
            "id":investor.name,
            "name":investor.name,
            "deck_id":investor.deck_id or "",
            "deal_name":investor.deal_name or "",
            "status":investor.crm_status or "",
            "applied_date":format_date(investor.applied_date) or "",
            "source_of_deal":investor.source_of_deal or "",
            "sector":investor.sector or "",
            "pitch_deck_link":investor.pitch_deck_link or "",
            "one_page_link":investor.one_page_link or "",
            "revenue":investor.revenue or "",
            "format_revenue":"{:,.0f}".format(investor.revenue) or "",
            "burn":investor.burn or "",
            "format_burn":"{:,.0f}".format(investor.burn) or "",
            "ask":investor.ask or "",
            }
            for investor in investor_crm
        ]
        return crm_list
    except Exception as e:
        return e          


@frappe.whitelist()
def crm_status_move(user_name,crm_id,status):
    try:
        investor_crm = frappe.get_doc("Investor CRM",crm_id)
        investor_crm.update({"crm_status": status})
        investor_crm.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Investor CRM",investor_crm.name,'owner',user_name)
        return {"status": True, "message": "Deal status updated successfully."}
    except frappe.exceptions.DoesNotExistError:
        return {"status": False, "message": f"Investor CRM with ID {crm_id} does not exist."}    
    except Exception as e:
        return {"status":False,"message":e}
 
    
@frappe.whitelist()
def delete_crm(user_name,crm_id,delete):
    try:
        get_investor_crm = frappe.get_doc("Investor CRM",crm_id)
        get_investor_crm.crm_shortlisted_delete = delete
        get_investor_crm.crm_status = ""
        get_investor_crm.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Investor CRM",get_investor_crm.name,'owner',user_name)
        return {"status":True,"message":"CRM Deleted"}
    except Exception as e:
        return {"status":True,"message":e}

@frappe.whitelist()
def make_recommended_investor_shortlist(user_name,crm_id,status):
    try:
        get_investor_crm = frappe.get_doc("Investor CRM",crm_id)
        get_investor_crm.crm_status = status
        get_investor_crm.disabled = 0
        get_investor_crm.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Investor CRM",get_investor_crm.name,'owner',user_name)
        return{"status":True,"message":"CRM Shortlisted"}
    except Exception as e:
        return {"status":False,"message":e}

@frappe.whitelist()
def create_investor_crm(user,deal_name,pitch_deck_link,one_page_link,source_of_deal,revenue,burn,notes,ask,sector):
    try:
        status = ""
        message = ""
        crm_list = []

        if frappe.db.exists("User",user):
            new_investor_crm = frappe.new_doc("Investor CRM")
            new_investor_crm.deal_name = deal_name
            new_investor_crm.crm_status = "Deal"
            new_investor_crm.applied_date = today()
            new_investor_crm.source_of_deal = source_of_deal
            new_investor_crm.sector = sector
            new_investor_crm.pitch_deck_link = pitch_deck_link
            new_investor_crm.one_page_link = one_page_link
            new_investor_crm.revenue = revenue
            new_investor_crm.burn = burn
            new_investor_crm.notes = notes
            new_investor_crm.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Vault",new_investor_crm.name,'owner',user)

            status = True
            message = "Investor CRM Created Successfully"
            get_latest_crm = frappe.get_doc("Investor CRM",new_investor_crm.name)
            investor_crm = {
                "id":get_latest_crm.name,
                "name":get_latest_crm.name,
                "deal_name":get_latest_crm.deal_name or "",
                "status":get_latest_crm.crm_status or "",
                "applied_date":format_date(get_latest_crm.applied_date) or "",
                "source_of_deal":get_latest_crm.source_of_deal or "",
                "sector":get_latest_crm.sector or "",
                "pitch_deck_link":get_latest_crm.pitch_deck_link or "",
                "one_page_link":get_latest_crm.one_page_link or "",
                "revenue":get_latest_crm.revenue or "",
                "format_revenue":"{:,.0f}".format(get_latest_crm.revenue) or "",
                "burn":get_latest_crm.burn or "",
                "format_burn":"{:,.0f}".format(get_latest_crm.burn) or "",
                "ask":get_latest_crm.ask or "",
            }
            crm_list.append(investor_crm)
            status = True
            message = ""
        else:
            status = False
            message = "User not Found"
        return {"status":status,"message":message,"investor_crm":crm_list}
    except Exception as e:
        return {"status":False,"message":e}