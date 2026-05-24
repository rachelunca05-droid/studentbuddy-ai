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

FLOW_HOSTEL = "hostel_flow"
FLOW_ASSIGNMENT = "assignment_flow"
FLOW_NAVIGATION = "navigation_flow"

SUPABASE_URL = "https://nydgmpsoqidjxyoxxhaz.supabase.co"
SUPABASE_KEY = "sb_publishable_Nu2qT_iCvft5r0iTTuqryw_3UoM6P42"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

SYSTEM_PROMPT = """
You are an intelligent AI assistant similar to ChatGPT.

You should:
- Think before responding
- Ask follow-up questions if needed
- Adapt to the user's situation
- Personalize responses using past context
- Break down complex help into steps

Do NOT:
- Give robotic replies
- Rush answers
- Ignore emotional context

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
    
def format_hostel_response(hostel_data):
    if not hostel_data:
        return "❌ No hostel options available right now."

    reply = "Sure! 😊 Here are the available hostel options:\n\n"

    for h in hostel_data:
        reply += f"""🏠 {h.get('name', 'Hostel Room')}
- Type: {h.get('type', 'Standard')}
- Price: {h.get('price', 'N/A')}
- Status: {h.get('status', 'Unknown')}

"""

    reply += "📌 Note:\n- Apply early to secure your slot.\n\nWould you like to choose one of these options?"
    return reply

import json

def run_agent(messages, user_id, max_steps=3):

    for step in range(max_steps):

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
        )

        msg = response.choices[0].message

        # ✅ Normal response (no tool calling yet)
        return msg.content

    return "⚠️ I couldn’t process that properly."

def clean_response(text):
    return text.strip().replace("  ", " ")

import random

def add_followup(reply):
    suggestions = [
        "📝 Need help planning your assignment?",
        "🏠 Looking for hostel options?",
        "⏰ Want to set a reminder?",
        "💙 Need help managing stress?"
    ]

    chosen = random.sample(suggestions, 2)

    reply += "\n\n💡 You may also want:\n"
    for c in chosen:
        reply += f"- {c}\n"

    return reply

from datetime import datetime, timedelta

def convert_date_time(date_str, time_str):
    try:
        now = datetime.now()

        # ✅ Convert date
        if "tomorrow" in date_str.lower():
            date = now + timedelta(days=1)
        else:
            date = datetime.strptime(date_str, "%Y-%m-%d")

        formatted_date = date.strftime("%Y-%m-%d")

        # ✅ Convert time (5pm → 17:00:00)
        time = datetime.strptime(time_str.strip(), "%I%p")
        formatted_time = time.strftime("%H:%M:%S")

        return formatted_date, formatted_time

    except Exception as e:
        print("⚠️ Conversion error:", e)
        return None, None

@app.route("/chat", methods=["POST"])
def chat():
    reply = ""
    user_message = request.json.get("message", "")
    user_id = "default_user"
    student_db_id = 1 

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

    if "task:" in user_message.lower() and "date:" in user_message.lower() and "time:" in user_message.lower():

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

            db_date, db_time = convert_date_time(date, time)

            if not db_date or not db_time:
                reply = "⚠️ I couldn't understand the date or time. Please clarify 😊"
            else:
                supabase.table("reminders").insert({
                    "user_id": user_id,
                    "task": task,
                    "date": db_date,
                    "time": db_time
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

    if user_context.get(user_id, {}).get("intent") == "reminder_creation":

        context = user_context[user_id]
        step = context.get("step")

        if step == "ask_task":
            context["task"] = user_message
            context["step"] = "ask_date"

            return jsonify({
                "reply": "📅 When should I remind you?",
                "response": "📅 When should I remind you?",
                "text": "📅 When should I remind you?",
                "message": "📅 When should I remind you?"
            })

        elif step == "ask_date":
            context["date"] = user_message
            context["step"] = "ask_time"

            return jsonify({
                "reply": "⏰ What time?",
                "response": "⏰ What time?",
                "text": "⏰ What time?",
                "message": "⏰ What time?"
            })

        elif step == "ask_time":
            context["time"] = user_message

            supabase.table("reminders").insert({
                "user_id": user_id,
                "task": context["task"],
                "date": context["date"],
                "time": context["time"]
            }).execute()

            user_context[user_id] = {}

            reply = f"""✅ Reminder created!

    📝 Task: {context['task']}
    📅 Date: {context['date']}
    ⏰ Time: {context['time']}
"""

            return jsonify({
                "reply": reply,
                "response": reply,
                "text": reply,
                "message": reply
            })
        
    if user_context.get(user_id, {}).get("intent") == FLOW_HOSTEL:

        context = user_context[user_id]
        step = context.get("step")

        if step == "show_options":
            context["step"] = "ask_preference"

            return jsonify({
                "message": "🏠 Do you prefer:\n- Single room\n- Shared room\n- Cheapest option?"
            })

        elif step == "ask_preference":

            preference = user_message.lower()

            filtered = []

            for h in hostel_data:
                name = str(h.get("name", "")).lower()
                h_type = str(h.get("type", "")).lower()

                if "single" in preference and "single" in h_type:
                    filtered.append(h)
                elif "shared" in preference and "shared" in h_type:
                    filtered.append(h)
                elif "cheap" in preference or "cheapest" in preference:
                    filtered.append(h)

            if not filtered:
                filtered = hostel_data

            user_context[user_id] = {}

            reply = format_hostel_response(filtered)

            return jsonify({
                "message": reply,
                "reply": reply,
                "response": reply,
                "text": reply
            })

    if user_context.get(user_id, {}).get("intent") == FLOW_ASSIGNMENT:

        context = user_context[user_id]
        step = context.get("step")

        if step == "choose_assignment":

            try:
                index = int(user_message) - 1
                selected = assignment_data[index]

                context["assignment"] = selected
                context["step"] = "planning"

                return jsonify({
                "message": f"✅ Great! Let's plan: {selected.get('title')}\n\nType 'start' to get a workflow."
                })

            except:
                return jsonify({"message": "⚠️ Please enter a valid number."})

        elif step == "planning":

            user_context[user_id] = {}

            reply = """Sure! 📝 Here is a simple workflow:

    📌 Step 1: Understand the task
    - Read instructions carefully

    📌 Step 2: Research
    - Gather key materials

    📌 Step 3: Draft
    - Write your first version

    📌 Step 4: Review
    - Edit and finalize

    Would you like help starting Step 1?
    """

            return jsonify({"message": reply})
    
    if user_context.get(user_id, {}).get("intent") == FLOW_NAVIGATION:

        context = user_context[user_id]
        step = context.get("step")

        if step == "ask_destination":
            context["destination"] = user_message
            context["step"] = "ask_start"

            return jsonify({"message": "📍 Where are you starting from?"})

        elif step == "ask_start":

            destination = context.get("destination")

            user_context[user_id] = {}

            reply = f"""Sure! 📍 I can help you find it.

    🧭 Destination:
    - {destination}

    🚶 Direction:
    - Start from your location
    - Walk toward main campus road
    - Follow signs to {destination}

    🖼️ Visual guide:
    - I can generate a map image if needed.

    """

            return jsonify({"message": reply})

    if "first-year" in user_message.lower():
        user_context[user_id] = {"year": "first-year"}

    context = user_context.get(user_id, {})

    database_context = f"""
    🎓 STUDENT PROFILE:
    Name: {profile_data.get('name')}
    Semester: {profile_data.get('semester')}

    📚 CURRENT ASSIGNMENTS:
    {assignment_data}

    🏠 HOSTELS:
    {hostel_data}

    💙 EMOTIONAL STATE:
    Recent Mood: {emotional_profile.get('recent_mood', 'Neutral')}

    🧠 RECENT CHAT MEMORY:
    {past_chat_logs}

    📌 Instructions:
    - Use this information naturally when relevant
    - Do NOT repeat raw database data
    - Do NOT dump lists directly
    - Summarize or explain instead
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
        reply = run_agent(messages_payload, user_id)

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

    reply = add_followup(reply)

    reply = clean_response(reply)

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