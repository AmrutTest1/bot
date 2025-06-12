from flask import Flask, request, render_template
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAB72YZA4NcjIBO2Wg8WIv35tmmnqWZCgy7qX6ZClLSQRdsYkAyLjRZCIlsmRd9NGIGWb9ZBZA3ZAigyKYjkLBkdm4m0Rcr9PNUIKRWrKLKZBdedsB9370cFzsf7AfD5G8gqPXygLkCIfM4bVzsZCF23Hq0KnwuzfB31PtUi1o3Tv4ucpdfAK4kUxpz3tMhHStA81FEhZBC2cED0eb48bsZA7Epu9w3JcwPYUSwOb4gZD"
PHONE_NUMBER_ID = "530531536814628"
VERIFY_TOKEN = "amrut"

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
        user_msg = msg['text']['body'].lower()
        sender = msg['from']

        # Bot logic
        if "course" in user_msg:
            reply_text = "KSOU Courses:\n1. BA\n2. BCom\n3. BSc"
        else:
            reply_text = "Welcome to KSOU Bot!"

        # Send response
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
