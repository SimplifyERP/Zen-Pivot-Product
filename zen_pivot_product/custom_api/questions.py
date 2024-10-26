import frappe

@frappe.whitelist()
def overall_get_questions():
    try:
        question_masters = []
        questions = frappe.db.get_all("Questions Master",{'disabled':0},["*"],order_by='idx ASC')
        for question in questions:
            questions_list = {
                "id":question.name,
                "name":question.name,
                "risk_type":question.risk_type or "",
                "question":question.question or "",
                "question_type":question.question_type or "",
                "fill_the_blanks_type":question.fill_the_blanks_type or "",
                "choices_type":question.choices_type or "",
                "table":[],
                "option_1":question.option_1 or "",
                "option_2":question.option_2 or "",
                "option_3":question.option_3 or "",
                "option_4":question.option_4 or "",
                "option_5":question.option_5 or "",
                "option_6":question.option_6 or "",
            }
            get_table_details = frappe.db.get_all("Questions Type Table",{'parent':question.name},["*"],order_by='idx ASC')
            for table in get_table_details: 
                questions_list["table"].append({
                    "table_heading":table.table_heading,
                })
            question_masters.append(questions_list)
        return {"status":True,"message":question_masters}
    except Exception as e:
        return {"status":False,"message":e}
    

@frappe.whitelist()
def get_questions_flow():
    try:
        questions_flow = frappe.db.get_all("Questions Flow",{"disabled":0},["*"],order_by='idx ASC')
        for questions in questions_flow:
            # get_questions = frappe.get_doc()
            question_flow_list = {
                "id":questions.name,
                "name":questions.name
            }
    except Exception as e:
        return {"status":False,"message":e}