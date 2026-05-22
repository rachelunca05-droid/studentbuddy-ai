from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
user_context = {}

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/chat", methods=["POST"])
def chat():
    try:                                                    
        user_message = request.json.get("message", "")
        user_id = "default_user"

        if "first-year" in user_message.lower():
            user_context[user_id] = {"year": "first-year"}

        context = user_context.get(user_id, {})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful university assistant that helps students with registration, hostel, fees, and advice. User info: {context}"
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Something went wrong with the AI companion"}), 500

    if "hostel" in user_message.lower():
        reply += "\n⚠️ Apply early! Hostel slots fill up quickly."
    
    if "registration" in user_message.lower():
        reply += "\n📅 Don't forget to complete registration before the deadline."

    if "stressed" in user_message.lower() or "stress" in user_message.lower():
        reply = "I understand this can be stressful. Let me help you. \n" + reply

    if "confused" in user_message.lower():
        reply = "No worries, I'll explain it simply.\n" + reply

    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(debug=True)