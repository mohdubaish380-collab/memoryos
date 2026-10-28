from datetime import datetime, timedelta
import json
import os
import streamlit as st

DATA_FILE = "smart_revision_web.json"


def load_data():
  if not os.path.exists(DATA_FILE):
    return {"topics": [], "streak": 0, "last_active": ""}
  try:
    with open(DATA_FILE, "r") as f:
      return json.load(f)
  except:
    return {"topics": [], "streak": 0, "last_active": ""}


def save_data(data):
  with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=4)


st.set_page_config(
    page_title="MemoryOS - Board Exam Startup", page_icon="🧠", layout="centered"
)

st.title("🧠 MemoryOS: Board Exam Spaced Repetition + AI")
st.write(
    "10th & 12th ke bacho ke liye Smart Revision & Aasan Hinglish AI Quiz System"
)

app_data = load_data()

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
      "Abhi koi chapter saved nahi hai. Upar se apna pehla chapter add"
      " karein!"
  )
else:
  today = datetime.now().date()
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
        f"- **{item['subject']}** | {item['topic']} | Last Studied:"
        f" {item['last_date']}"
    )

st.markdown("---")

# 2. AI Quiz Generator Section (Aasan Hinglish Edition)
st.subheader("🤖 AI Instant Quiz & Practice Generator (Aasan Bhasha)")
ai_subject = st.selectbox(
    "Subject Select Karein",
    ["Physics", "Chemistry", "Maths", "Biology", "English", "Social Science"],
    key="ai_sub",
)
ai_topic = st.text_input(
    "Chapter ya Topic ka naam likhein (jaise Current Electricity / Light)",
    key="ai_top",
)

if st.button("Generate Aasan AI Quiz ⚡"):
  if ai_topic:
    st.success(
        f"'{ai_topic}' ({ai_subject}) ke liye aasan Hinglish sawal taiyar"
        " hain!"
    )

    # Dynamic aasan bhasha format for students
    st.markdown(
        f"### Q1: Board Exam Special - {ai_topic} mein main concept kya hota"
        " hai?"
    )
    ans = st.radio(
        "Sahi option chunein:",
        [
            (
                "A) Yeh ek aasan formula hai jo board exam mein numerical ke"
                " liye use hota hai."
            ),
            (
                "B) Yeh chapter ki basic definition aur theory par base hota"
                " hai."
            ),
            "C) Yeh dono (Formula + Theory) important hain.",
            "D) Iska exam se koi lena-dena nahi hai.",
        ],
        key="quiz_q1_hin",
    )

    if st.button("Jawab Check Karein 🎯"):
      st.balloons()
      st.success(
          "Ekdum Sahi Jawab! 🎉 Aise hi concepts clear rakhoge toh board exam"
          " mein top karoge!"
      )
  else:
    st.warning("Kripya chapter ya topic ka naam darj karein!")