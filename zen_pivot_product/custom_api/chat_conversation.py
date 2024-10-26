import frappe
import html2text
from bs4 import BeautifulSoup
from openai import AzureOpenAI
import os
import json
from frappe.utils import now, getdate, today, format_date,format_time
import requests



""" List the Zen Chat Type """
@frappe.whitelist()
def get_chat_list(user_name,prompt_type,deck_id,type_of_chat):
    try:
        status = ""
        message = ""
        chat_list = []
        get_deck = frappe.db.get_value("Deck Review",{"name":deck_id,"user_idemail":user_name},["deck_text_extraction"])
        if get_deck:
            if type_of_chat:
                get_chat_list_questions = frappe.db.get_all("Zen Chat Questions",{"disabled":0,"name":type_of_chat},["*"], order_by="creation ASC")
            else:
                get_chat_list_questions = frappe.db.get_all("Zen Chat Questions",{"disabled":0},["*"], order_by="creation ASC")
            for chat_question in get_chat_list_questions:
                chat = {
                    "id":chat_question.name,
                    "name":chat_question.name,
                    "title":chat_question.chat_list_name,
                    "questions":[]
                }
                if prompt_type == "Discuss":
                    discuss_chat_question = frappe.db.get_all("Chat Type Questions",{"parentfield":"discuss_questions","parent":chat_question.name,"with_deck":1},["*"],order_by='idx ASC')
                    for discuss_chat in discuss_chat_question:
                        chat["questions"].append({
                            "question":discuss_chat.questions or ""
                        })
                        status = True
                        message = "success" 
                elif prompt_type == "Task":
                    discuss_chat_question = frappe.db.get_all("Chat Type Questions",{"parentfield":"task_questions","parent":chat_question.name,"with_deck":1},["*"],order_by='idx ASC')
                    for discuss_chat in discuss_chat_question:
                        chat["questions"].append({
                            "question":discuss_chat.questions or ""
                        })
                        status = True
                        message = "success"
                elif prompt_type == "Learn":
                    discuss_chat_question = frappe.db.get_all("Chat Type Questions",{"parentfield":"learn_questions","parent":chat_question.name,"with_deck":1},["*"],order_by='idx ASC')
                    for discuss_chat in discuss_chat_question:
                        chat["questions"].append({
                            "question":discuss_chat.questions or ""
                        })
                        status = True
                        message = "success"
                else:
                    status = False
                    message = "Type of chat is Invalid" 
                """ Append the chat dict in list """
                chat_list.append(chat)        
        elif deck_id == "general-001":
            if type_of_chat:
                get_chat_list_questions = frappe.db.get_all("Zen Chat Questions",{"disabled":0,"name":type_of_chat},["*"], order_by="creation ASC")
            else:
                get_chat_list_questions = frappe.db.get_all("Zen Chat Questions",{"disabled":0},["*"], order_by="creation ASC")
            for chat_question in get_chat_list_questions:
                chat = {
                    "id":chat_question.name,
                    "name":chat_question.name,
                    "title":chat_question.chat_list_name,
                    "questions":[]
                }
                if prompt_type == "Discuss":
                    discuss_chat_question = frappe.db.get_all("Chat Type Questions",{"parentfield":"discuss_questions","parent":chat_question.name,"without_deck":1},["*"],order_by='idx ASC')
                    for discuss_chat in discuss_chat_question:
                        chat["questions"].append({
                            "question":discuss_chat.questions or ""
                        })
                        status = True
                        message = "success" 
                elif prompt_type == "Task":
                    discuss_chat_question = frappe.db.get_all("Chat Type Questions",{"parentfield":"task_questions","parent":chat_question.name},["*"],order_by='idx ASC')
                    for discuss_chat in discuss_chat_question:
                        chat["questions"].append({
                            "question":discuss_chat.questions or ""
                        })
                        status = True
                        message = "success"
                elif prompt_type == "Learn":
                    discuss_chat_question = frappe.db.get_all("Chat Type Questions",{"parentfield":"learn_questions","parent":chat_question.name},["*"],order_by='idx ASC')
                    for discuss_chat in discuss_chat_question:
                        chat["questions"].append({
                            "question":discuss_chat.questions or ""
                        })
                        status = True
                        message = "success"
                else:
                    status = False
                    message = "Type of chat is Invalid"

                """ Append the chat dict in list """
                chat_list.append(chat)
        else:
            status = False
            message = "Deck ID is Invalid"     
        return {"status":status,"message":message,"chat_list":chat_list,"deck_list":get_user_upload_deck(user_name)}
    except Exception as e:
        return {"status":False,"message":e}

""" Get the Deck Documents user uploaded """
def get_user_upload_deck(user_name):
    user_deck_list = []
    try:
        user_deck_list.append(get_general_deck())
        get_deck = frappe.db.get_all("Deck Review",{"user_idemail":user_name},["name","deck_name"],order_by='idx ASC')
        for deck in get_deck:
            deck_list = {
                "id":deck.name,
                "name":deck.name,
                "deck_name":deck.deck_name or ""
            }
            user_deck_list.append(deck_list)
        return user_deck_list    
    except Exception as e:
        return user_deck_list 

""" General Deck List """
def get_general_deck():
    deck_list = {
        "id":"general-001",
        "name":"general-001",
        "deck_name":"General"
    }
    return deck_list
    
""" Processing the chat conversation set in comment doctype """
@frappe.whitelist()
def process_chat_conversation(user_name,deck_id,type_of_chat,prompt_type,user_prompt):
    try:
        chat = []
        status = ""
        message = ""
        extraction_prompt = frappe.db.get_value("Deck Review",{"name":deck_id,"user_idemail":user_name},["deck_text_extraction"])
        if extraction_prompt:
            get_extraction_prompt = extraction_prompt

            get_chat_prompts = frappe.get_doc("Zen Chat Questions",{"name":type_of_chat})
            if get_chat_prompts.discuss_chat == prompt_type:
                get_prompt = get_chat_prompts.discuss_chat_prompt
            elif get_chat_prompts.task_chat == prompt_type:  
                get_prompt = get_chat_prompts.task_chat_prompt
            elif get_chat_prompts.learn_chat == prompt_type:  
                get_prompt = get_chat_prompts.learn_chat_prompt  
        
            """ Create a log chat in comment doctype """
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": "Deck Review",
                "reference_name":deck_id,
                "custom_type_of_chat":type_of_chat,
                "content": user_prompt,
                "custom_user":1,
                "comment_email": frappe.session.user,
                "comment_by": "User"
            }).insert(ignore_permissions=True)
            frappe.db.commit()

            status = True
            message = "success"

            conversation_history = [  
                {"role": "system", "content":get_extraction_prompt},
                {"role": "system", "content":get_prompt},
                {"role": "user", "content":user_prompt}
            ]

        elif deck_id == "general-001":
            get_chat_prompts = frappe.get_doc("Zen Chat Questions",{"name":type_of_chat})
            if get_chat_prompts.discuss_chat == prompt_type:
                get_prompt = get_chat_prompts.discuss_chat_prompt
            elif get_chat_prompts.task_chat == prompt_type:  
                get_prompt = get_chat_prompts.task_chat_prompt
            elif get_chat_prompts.learn_chat == prompt_type:  
                get_prompt = get_chat_prompts.learn_chat_prompt  

            if not frappe.db.exists("General Chat",{"name":user_name}):
                new_user_chat = frappe.new_doc("General Chat")
                new_user_chat.user = user_name
                new_user_chat.general_chat_id = deck_id
                new_user_chat.type_of_chat = type_of_chat
                new_user_chat.prompt_type = prompt_type
                new_user_chat.save(ignore_permissions=True)
                frappe.db.set_value("General Chat",new_user_chat.name,'owner',user_name)

                """ Create a log chat in comment doctype """
                frappe.get_doc({
                    "doctype": "Comment",
                    "comment_type": "Comment",
                    "reference_doctype": "General Chat",
                    "reference_name":new_user_chat.name,
                    "custom_type_of_chat":type_of_chat,
                    "content": user_prompt,
                    "custom_user":1,
                    "comment_email": frappe.session.user,
                    "comment_by": "User"
                }).insert(ignore_permissions=True)
                frappe.db.commit()
            else:
                user_chat_id = frappe.db.exists("General Chat",{"name":user_name})
        
                """ Create a log chat in comment doctype """
                frappe.get_doc({
                    "doctype": "Comment",
                    "comment_type": "Comment",
                    "reference_doctype": "General Chat",
                    "reference_name":user_chat_id,
                    "custom_type_of_chat":type_of_chat,
                    "content": user_prompt,
                    "custom_user":1,
                    "comment_email": frappe.session.user,
                    "comment_by": "User"
                }).insert(ignore_permissions=True)
                frappe.db.commit()

            status = True
            message = "success"

            conversation_history = [  
                {"role": "system", "content":get_prompt},
                {"role": "user", "content":user_prompt}
            ]

        else:
            status = False
            message = "Not a Valid Deck ID"
        chat_conversation = process_chat_conversation_api(user_name,deck_id,type_of_chat,prompt_type,conversation_history)  
        return {"status":status,"message":message,"chat_conversation":chat_conversation}    
    except Exception as e:
        return {"status":False,"message":e}          

""" Processing the chat with azure api """
def process_chat_conversation_api(user_name,deck_id,type_of_chat,prompt_type,conversation_history):
    chat = []
    try:
        if prompt_type == "Discuss":
            tokens = frappe.db.get_single_value("Zen Chat Prompt Settings","discuss_max_response") or 0
            temp = frappe.db.get_single_value("Zen Chat Prompt Settings","discuss_temperature") or 0.0
            top = frappe.db.get_single_value("Zen Chat Prompt Settings","discuss_top_p") or 0.0
            frequency = frappe.db.get_single_value("Zen Chat Prompt Settings","discuss_frequency_penalty") or 0
            presence = frappe.db.get_single_value("Zen Chat Prompt Settings","discuss_presence_penalty") or 0
        elif prompt_type == "Task":    
            tokens = frappe.db.get_single_value("Zen Chat Prompt Settings","task_max_response") or 0
            temp = frappe.db.get_single_value("Zen Chat Prompt Settings","task_temperature") or 0.0
            top = frappe.db.get_single_value("Zen Chat Prompt Settings","task_top_p") or 0.0
            frequency = frappe.db.get_single_value("Zen Chat Prompt Settings","task_frequency_penalty") or 0
            presence = frappe.db.get_single_value("Zen Chat Prompt Settings","task_presence_penalty") or 0
        elif prompt_type == "Learn":
            tokens = frappe.db.get_single_value("Zen Chat Prompt Settings","learn_max_response") or 0
            temp = frappe.db.get_single_value("Zen Chat Prompt Settings","learn_temperature") or 0.0
            top = frappe.db.get_single_value("Zen Chat Prompt Settings","learn_top_p") or 0.0
            frequency = frappe.db.get_single_value("Zen Chat Prompt Settings","learn_frequency_penalty") or 0
            presence = frappe.db.get_single_value("Zen Chat Prompt Settings","learn_presence_penalty") or 0

        ENDPOINT = "https://deck-review.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview"
        API_KEY = "c13b1bebae7f4ebea81d55a80dd9b39d"
        # deployment = os.getenv("DEPLOYMENT_NAME", "gpt-35-turbo")   


        """ API Headers """
        headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
        }

        """ API Payload """
        payload = {
            "messages":conversation_history,
            "temperature": temp,
            "top_p": top,
            "max_tokens": tokens,
            "frequency_penalty": frequency,
            "presence_penalty": presence
        }

        # client = AzureOpenAI(
        #     api_version="2024-02-01",
        #     azure_endpoint=end_point,
        #     api_key=api_key
        # )

        # completion = client.chat.completions.create(
        #     model=deployment,
        #     messages = conversation_history,
        #     max_tokens=tokens,
        #     temperature=temp,
        #     top_p=top,
        #     frequency_penalty=frequency,
        #     presence_penalty=presence,
        #     stop=None,
        #     stream=False
        # )
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()    
        get_response_data = response.json()
        # change_resposne_data_json_loads = json.loads(get_response_data)
        response_assistant_chat = get_response_data["choices"][0]["message"]["content"].replace("#", "").replace("*", "")

        extraction_prompt = frappe.db.get_value("Deck Review",{"name":deck_id,"user_idemail":user_name},["deck_text_extraction"])
        if extraction_prompt:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": "Deck Review",
                "reference_name":deck_id,
                "custom_type_of_chat":type_of_chat,
                "content": response_assistant_chat,
                "custom_user":0,
                "comment_email": frappe.session.user,
                "comment_by": "admin"
            }).insert(ignore_permissions=True)
            frappe.db.commit()

            user_conversation = frappe.db.get_all("Comment",filters={"reference_name":deck_id,"reference_doctype":"Deck Review","comment_type":"Comment","custom_type_of_chat":type_of_chat},fields=['*'], order_by="creation ASC")
            for comment in user_conversation:
                content = comment.get('content')
                custom_user = comment.get('custom_user')
                if content:
                    comment_text = BeautifulSoup(content, "html.parser").get_text()
                    creation_timestamp = str(comment.get('creation'))
                    creation_date = format_date(creation_timestamp)
                    creation_time = format_time(creation_timestamp)
                    if custom_user == 1:
                        place = "Right"
                    else:
                        place = "Left"		
                chat_boxes = {
                    "user_type":comment.get("comment_by"),
                    "chat_box": comment_text,
                    "chat_date": creation_date,
                    "chate_time": creation_time,
                    "place":place
                }
                chat.append(chat_boxes)

        elif deck_id == "general-001":
            """ Create a log chat in comment doctype """
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": "General Chat",
                "reference_name":user_name,
                "custom_type_of_chat":type_of_chat,
                "content": response_assistant_chat,
                "custom_user":0,
                "comment_email": frappe.session.user,
                "comment_by": "admin"
            }).insert(ignore_permissions=True)
            frappe.db.commit()

            user_conversation = frappe.db.get_all("Comment",filters={"reference_name":user_name,"reference_doctype":"General Chat","comment_type":"Comment","custom_type_of_chat":type_of_chat},fields=['*'], order_by="creation ASC")
            for comment in user_conversation:
                content = comment.get('content')
                custom_user = comment.get('custom_user')
                if content:
                    comment_text = BeautifulSoup(content, "html.parser").get_text()
                    creation_timestamp = str(comment.get('creation'))
                    creation_date = format_date(creation_timestamp)
                    creation_time = format_time(creation_timestamp)
                    if custom_user == 1:
                        place = "Right"
                    else:
                        place = "Left"		
                chat_boxes = {
                    "user_type":comment.get("comment_by"),
                    "chat_box": comment_text,
                    "chat_date": creation_date,
                    "chate_time": creation_time,
                    "place":place
                }
                chat.append(chat_boxes)
        
        return chat
    except Exception as e:
        return chat

""" Get the chat conversation list for each user """
@frappe.whitelist()
def get_chat_conversation_list(user_name,deck_id,type_of_chat):
    try:
        chat = []
        extraction_prompt = frappe.db.get_value("Deck Review",{"name":deck_id,"user_idemail":user_name},["deck_text_extraction"])
        if extraction_prompt:
            user_conversation = frappe.db.get_all("Comment",filters={"reference_name":deck_id,"reference_doctype":"Deck Review","comment_type":"Comment","custom_type_of_chat":type_of_chat},fields=['*'], order_by="creation ASC")
            for comment in user_conversation:
                content = comment.get('content')
                custom_user = comment.get('custom_user')
                if content:
                    comment_text = BeautifulSoup(content, "html.parser").get_text()
                    creation_timestamp = str(comment.get('creation'))
                    creation_date = format_date(creation_timestamp)
                    creation_time = format_time(creation_timestamp)
                    if custom_user == 1:
                        place = "Right"
                    else:
                        place = "Left"		
                chat_boxes = {
                    "user_type":comment.get("comment_by"),
                    "chat_box": comment_text,
                    "chat_date": creation_date,
                    "chate_time": creation_time,
                    "place":place
                }
                chat.append(chat_boxes)
                
        elif deck_id == "general-001":
            user_conversation = frappe.db.get_all("Comment",filters={"reference_name":user_name,"reference_doctype":"General Chat","comment_type":"Comment","custom_type_of_chat":type_of_chat},fields=['*'], order_by="creation ASC")
            for comment in user_conversation:
                content = comment.get('content')
                custom_user = comment.get('custom_user')
                if content:
                    comment_text = BeautifulSoup(content, "html.parser").get_text()
                    creation_timestamp = str(comment.get('creation'))
                    creation_date = format_date(creation_timestamp)
                    creation_time = format_time(creation_timestamp)
                    if custom_user == 1:
                        place = "Right"
                    else:
                        place = "Left"		
                chat_boxes = {
                    "user_type":comment.get("comment_by"),
                    "chat_box": comment_text,
                    "chat_date": creation_date,
                    "chate_time": creation_time,
                    "place":place
                }
                chat.append(chat_boxes)
                
        return {"status":True,"message":"success","chat_conversation":chat}    
    except Exception as e:
        return {"status":False,"message":e}