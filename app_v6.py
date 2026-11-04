from datetime import datetime, timedelta
import json
import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    pass

DATA_FILE = "smart_revision_web.json"
 
def load_data():
  if not os.path.exists(DATA_FILE):
    default_data = {"topics": [], "streak": 0, "last_active": "", "users": [], "history": [], "daily_goal": 3}
    with open(DATA_FILE, "w") as f:
      json.dump(default_data, f, indent=4)
    return default_data
  try:
    with open(DATA_FILE, "r") as f:
      data = json.load(f)
      if "history" not in data:
          data["history"] = []
      if "daily_goal" not in data:
          data["daily_goal"] = 3
      if "topics" not in data:
          data["topics"] = []
      return data
  except:
    return {"topics": [], "streak": 0, "last_active": "", "users": [], "history": [], "daily_goal": 3}

def save_data(data):
  try:
    with open(DATA_FILE, "w") as f:
      json.dump(data, f, indent=4)
  except Exception as e:
    print(f"Error saving data: {e}")

st.set_page_config(
    page_title="MemoryOS - Board Exam Prep", page_icon="🧠", layout="wide"
)

# --- PROFESSIONAL UI & BUTTON STYLING (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .custom-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: 600;
        background-color: #ffffff;
        border: 1px solid #dee2e6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: white !important;
    }
    /* Professional Colorful Buttons Styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

app_data = load_data()
  
# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    saved_user = st.query_params.get("user", "")
    if saved_user:
        st.session_state.logged_in = True
        st.session_state.username = saved_user
    else:
        st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = st.query_params.get("user", "")

if "auth_provider" not in st.session_state:
    st.session_state.auth_provider = None

if "dismiss_alarm" not in st.session_state:
    st.session_state.dismiss_alarm = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🧠 Welcome to MemoryOS</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>10th & 12th Board Exam Spaced Repetition Platform</p>", unsafe_allow_html=True)
        
        enter_email = st.text_input("Enter your email", placeholder="name@example.com")
        if st.button("Continue to App 🚀", use_container_width=True):
            if enter_email and "@" in enter_email:
                st.session_state.logged_in = True
                st.session_state.username = enter_email
                st.query_params["user"] = enter_email
                st.rerun()
            else:
                st.warning("Please enter a valid email!")
else:
    # --- SIDEBAR ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Settings")
    notif_toggle = st.sidebar.toggle("Enable Revision Alerts", value=True)
    
    daily_target_input = st.sidebar.slider("🎯 Daily Target (Chapters)", min_value=1, max_value=10, value=app_data.get("daily_goal", 3))
    if daily_target_input != app_data.get("daily_goal", 3):
        app_data["daily_goal"] = daily_target_input
        save_data(app_data)

    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        if "user" in st.query_params:
            del st.query_params["user"]
        st.rerun()

    # --- TOP HEADER ---
    st.title("🧠 MemoryOS Dashboard")
    st.caption("Smart Revision & AI Powered Study Assistant for Board Exams")

    today = datetime.now().date()
    today_str_check = datetime.now().strftime("%Y-%m-%d")

    # --- TABS FOR CLEAN ORGANIZATION ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Today's Revisions", 
        "📚 Manage Chapters", 
        "🤖 AI Quiz", 
        "📜 Revision History"
    ])

    # --- TAB 1: REVISIONS & METRICS ---
    with tab1:
        due_topics = []
        revised_today_count = sum(1 for h in app_data.get("history", []) if h["date"] == today_str_check and "Revised:" in h["action"])

        for index, item in enumerate(app_data.get("topics", [])):
            try:
                last_date = datetime.strptime(item["last_date"], "%Y-%m-%d").date()
                stage = item["stage"]
                intervals = item["intervals"]
                if stage < len(intervals):
                    due_date = last_date + timedelta(days=intervals[stage])
                    if today >= due_date or item["last_date"] == today_str_check:
                        due_topics.append((index, item, due_date))
            except:
                pass

        # Alarm Alert
        if notif_toggle and due_topics and not st.session_state.dismiss_alarm:
            st.warning(f"🚨 **Alert:** Aapke paas aaj ke liye {len(due_topics)} pending chapters hain!")
            st.markdown("""
                <audio autoplay controls style="height:30px;">
                  <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                </audio>
            """, unsafe_allow_html=True)
            if st.button("🔕 Dismiss Alert"):
                st.session_state.dismiss_alarm = True
                st.rerun()

        # Stats Cards
        c1, c2, c3 = st.columns(3)
        c1.metric("🔥 Current Streak", f"{app_data.get('streak', 0)} Days")
        c2.metric("🎯 Today's Goal Progress", f"{revised_today_count} / {app_data.get('daily_goal', 3)}")
        c3.metric("⏰ Pending Revisions", f"{len(due_topics)}")

        target_goal = app_data.get("daily_goal", 3)
        st.progress(min(revised_today_count / target_goal, 1.0))

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔥 Pending Revisions For Today")
        
        if not due_topics:
            st.success("🎉 Sabhi Revisions Complete Ho Chuke Hain!")
        else:
            for idx, item, due_date_val in due_topics:
                with st.container():
                    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                    col_a, col_b = st.columns([3, 1])
                    col_a.markdown(f"### {item['subject']}: {item['topic']}\n*Due Date: {due_date_val.strftime('%d %b %Y')}*")
                    if col_b.button("✅ Mark Revised", key=f"rev_{idx}", use_container_width=True):
                        app_data["topics"][idx]["last_date"] = today_str_check
                        app_data["topics"][idx]["stage"] += 1
                        app_data["history"].append({"date": today_str_check, "action": f"Revised: {item['subject']} - {item['topic']}"})
                        if app_data.get("last_active") != today_str_check:
                            app_data["streak"] = app_data.get("streak", 0) + 1
                            app_data["last_active"] = today_str_check
                        save_data(app_data)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 2: CHAPTER MANAGEMENT ---
    with tab2:
        st.subheader("📚 Add New Chapter")
        with st.form("add_chapter_form"):
            col_f1, col_f2 = st.columns(2)
            subject = col_f1.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Social Science"])
            chap_no = col_f2.text_input("Chapter Number (e.g. 1)")
            topic_name = st.text_input("Chapter / Topic Name")
            submitted = st.form_submit_button("Save Chapter 🚀", use_container_width=True)

            if submitted:
                if chap_no and topic_name:
                    full_title = f"Ch {chap_no}: {topic_name}"
                    app_data["topics"].append({
                        "subject": subject,
                        "topic": full_title,
                        "last_date": today_str_check,
                        "stage": 0,
                        "intervals": [1, 3, 7, 15, 30]
                    })
                    app_data["history"].append({"date": today_str_check, "action": f"Added: {subject} - {full_title}"})
                    save_data(app_data)
                    st.success(f"'{full_title}' saved successfully!")
                    st.rerun()
                else:
                    st.error("Dono Details Fill Karein!")

        st.markdown("---")
        st.subheader("📈 Subject Progress & Saved Chapters")
        
        all_subjects = ["Physics", "Chemistry", "Maths", "Biology", "English", "Social Science"]
        for sub in all_subjects:
            sub_topics = [t for t in app_data.get("topics", []) if t["subject"] == sub]
            completed = sum(1 for t in sub_topics if t["stage"] >= len(t["intervals"]))
            total = len(sub_topics)
            ratio = completed / total if total > 0 else 0.0
            st.write(f"**{sub}** ({completed}/{total} chapters mastered)")
            st.progress(ratio)

        st.markdown("### 📚 All Saved Topics")
        for index, item in enumerate(app_data.get("topics", [])):
            col_t1, col_t2 = st.columns([4, 1])
            col_t1.write(f"• **{item['subject']}** - {item['topic']} (Stage: {item['stage']})")
            if col_t2.button("🗑️ Delete", key=f"del_{index}", use_container_width=True):
                app_data["topics"].pop(index)
                save_data(app_data)
                st.rerun()

    # --- TAB 3: AI QUIZ ---
    with tab3:
        st.subheader("🤖 AI Instant Quiz Generator")
        ai_subject = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Social Science"], key="tab3_sub")
        ai_topic = st.text_input("Topic Name", key="tab3_top")

        if st.button("Generate Quiz Question ⚡", use_container_width=True):
            if ai_topic:
                with st.spinner("AI sawal taiyar kar raha hai..."):
                    try:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"Create 1 MCQ for Indian student on {ai_subject} chapter {ai_topic} in Aasan Hinglish."
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error("AI Limit Exceeded. Try again in 2 minutes.")
            else:
                st.warning("Topic name enter karein!")

    # --- TAB 4: REVISION HISTORY ---
    with tab4:
        st.subheader("📜 Complete Activity & Revision History")
        history_list = app_data.get("history", [])
        
        if not history_list:
            st.info("Abhi tak koi revision history nahi hai. Jab aap chapters revise karenge, yahan logs dikhenge!")
        else:
            for hist in reversed(history_list):
                st.markdown(f"""
                    <div style="background-color: white; padding: 10px 15px; border-radius: 8px; border-left: 4px solid #4F46E5; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <b>📅 Date:</b> {hist['date']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>📝 Action:</b> {hist['action']}
                    </div>
                """, unsafe_allow_html=True)
            
            if st.button("Clear History 🧹", use_container_width=True):
                app_data["history"] = []
                save_data(app_data)
                st.rerun()
                print("Revision history cleared successfully.")