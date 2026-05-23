from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key="sk-3cb6345534c043cca511141eb3d8c675",  
    base_url="https://api.deepseek.com"          
)
user_context = {}

SUPABASE_URL = "https://nydgmpsoqidjxyoxxhaz.supabase.co"
SUPABASE_KEY = "sb_publishable_Nu2qT_iCvft5r0iTTuqryw_3UoM6P42"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

        # 🚀 1. ADD THESE LINES TO PULL YOUR REAL DATA FROM SUPABASE
        try:
            profile_data = supabase.table("student_profiles").select("*").eq("id", 1).single().execute().data
            assignment_data = supabase.table("Assignments").select("*").eq("student_id", 1).execute().data
            hostel_data = supabase.table("Hostel").select("*").execute().data
        except Exception as db_err:
            print(f"Database fetch warning: {db_err}")
            profile_data, assignment_data, hostel_data = {}, [], []

        # 🚀 2. BUNDLE IT ALL TOGETHER FOR DEEPSEEK
        database_context = f"""
        Profile: {profile_data}
        Assignments: {assignment_data}
        Hostels: {hostel_data}
        """

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful university assistant. Use this live data to answer the student: {database_context}. Original Context: {context}"
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

    # Your custom keyword filters stay exactly the same below here...
    if "hostel" in user_message.lower():
        reply += "\n⚠️ Apply early! Hostel slots fill up quickly."
    
    if "registration" in user_message.lower():
        reply += "\n📅 Don't forget to complete registration before the deadline."

    if "stressed" in user_message.lower() or "stress" in user_message.lower():
        reply = "I understand this can be stressful. Let me help you. \n" + reply

    if "confused" in user_message.lower():
        reply = "No worries, I'll explain it simply.\n" + reply

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)