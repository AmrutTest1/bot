from flask import Flask, request, render_template
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAB72YZA4NcjIBO6CqVP6NH8pcpGVGVakO97yjS8bm9FPdgxCZBbRjs93OOfW70IT7JEYQUajdHUQ9aWhUfnN40ZCWFTwQKOzqbODPXpUytDPZAZBIA0TuiIvbyqHHAySqZB0pUwU2ZAzaGRgsAdVca8y8YG0Rr1nr8gU6XiV3gYsuGsEZBgE0IDhnhwW13Bcn3zl38iP4Pw75TEjHsIzqXd7atQds7oHH5ddRZBMZD"
PHONE_NUMBER_ID = "530531536814628"
VERIFY_TOKEN = "amrut"


# ========== UTILITIES ==========
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
                "text": "🎓 Welcome to Karnataka State Open University, Mysuru\n\nOffering Online Courses and ODL Programs.\n\nPlease choose your program type:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "online_program", "title": "1️⃣ ONLINE PROGRAM"}
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "odl_program", "title": "2️⃣ ODL PROGRAM"}
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

    buttons = [{
        "type": "reply",
        "reply": {"id": f"course_{c.lower().replace(' ', '_')}", "title": c}
    } for c in courses[:3]]  # WhatsApp allows only 3 buttons, adjust later for more

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
        "admission_info": "https://www.ksoumysuru.ac.in/index.php/admissions/",
        "exam_fee": "https://ksouportal.com/views/ExamHome.aspx",
        "exam_date": "https://www.ksoumysuru.ac.in/index.php/Exam/",
        "slm": "https://app.ksouonlinestudy.com/",
        "syllabus": "https://app.ksouonlinestudy.com/"
    }
    if action in links:
        send_whatsapp_message(to, f"Dear Student, Please Visit:
{links[action]}")

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
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
