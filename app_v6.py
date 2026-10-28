import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="MemoryOS - Smart Hinglish Quiz", page_icon="🧠", layout="centered")

st.title("🧠 MemoryOS: Smart Hinglish Quiz Generator")
st.write("Local students ke liye aasan Hinglish mein board exam ki tayyari!")

# API Key handling (Secrets ya Direct Input)
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    st.markdown("---")
    api_key = st.text_input("🔑 Apni Gemini API Key yahan daalein (Sirf ek baar dalni hai):", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    # Category Selection
    category = st.selectbox(
        "Padhai ki Category Chunein:",
        ["Literature / Story (Jaise Panchlite, Kahani, Chapter Summary)", "Science / Math / Physics (Numericals & Formulas)"]
    )
    
    subject = st.text_input("Subject ka Naam likhein (Jaise: English, Hindi, Physics):")
    topic = st.text_input("Chapter ya Topic ka naam likhein (Jaise: Panchlite, Current Electricity):")
    
    if st.button("🚀 Generate Smart Aasan AI Quiz"):
        if subject and topic:
            with st.spinner("AI smart sawal tayyar kar raha hai... thoda intezaar karein!"):
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    if "Literature" in category:
                        prompt = f"""
                        You are an expert UP Board / CBSE teacher. The student is studying a Literature/Story chapter.
                        Subject: {subject}
                        Topic/Story: {topic}
                        
                        Create 1 very easy multiple-choice question (MCQ) in Aasan Hinglish specifically focused on the story plot, characters, theme, or author of this literature chapter. DO NOT ask formula or numerical questions because this is a story/literature chapter.
                        
                        Format the response clearly:
                        Q1: [Smart question about the story/chapter in Hinglish]
                        A) [Option 1]
                        B) [Option 2]
                        C) [Option 3]
                        D) [Option 4]
                        Correct Answer: [Option letter and text]
                        Explanation: [Aasan Hinglish mein chhota sa explanation ki yeh answer kyun hai]
                        """
                    else:
                        prompt = f"""
                        You are an expert UP Board / CBSE science/math teacher. 
                        Subject: {subject}
                        Topic: {topic}
                        
                        Create 1 conceptual or formula-based MCQ question in Aasan Hinglish suitable for board exams.
                        
                        Format the response clearly:
                        Q1: [Clear question or numerical concept in Hinglish]
                        A) [Option 1]
                        B) [Option 2]
                        C) [Option 3]
                        D) [Option 4]
                        Correct Answer: [Option letter and text]
                        Explanation: [Aasan Hinglish mein formula ya concept ka explanation]
                        """
                    
                    response = model.generate_content(prompt)
                    
                    st.success(f"'{topic}' ({subject}) ke liye smart sawal tayyar hai!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Kuch gadbad ho gayi: {e}")
        else:
            st.warning("Bhai, kripya Subject aur Topic dono ka naam bharein!")
else:
    st.info("👆 Kripya upar diye gaye box mein apni Gemini API Key paste karein taaki app khul jaye.")