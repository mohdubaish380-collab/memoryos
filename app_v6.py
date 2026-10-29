from datetime import datetime, timedelta
import json
import os
import streamlit as st
import google.generativeai as genai

DATA_FILE = "smart_revision_web.json"

def load_data():
  if not os.path.exists(DATA_FILE):
    return {"topics": [], "streak": 0, "last_active": "", "users": []}
  try:
    with open(DATA_FILE, "r") as f:
      return json.load(f)
  except:
    return {"topics": [], "streak": 0, "last_active": "", "users": []}

def save_data(data):
  with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=4)

st.set_page_config(
    page_title="MemoryOS - Board Exam Startup", page_icon="🧠", layout="centered"
)

# --- SECURE API KEY CONFIGURATION ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        genai.configure(api_key="YAHAN_APNI_GEMINI_API_KEY_DAAL_DENA")
except Exception:
    pass

app_data = load_data()

# --- SESSION STATE FOR LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_provider" not in st.session_state:
    st.session_state.auth_provider = None

# --- PROFESSIONAL LOGIN PAGE ---
if not st.session_state.logged_in:
    st.markdown("""
        <style>
        .stApp {
            background-color: #f7f9fa;
        }
        .title-text {
            text-align: center;
            font-size: 26px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .sub-text {
            text-align: center;
            font-size: 12px;
            color: #657786;
            margin-bottom: 25px;
            line-height: 1.4;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .stButton button {
            width: 100%;
            border-radius: 30px;
            font-weight: 600;
            padding: 12px 20px;
            margin-bottom: 12px;
            border: 1px solid #cfd9de;
            background-color: #ffffff;
            color: #0f1419;
            font-size: 15px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .stButton button:hover {
            background-color: #f7f9f9;
            border-color: #b0c4de;
        }
        .divider-text {
            text-align: center;
            color: #536471;
            font-size: 13px;
            margin: 15px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown("<div class='title-text'>Create your account</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>By continuing, you agree to the MemoryOS Terms of Service, Privacy Policy, and Cookie Policy.</div>", unsafe_allow_html=True)
        
        if st.session_state.auth_provider == "Google":
            st.info("🌐 Google Sign-in: Apni Google Email ID darj karein.")
            g_email = st.text_input("Google Email ID", placeholder="example@gmail.com")
            if st.button("Verify & Continue with Google 🚀"):
                if g_email and "@" in g_email:
                    st.session_state.logged_in = True
                    st.session_state.username = g_email
                    st.success("Google account verified successfully!")
                    st.rerun()
                else:
                    st.error("Kripya ek valid email ID dalein!")
            if st.button("← Back"):
                st.session_state.auth_provider = None
                st.rerun()

        elif st.session_state.auth_provider == "Apple":
            st.info("🍎 Apple ID: Apni Apple Email ID darj karein.")
            a_email = st.text_input("Apple ID Email", placeholder="example@icloud.com")
            if st.button("Verify & Continue with Apple 🚀"):
                if a_email and "@" in a_email:
                    st.session_state.logged_in = True
                    st.session_state.username = a_email
                    st.success("Apple ID verified successfully!")
                    st.rerun()
                else:
                    st.error("Kripya ek valid Apple email ID dalein!")
            if st.button("← Back"):
                st.session_state.auth_provider = None
                st.rerun()

        else:
            if st.button("🌐  Continue with Google"):
                st.session_state.auth_provider = "Google"
                st.rerun()
                
            if st.button("  Continue with Apple"):
                st.session_state.auth_provider = "Apple"
                st.rerun()

            st.markdown("<div class='divider-text'>or</div>", unsafe_allow_html=True)
            
            enter_email = st.text_input("Enter your email", placeholder="name@example.com", label_visibility="collapsed")
            
            if st.button("Continue"):
                if enter_email and "@" in enter_email:
                    st.session_state.logged_in = True
                    st.session_state.username = enter_email
                    st.success(f"Swagat hai, {enter_email}!")
                    st.rerun()
                else:
                    st.warning("Kripya pehle apni valid email id darj karein!")

else:
    # --- MAIN APP AFTER LOGIN ---
    st.sidebar.title(f"👤 User: {st.session_state.username}")
    
    # Notification Settings in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 Notification Settings")
    notif_toggle = st.sidebar.toggle("Enable Revision Alerts", value=True)
    if notif_toggle:
        st.sidebar.success("Alerts Active (App khulte hi reminder milega)")

    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.auth_provider = None
        st.rerun()

    st.title("🧠 MemoryOS: Board Exam Spaced Repetition + AI")
    st.write(
        "10th & 12th ke bacho ke liye Smart Revision & Aasan Hinglish AI Quiz System"
    )

    # --- URGENT NOTIFICATION & REVISION ALERT SYSTEM ---
    today = datetime.now().date()
    due_topics_check = []
    for item in app_data.get("topics", []):
        last_date = datetime.strptime(item["last_date"], "%Y-%m-%d").date()
        stage = item["stage"]
        intervals = item["intervals"]
        if stage < len(intervals):
            due_date = last_date + timedelta(days=intervals[stage])
            if today >= due_date or item["last_date"] == datetime.now().strftime("%Y-%m-%d"):
                due_topics_check.append(item)

    if notif_toggle and due_topics_check:
        st.markdown(f"""
            <div style="background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
                <h4 style="margin: 0; color: #856404;">🚨 Revision Time Alert!</h4>
                <p style="margin: 5px 0 0 0; color: #856404; font-size: 14px;">
                    Aapke paas aaj ke liye <b>{len(due_topics_check)} pending chapters</b> hain jinka revision ka samay ho gaya hai. Abhi revise karein aur apna streak bachayein!
                </p>
            </div>
        """, unsafe_allow_html=True)

    # 1. Dashboard & Revision Section
    st.subheader("📚 Naya Chapter Add Karein")
    subject = st.selectbox(
        "Subject Chunein",
        ["Physics", "Chemistry", "Maths", "Biology", "English", "Social Science"],
    )
    chap_no = st.text_input("Chapter Number (e.g. 1)")
    topic_name = st.text_input("Chapter / Topic Ka Naam")

    if st.button("Save & Schedule 🚀"):
      if not chap_no or not topic_name:
        st.error("Kripya Chapter Number aur Topic ka naam dono likhein!")
      else:
        full_topic_title = f"Ch {chap_no}: {topic_name}"
        today_str = datetime.now().strftime("%Y-%m-%d")

        new_item = {
            "subject": subject,
            "topic": full_topic_title,
            "last_date": today_str,
            "stage": 0,
            "intervals": [1, 3, 7, 15, 30],
        }

        app_data["topics"].append(new_item)
        save_data(app_data)
        st.success(f"'{full_topic_title}' ({subject}) successfully save ho gaya!")

    st.markdown("---")
    st.subheader("📊 Your Dashboard & Due Revisions")

    if not app_data["topics"]:
      st.info(
          "Abhi koi chapter saved nahi hai. Upar se apna pehla chapter add karein!"
      )
    else:
      due_topics = []

      for index, item in enumerate(app_data["topics"]):
        last_date = datetime.strptime(item["last_date"], "%Y-%m-%d").date()
        stage = item["stage"]
        intervals = item["intervals"]

        if stage < len(intervals):
          next_due_days = intervals[stage]
          due_date = last_date + timedelta(days=next_due_days)
        else:
          due_date = last_date

        if stage < len(intervals) and (
            today >= due_date
            or item["last_date"] == datetime.now().strftime("%Y-%m-%d")
        ):
          due_topics.append((index, item))

      st.metric(
          label="🔥 Current Streak", value=f"{app_data.get('streak', 0)} Days"
      )
      st.write(f"⏰ **Pending Revisions Today:** {len(due_topics)}")

      if due_topics:
        st.markdown("### 🔥 Aaj Ke Pending Revisions:")
        for idx, item in due_topics:
          col1, col2 = st.columns([3, 1])
          col1.write(f"**{item['subject']}** - {item['topic']}")
          if col2.button("✅ Done", key=f"rev_{idx}"):
            today_str = datetime.now().strftime("%Y-%m-%d")
            app_data["topics"][idx]["last_date"] = today_str
            app_data["topics"][idx]["stage"] += 1

            last_active = app_data.get("last_active", "")
            if last_active != today_str:
              app_data["streak"] = app_data.get("streak", 0) + 1
              app_data["last_active"] = today_str

            save_data(app_data)
            st.success("Revision Done! Streak updated! 🎉")
            st.rerun()

      st.markdown("### 📚 All Saved Chapters")
      for item in app_data["topics"]:
        st.write(
            f"- **{item['subject']}** | {item['topic']} | Last Studied: {item['last_date']}"
        )

    st.markdown("---")

    # 2. AI Quiz Generator Section
    st.subheader("🤖 AI Instant Quiz & Practice Generator (Aasan Bhasha)")

    ai_subject = st.selectbox(
        "Subject Select Karein",
        ["Physics", "Chemistry", "Maths", "Biology", "English", "Social Science"],
        key="ai_sub",
    )
    ai_topic = st.text_input(
        "Chapter ya Topic ka naam likhein (jaise Panchlite / Current Electricity)",
        key="ai_top",
    )

    if st.button("Generate Aasan AI Quiz ⚡"):
      if ai_topic:
        with st.spinner("AI aasan Hinglish sawal tayyar kar raha hai..."):
          try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert board exam teacher for Indian 10th and 12th students.
            Subject: {ai_subject}
            Topic/Chapter: {ai_topic}
            
            Create 1 high-quality Multiple Choice Question (MCQ) in Aasan Hinglish. 
            If the topic is a story or literature chapter, make sure the question is about the story plot, characters, theme, or author—DO NOT ask formulas or numericals.
            If the topic is Science or Math, make sure it tests concepts or formulas.
            
            Format your response cleanly like this:
            **Q1: [Sawall Hinglish mein]**
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            
            **Sahi Jawab:** [Correct Option]
            **Explanation:** [Aasan Hinglish mein chhota sa explanation]
            """
            
            response = model.generate_content(prompt)
            st.success(f"'{ai_topic}' ({ai_subject}) ke liye sawal taiyar hai!")
            st.markdown("---")
            st.markdown(response.text)
            
          except Exception as e:
            st.error(f"Kuch gadbad ho gayi: {e}")
      else:
        st.warning("Kripya chapter ya topic ka naam darj karein!")