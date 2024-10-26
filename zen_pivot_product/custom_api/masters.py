import frappe

@frappe.whitelist()
def get_masters_data():
    try:
        masters_data = {
            "customer_group":get_customer_group(),
            "firm_type":get_firm_type(),
            "state":get_state_list(),
            "city":get_city(),
            "country":get_country(),
            "limited_partners":get_limited_partners(),
            "other_locations":get_other_locations(),
            "focus_and_capital_source":get_focus_and_capital_source(),
            "sub_sector":get_sub_sector(),
            "funding_stages":get_funding_stages(),
            "crm_status_startup":get_crm_status_startup_list(),
            "ticket_type":get_ticket_type()
        }
        return {"status":True,"master_data":masters_data}
    except Exception as e:
        return {"status":False,"message":e}    


def get_customer_group():
    try:
        customer_group = frappe.db.get_all("Customer Group",{"custom_deck_user_type":1},["name"])
        return customer_group
    except Exception as e:
        return {"status":False,"message":e}
    
def get_firm_type():
    try:
        firm_type = frappe.db.get_all("Firm Type",{"disabled":1},["name"])
        return firm_type
    except Exception as e:
        return {"status":False,"message":e}

def get_country():
    try:
        country = frappe.db.get_all("Country",["name"])
        return country
    except Exception as e:
        return {"status":False,"message":e}   

def get_limited_partners():
    try:
        limited_partners = frappe.db.get_all("Limited Partners",{"disabled":0},["name"])
        return limited_partners
    except Exception as e:
        return {"status":False,"message":e}   

def get_other_locations():
    try:
        get_location = frappe.db.get_all("Location",["name"])
        return get_location
    except Exception as e:
        return {"status":False,"message":e}
    
def get_city():
    try:
        city = frappe.db.get_all("City",{"disabled":0},["name"])
        return city
    except Exception as e:
        return {"status":False,"message":e}

def get_focus_and_capital_source():
    try:
        focus_and_capital_source = frappe.db.get_all("Focus and Captial Source",{"disabled":0},["name"])
        return focus_and_capital_source
    except Exception as e:
        return {"status":False,"message":e}

def get_sub_sector():
    try:
        sub_sector = frappe.db.get_all("Sub Sector",{"disabled":0},["name"])
        return sub_sector
    except Exception as e:
        return {"status":False,"message":e}

def get_funding_stages():
    try:
        funding_stages = frappe.db.get_all("Funding Stages",{"disabled":0},["name"])
        return funding_stages
    except Exception as e:
        return {"status":False,"message":e}

def get_state_list():
    try:
        state = frappe.db.get_all("State List",{"disabled":0},["name"])
        return state
    except Exception as e:
        return {"status":False,"message":e}
    
def get_ticket_type():
    try:
        ticket_type = frappe.db.get_all("HD Ticket Type",["name"])
        return ticket_type
    except Exception as e:
        return {"status":False,"message":e}

def get_crm_status_startup_list():
    try:
        crm_status_list = []
        crm_status = ["Shortlisted","To be Contacted","Contacted","Pitched","Diligence","Term Sheet","Negotiating","Successfully Closed","Rejected"]
        for crm in crm_status:
            crm_status_startup = {
                "crm_status":crm
                }
            crm_status_list.append(crm_status_startup)
        return crm_status_list
    except Exception as e:
        return {"status":False,"message":e}

