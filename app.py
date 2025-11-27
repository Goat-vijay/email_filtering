print("Flask starting...")

from flask import Flask, request, jsonify, render_template
import imaplib
import email
import requests
import json


app = Flask(__name__, static_url_path='',  static_folder='static',template_folder='templates')


# ---------- INSERT YOUR IBM NLU CREDENTIALS ----------
NLU_API_KEY = "QrheBuWxzLL8Fr67E-297qCa6xs_aW1Iot7-TUFWZwYV"
NLU_URL = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/c2700662-6e1b-4a53-b060-c2e60c4ef7b8/v1/analyze?version=2022-04-07"


# ---------- EMAIL CLASSIFICATION ----------
from email.header import decode_header

# Decode email subject properly
def decode_subject(subject):
    decoded_parts = decode_header(subject)
    decoded_subject = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_subject += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded_subject += part
    return decoded_subject

def classify_email(full_text):
    payload = {
        "text": full_text,
        "features": {"categories": {}},
        "return_analyzed_text": True
    }

    try:
        response = requests.post(
            NLU_URL,
            auth=("apikey", NLU_API_KEY),
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        data = response.json()

        mapping = {
            "personal": "personal",
            "education": "university",
            "university": "university",
            "school": "university",
            "college": "university",
            "syllabus": "university",
            "course": "university",
            "lecture": "university",
            "assignment": "university",
            "job": "work",
            "work": "work",
            "business": "work",
            "office": "work",
            "advertising": "ads",
            "marketing": "ads",
            "promotion": "ads",
            "offer": "ads",
            "discount": "ads",
            "sale": "ads",
            "lottery": "spam",
            "spam": "spam",
            "free": "spam",
        }

        # 1️⃣ Check Watson categories
        if "categories" in data and len(data["categories"]) > 0:
            label = data["categories"][0]["label"].lower()
            for key, value in mapping.items():
                if key in label:
                    return value

        # 2️⃣ Fallback: check text content for keywords
        text_lower = full_text.lower()
        for key, value in mapping.items():
            if key in text_lower:
                return value

        return "uncategorized"

    except Exception as e:
        print("Watson Error:", e)
        return "uncategorized"


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/application")
def appli():
    return render_template("application.html")



@app.route("/api", methods=["POST"])
def api_route():
    data = request.get_json()
    user_email = data.get("email")
    password = data.get("password")
    count = int(data.get("count", 5))

    results = []

    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(user_email, password)
        mail.select('inbox')

        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()[-count:]

        for eid in email_ids:
            status, msg_data = mail.fetch(eid, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            subject = msg['subject'] or "No Subject"
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            full_text = f"Subject: {subject}\n\n{body}"

            category = classify_email(full_text)

            results.append({
                "email": subject,
                "category": category
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)


