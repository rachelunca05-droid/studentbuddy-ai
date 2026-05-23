from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key="sk-dbc4cb0a6d65470b8ef58afe554fc8cd",  
    base_url="https://api.deepseek.com"          
)
user_context = {}

SUPABASE_URL = "https://nydgmpsoqidjxyoxxhaz.supabase.co"
SUPABASE_KEY = "sb_publishable_Nu2qT_iCvft5r0iTTuqryw_3UoM6P42"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

SYSTEM_PROMPT = """
You are a smart student support assistant for a university system.

Your purpose is to help students with:
- Hostel and accommodation recommendations
- Assignment guidance and workflow planning
- Automatic reminder preparation
- Campus navigation and map guidance
- Emotional support for stress, sadness, anxiety, loneliness, burnout, or other student emotions
- General student support

You must always respond in a clean, organized, and student-friendly format.

GENERAL STYLE RULES:
- Never write one long paragraph.
- Always use line breaks.
- Use short and clear sentences.
- Use bullet points when listing information.
- Use emojis naturally to guide attention.
- Keep the response friendly, supportive, and easy to scan.
- Do not overuse emojis.
- Do not sound robotic.
- Do not give unnecessary long explanations.
- Do not mention database, backend, API, query, JSON, server, or system to the student.
- Do not say “Based on the database”.
- Do not expose internal logic.
- Do not invent missing information.

CONTEXT AWARENESS RULE:
- Remember the current conversation context.
- Use previous messages in the same chat to understand what the student needs.
- If the student already gave a name, emotion, location, task, or preference, use it naturally.
- Do not ask again for information that was already provided.
- If the context is unclear, ask a short clarifying question.
- Keep responses consistent with earlier messages.

RESPONSE STRUCTURE:
Every response should follow this structure when possible:
1. Start with a short friendly sentence.
2. Give the main answer using bullets or clear sections.
3. Use emojis to highlight important points.
4. End with a helpful next step or gentle question.

USEFUL EMOJIS:
- 😊 Friendly opening
- 🏠 Hostel or accommodation
- ✅ Available / completed
- ❌ Not available / cannot proceed
- 💰 Price or fee
- 📝 Assignment / task
- ⏰ Reminder / deadline
- 📍 Location / map
- 🧭 Direction / navigation
- 📌 Important note
- ⚠️ Warning / reminder
- 📅 Date or schedule
- 🚶 Walking direction
- 🖼️ Image or map generation
- 💙 Emotional support
- 🌿 Calm / breathing
- 🧠 Mental well-being
- 🤝 Support / help

HOSTEL FORMAT:
When the student asks about hostel or accommodation, use this exact layout:

Sure! 😊 Here are the available hostel options:

🏠 [Room / Hostel Name]
- Type: [Room Type]
- Price: [Price]
- Status: [Availability]

🏠 [Room / Hostel Name]
- Type: [Room Type]
- Price: [Price]
- Status: [Availability]

📌 Note:
- [Short helpful note if needed]

Would you like to choose one of these options?

ASSIGNMENT FORMAT:
When the student asks about assignments, use this exact layout:

Sure! 📝 Here is a simple workflow:

📌 Step 1: [Step title]
- [Short explanation]

📌 Step 2: [Step title]
- [Short explanation]

📌 Step 3: [Step title]
- [Short explanation]

📌 Step 4: [Step title]
- [Short explanation]

Would you like me to help you start with Step 1?

REMINDER FORMAT:
When the student asks for a reminder, use this exact layout:

Sure! ⏰ I can help with that.

📝 Task:
- [Task name]

📅 Date / Time:
- [Date and time]

📌 Reminder plan:
- [Reminder suggestion]

If the date or time is missing, ask:
Could you tell me the date and time for the reminder? 😊

MAP FORMAT:
When the student asks about a campus location, use this exact layout:

Sure! 📍 I can help you find it.

🧭 Destination:
- [Place name]

🚶 Direction:
- Start from [Starting point]
- Walk toward [Landmark]
- Turn [left/right] at [Location]
- Continue until you reach [Destination]

🖼️ Visual guide:
- I can generate a map image to help you reach the place.

Where are you starting from?

EMOTIONAL SUPPORT FORMAT:
When the student says they are stressed, sad, anxious, overwhelmed, lonely, tired, burned out, or emotionally struggling, respond with care.
Use this exact layout:

I’m sorry you’re feeling this way 💙  
You don’t have to handle everything alone.

🌿 First, try this:
- Take a slow breath in for 4 seconds.
- Hold it for 2 seconds.
- Breathe out slowly for 6 seconds.

🧠 What might help right now:
- Pause for a few minutes.
- Drink some water.
- Write down what is bothering you.
- Focus on one small task first.
- Talk to someone you trust.

📌 Gentle reminder:
- Your feelings are valid.
- It is okay to feel tired.
- You are not weak for needing rest.

Would you like to tell me what happened?

EMOTIONAL SPEECH FORMAT:
If the student asks for motivation, encouragement, or a short speech, use this style:

You’re doing better than you think 💙

📌 Remember this:
- One bad day does not mean you are failing.
- Feeling tired does not mean you are weak.
- Progress can still happen slowly.
- You only need to take the next small step.

🌿 For now:
- Breathe.
- Rest if you need to.
- Then continue one thing at a time.

I’m here with you. What is making you feel this way?

SAFETY RULE FOR SERIOUS EMOTIONS:
If the student mentions self-harm, suicide, wanting to disappear, or not wanting to live:
- Respond calmly and seriously.
- Encourage them to contact emergency services or a trusted person immediately.
- Do not give harmful advice.
- Do not make jokes.
- Keep the response supportive and urgent.

Use this layout:

I’m really sorry you’re feeling this much pain 💙  
Your safety matters right now.

⚠️ Please do this now:
- Contact someone you trust immediately.
- Stay near other people if possible.
- Call local emergency services if you might hurt yourself.
- If you are in Malaysia, you can contact Befrienders KL at 03-7627 2929.

📌 You do not have to go through this alone.
Please reach out to someone now.

MISSING INFORMATION RULE:
If important information is missing:
- Do not guess.
- Ask a short and polite question.

Example:
I can help with that 😊  
Could you tell me your starting location first?

FINAL RULE:
Every answer must look clean, lightweight, and readable.
Always use line breaks, emojis, and bullet points.
Never respond with one heavy paragraph.
"""

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/chat", methods=["POST"])
def chat():
    reply = ""
    user_message = request.json.get("message", "")
    user_id = "default_user"
    student_db_id = 1 
    positive_responses = ["yes", "y", "yeah", "ya", "sure", "okay", "ok", "of course", "please", "can"]
    negative_responses = ["no", "nope", "nah", "not now"]

    if "reminder" in user_message.lower():

        reminder_res = supabase.table("reminders")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        reminders = reminder_res.data

        if not reminders:
            reply = "📌 **Your Reminders:**\n- You currently have no reminders set.\n\nWould you like me to help you create one? 😊"
        else:
            reply = "📌 **Your Reminders:**\n\n"
            for r in reminders:
                reply += f"📝 {r['task']}\n📅 {r['date']} at {r['time']}\n\n"
                reply += "Would you like to add another reminder or edit one? 😊"
        user_context[user_id] = {"intent": "reminder_followup"}

        return jsonify({
            "reply": reply,
            "response": reply,
            "text": reply,
            "message": reply
        })

    if user_context.get(user_id, {}).get("intent") == "reminder_followup" \
    and "task:" in user_message.lower() and "date:" in user_message.lower():

        try:
            lines = user_message.split("\n")

            task = ""
            date = ""
            time = ""

            for line in lines:
                if "task:" in line.lower():
                    task = line.split(":", 1)[1].strip()
                elif "date:" in line.lower():
                    date = line.split(":", 1)[1].strip()
                elif "time:" in line.lower():
                    time = line.split(":", 1)[1].strip()

            supabase.table("reminders").insert({
                "user_id": user_id,
                "task": task,
                "date": date,
                "time": time
            }).execute()

            user_context[user_id] = {}

            reply = (
                "✅ Your reminder has been created successfully!\n\n"
                f"📝 Task: {task}\n"
                f"📅 Date: {date}\n"
                f"⏰ Time: {time}"
            )

        except Exception as e:
            print("ERROR:", e)
            reply = "⚠️ I couldn't save your reminder. Please try again."

        return jsonify({
            "reply": reply,
            "response": reply,
            "text": reply,
            "message": reply
        })

    if user_context.get(user_id, {}).get("intent") == "reminder_followup" and any (p in user_message.lower() for p in positive_responses):

        reply = (
            "⏰ Great! Let’s create a new reminder.\n\n"
            "Tell me:\n"
            "- What is the task?\n"
            "- Date\n"
            "- Time\n\n"
            "Example:\n"
            "👉 Remind me to submit assignment tomorrow at 5pm 😊"
        )

        return jsonify({
            "reply": reply,
            "response": reply,
            "text": reply,
            "message": reply
        })

    if user_context.get(user_id, {}).get("intent") == "reminder_followup" and any(n in user_message.lower() for n in negative_responses):

        reply = "😊 No problem! Let me know if you need anything else."

        user_context[user_id] = {}  # reset context

        return jsonify({
            "reply": reply,
            "response": reply,
            "text": reply,
            "message": reply
        })
    
    if "add another" in user_message.lower():

        reply = (
            "✅ Sure! Let’s add another reminder.\n\n"
            "Tell me:\n"
            "- Task name\n"
            "- Date\n"
            "- Time\n\n"
            "Example:\n"
            "👉 Remind me to pay fees tomorrow at 12pm 😊"
        )

        return jsonify({
            "reply": reply,
            "response": reply,
            "text": reply,
            "message": reply
        })

    if "first-year" in user_message.lower():
        user_context[user_id] = {"year": "first-year"}

    context = user_context.get(user_id, {})

    profile_data = {"name": "Student", "semester": "Current"}
    assignment_data = []
    hostel_data = []
    reminder_data = []
    emotional_profile = {}
    past_chat_logs = []

    try:
        profile_res = supabase.table("student_profiles").select("*").eq("id", student_db_id).execute()
        if profile_res.data:
            profile_data = profile_res.data[0] if isinstance(profile_res.data, list) else profile_res.data

        assignment_res = supabase.table("Assignments").select("*").eq("student_id", student_db_id).execute()
        if assignment_res.data:
            assignment_data = assignment_res.data

        hostel_res = supabase.table("Hostel").select("*").execute()
        if hostel_res.data:
            hostel_data = hostel_res.data

        reminder_res = supabase.table("reminders").select("*").eq("user_id", user_id).execute()
        if reminder_res.data:
            reminder_data = reminder_res.data

        emo_res = supabase.table("emotional_context").select("*").eq("student_id", student_db_id).execute()
        if emo_res.data:
            emotional_profile = emo_res.data[0]

        memory_res = supabase.table("chat_memory").select("role", "content").eq("student_id", student_db_id).order("created_at", desc=True).limit(4).execute()
        if memory_res.data:
            past_chat_logs = list(reversed(memory_res.data)) 
    except Exception as db_err:
        print(f"⚠️ Database Context Reading Alert: {db_err}")

    database_context = f"""
    LIVE UTILITY RECORDS AVAILABLE:
    Profile: {profile_data}
    Assignments: {assignment_data}
    Hostels: {hostel_data}
    
    💙 ACTIVE EMOTIONAL HISTORY METRICS:
    Recent User Mood: {emotional_profile.get('recent_mood', 'Neutral')}
    Preferred Support Style: {emotional_profile.get('preferred_support_style', 'Friendly and concise')}
    """

    messages_payload = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}{database_context}\nActive Chat Context Tracker: {context}"
        }
    ]

    for log in past_chat_logs:
        messages_payload.append({"role": log["role"], "content": log["content"]})

    messages_payload.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages_payload
        )
        reply = response.choices[0].message.content

        try:
            supabase.table("chat_memory").insert({"student_id": student_db_id, "role": "user", "content": user_message}).execute()
            supabase.table("chat_memory").insert({"student_id": student_db_id, "role": "assistant", "content": reply}).execute()

            emotional_triggers = ["stress", "sad", "anxious", "lonely", "burnout", "tired", "overwhelmed", "stressed"]
            if any(trigger in user_message.lower() for trigger in emotional_triggers):

                supabase.table("mood_logs").insert({"student_id": student_db_id, "detected_emotion": "Stressed/Overwhelmed"}).execute()

                supabase.table("emotional_context").update({"recent_mood": "Stressed", "updated_at": "now()"}).eq("student_id", student_db_id).execute()
        except Exception as write_err:
            print(f"⚠️ Failed saving memory logs to Supabase: {write_err}")

    except Exception as ai_err:
        print(f"❌ LLM API Processing Error: {ai_err}")
        reply = "😊 Hello! I am here to fully support your student journey. Ask me about hostel options, study workflows, location paths, or talk to me about any stress you are feeling."

    if "hostel" in user_message.lower() and "⚠️" not in reply and "Befrienders" not in reply:
        reply += "\n\n⚠️ Apply early! Hostel slots fill up quickly."
    
    if "registration" in user_message.lower() and "📅" not in reply and "Befrienders" not in reply:
        reply += "\n\n📅 Don't forget to complete registration before the deadline."

    return jsonify({
        "reply": reply,
        "response": reply,
        "text": reply,
        "message": reply
    })

@app.route("/add-reminder", methods=["POST"])
def add_reminder():
    data = request.json

    print("✅ RECEIVED:", data)

    task = data.get("task")
    date = data.get("date")
    time = data.get("time")

    user_id = "default_user"

    try:
        response = supabase.table("reminders").insert({
            "user_id": user_id,
            "task": task,
            "date": date,
            "time": time
        }).execute()

        print("✅ INSERT RESPONSE:", response)  # DEBUG

        return jsonify({"status": "success"})

    except Exception as e:
        print("❌ INSERT ERROR:", e)
        return jsonify({"status": "error"})
    
if __name__ == "__main__":
    app.run(debug=True)