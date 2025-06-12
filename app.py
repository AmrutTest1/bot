from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# === WHATSAPP CREDENTIALS ===
ACCESS_TOKEN = "EAB72YZA4NcjIBOzOVSK3NIMlFXCaKFRyhfQOSUMjZCnoEPwE2FFcMsn6qsRqjFP9M57bMOvaYScySyZBKdEouEZB4sHw2LUPzJebuJdJmNZCI295UJLTqrZAQXnDV5HEt654WAfLhQz6plBZBgR9qZAbigAxkPF0qAZCETtvKWANQ1ET0hC0gSiAZB0eZC4XQFtKkEEmjItXlHXnyIZBIDVbmEmxyu5O5Y7WK62PkpwZD"
PHONE_NUMBER_ID = "530531536814628"
VERIFY_TOKEN = "amrut"

# === HOME ROUTE ===
@app.route("/")
def home():
    return render_template("index.html")

# === WEBHOOK VERIFICATION ===
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token"

# === WEBHOOK HANDLER ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_msg = msg['text']['body'].lower()
        sender = msg['from']

        # === BOT LOGIC ===
        if "course" in user_msg:
            reply_text = "📚 KSOU Courses:\n1. BA\n2. BCom\n3. BSc"
        elif "admission" in user_msg:
            reply_text = "📝 KSOU Admission:\nApply at https://ksouportal.com"
        elif "exam" in user_msg:
            reply_text = "🗓️ KSOU Exam Info:\nTimetable available at https://ksouportal.com/exams"
        else:
            reply_text = "👋 Welcome to KSOU Bot!\nType: 'course', 'admission', or 'exam' to get started."

        # === SEND REPLY BACK TO WHATSAPP ===
        requests.post(
            f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "messaging_product": "whatsapp",
                "to": sender,
                "text": {"body": reply_text}
            }
        )

    except Exception as e:
        print("Error:", e)

    return "OK", 200

# === RUN THE FLASK APP ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
