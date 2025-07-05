from flask import Flask, request, render_template, send_file
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

ACCESS_TOKEN = "EAB72YZA4NcjIBPInPc39XlbILv7JtRhEf9VgMk1CV0ZA2ZATAvjaHnAa6iaiPYz3M2FIoOwVJZAtEoKwC3nwG29wtAxz8t8gH6FEanfmp0I1s19hes6N4uwVOSkueWxcrdE8oHQJLo4tdDrNIaM6o6hqtM0ubjspRavr49SoIO8ZAfOqEwqdzN4R55zHkc85Uko9qIx6T4zrqPrWfLRMZBRuxpW9DHUpTZBwvJsr1I9ZA18RqQZDZD"
PHONE_NUMBER_ID = "530531536814628"
VERIFY_TOKEN = "amrut"
LOG_FILE = "webhook_log.txt"

# ========== UTILITIES ==========

def log_to_file(data):
    with open(LOG_FILE, "a") as f:
        f.write(f"\n[{datetime.now()}]\n{json.dumps(data, indent=2)}\n{'-'*60}\n")

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)

def send_program_buttons(to):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "🎓 Welcome to the University of Mysore – a heritage institution fostering knowledge, innovation, and excellence since 1916..\n\nPlease choose your program type:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "online_program", "title": "1️⃣ ONLINE PROGRAM"}
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "odl_program", "title": "2️⃣REGULAR PROGRAM"}
                    }
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=payload)

def send_course_buttons(to, program):
    online_courses = ["B.A", "B.COM", "M.SC MATHS", "MBA", "MA in KANNADA", "MA in HINDI", "MA in ENGLISH"]
    odl_courses = ["B.A", "B.COM", "BBA", "BCA", "BSW", "MSW", "M.COM", "M.SC"]
    courses = online_courses if program == "online_program" else odl_courses

    body_text = "Please choose a course under ONLINE PROGRAM:" if program == "online_program" else "Please choose a course under ODL PROGRAM:"

    buttons = [ {
        "type": "reply",
        "reply": {"id": f"course_{c.lower().replace(' ', '_')}", "title": c}
    } for c in courses[:3] ]  # Only 3 buttons allowed per message

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": buttons}
        }
    }
    requests.post(url, headers=headers, json=payload)

def send_course_menu(to):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Please choose one of the options for this course:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "admission_info", "title": "Admission Info"}},
                    {"type": "reply", "reply": {"id": "exam_fee", "title": "Exam Fee"}},
                    {"type": "reply", "reply": {"id": "syllabus", "title": "Syllabus"}}
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=payload)

def handle_final_action(to, action):
    links = {
        "admission_info": https://www.uompgadmissions.com/",
        "exam_fee": "https://www.uompgadmissions.com/",
        "exam_date": "https://www.uompgadmissions.com//",
        "syllabus": "https://www.uompgadmissions.com/"
    }
    if action in links:
        send_whatsapp_message(to, f"Dear Student, Please Visit:\n{links[action]}")

# ========== ROUTES ==========

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    # 🔒 Log entire webhook payload to file
    log_to_file(data)
    
    try:
        msg = data['entry'][0]['changes'][0]['value'].get('messages', [])[0]
        sender = msg['from']

        if 'interactive' in msg:
            button_id = msg['interactive']['button_reply']['id']

            if button_id in ["online_program", "odl_program"]:
                send_course_buttons(sender, button_id)
            elif button_id.startswith("course_"):
                send_course_menu(sender)
            elif button_id in ["admission_info", "exam_fee", "exam_date", "syllabus", "slm"]:
                handle_final_action(sender, button_id)
        else:
            send_program_buttons(sender)

    except Exception as e:
        print("Error:", e)

    return "OK", 200

@app.route("/download-log")
def download_log():
    if os.path.exists(LOG_FILE):
        return send_file(LOG_FILE, as_attachment=True)
    else:
        return "Log file not found.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
