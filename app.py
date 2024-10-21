import streamlit as st
import google.generativeai as genai
import os
import json
import re
import requests
from datetime import datetime
from streamlit_card import card
from PyPDF2 import PdfReader
import docx as docx

# Set up Gemini API - Add your correct API key here
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBXKl1WCCtS2qy6o_eUE6WsyKwOlB3MlcM'  # Replace with your actual API key
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Set up LM Studio API
LM_STUDIO_URL = 'http://192.168.247.1:1234/v1/chat/completions'  # Replace with your actual LM Studio URL

def generate_lm_response(prompt):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "model": "Meta-Llama-3.1-8B-lnstruct-GGUF",  # Specify your model here
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(LM_STUDIO_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error("Error communicating with LM Studio.")
        return None

@st.cache_resource
def load_gemini_model():
    return genai.GenerativeModel('gemini-pro')

model = load_gemini_model()

def parse_duration(duration_str):
    match = re.search(r'\d+', duration_str)
    if match:
        return int(match.group())
    return 60

def get_gemini_recommendations(subject, level, days_left):
    prompt = f"""
    Suggest 3 study resources for a student with the following criteria:
    - Subject: {subject}
    - Preparation level: {level}
    - Days left until exam: {days_left}

    Consider the time constraint and preparation level. 
    If time is short, prioritize quick review materials. For longer time frames, suggest more comprehensive resources.

    Use the following JSON format for the response only, without any extra commentary:
    [
        {{
            "title": "Resource Title",
            "type": "Resource Type (e.g., video, course, article)",
            "duration": "Estimated study time in minutes (just the number)",
            "url": "URL of the resource",
            "image_url": "URL of an image representing the resource"
        }},
        {{}} , {{}}
    ]
    """
    response_text = model.generate_content(prompt).text

    # Attempt to parse only the JSON part
    try:
        start_index = response_text.index('[')  # Find the start of the JSON array
        json_str = response_text[start_index:]  # Extract the JSON string
        recommendations = json.loads(json_str)  # Parse the JSON string
        for rec in recommendations:
            rec['duration'] = parse_duration(str(rec['duration']))
        return recommendations
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Failed to parse AI response: {e}")
        return []
    except ValueError:
        st.error("Could not find valid JSON in the response.")
        return []

def generate_study_schedule(subjects, levels, exam_dates):
    schedule = []
    start_date = datetime.now().date()

    for subject, level, exam_date in zip(subjects, levels, exam_dates):
        days_until_exam = (exam_date - start_date).days
        recommendations = get_gemini_recommendations(subject, level, days_until_exam)
        for rec in recommendations:
            schedule.append({
                'subject': subject,
                'title': rec['title'],
                'duration': rec['duration'],
                'url': rec['url'],
                'image_url': rec['image_url'],
                'type': rec['type']
            })

    # Store the schedule in session_state
    st.session_state['study_schedule'] = schedule
    return schedule

def display_study_schedule(schedule):
    st.subheader("Your Study Schedule")
    cols = st.columns(3)
    for index, item in enumerate(schedule):
        with cols[index % 3]:
            icon = "📺" if item['type'].lower() == 'video' else "📄" if item['type'].lower() == 'article' else "🎓"
            card(
                title=f"{icon} {item['title']}",
                text=f"{item['duration']} minutes | {item['type']}",
                image=item['image_url'],
                url=item['url'],
                key=f"card_{index}_{item['title']}",  # Ensure the key is unique
                styles={"card": {"width": "100%", "height": "100%", "border-radius": "10px",
                                 "box-shadow": "0 0 10px rgba(0,0,0,0.1)"}}
            )
            with st.expander("More Info", expanded=False):
                st.write(f"Subject: {item['subject']}")
                st.write(f"Duration: {item['duration']} minutes")
                st.write(f"Type: {item['type']}")
                st.write(f"URL: {item['url']}")

def extract_resume_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format")
    return text

def get_resume_analysis(resume_text, job_role):
    prompt = f"""
    A user has applied for the job role of {job_role}. Their résumé contains the following information:

    {resume_text}

    Provide a concise and human-readable analysis of the following:
    - List the most important skills the user lacks in one sentence.
    - Short suggestions for improving the résumé in one to two sentences.
    - Recommend two learning resources for the user to improve their knowledge (title and URL).

    The response should be formatted for readability with proper headings and in plain text.
    """
    response_text = generate_lm_response(prompt)

    try:
        # Format the output nicely
        analysis = response_text.strip()
        formatted_analysis = analysis.replace('###', '**').replace('##', '**')  # Adjust markdown for better format
        return formatted_analysis
    except json.JSONDecodeError:
        st.error("There was an error parsing the AI's response. Please try again.")
        return "No analysis available."

# Quiz Section
def fetch_quiz_questions_gemini(job_role, difficulty_level):
    prompt = f"""
    Generate a quiz with 10 questions for the job role of {job_role} at {difficulty_level} difficulty.
    Each question should have 4 options (A, B, C, D), and specify the correct answer.
    Respond ONLY with a JSON array of objects like this:
    [
        {{"question": "Question text", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option A"}} 
    ]
    """
    response_text = model.generate_content(prompt).text

    try:
        questions = json.loads(response_text)
        return questions
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Failed to parse AI response: {e}")
        return None


def chat_with_gemini(question, user_answer=None):
    if user_answer:
        prompt = f"User answered: {user_answer}. The question was: {question['question']}."
    else:
        prompt = f"Question: {question['question']}."

    response = model.generate_content(prompt).text
    return response


def quiz_app():
    st.header("Quiz Section")

    if 'quiz_questions' not in st.session_state:
        job_role = st.text_input("Enter the job role for the quiz")
        difficulty_level = st.selectbox("Select the difficulty level", ["easy", "medium", "hard"])

        if st.button("Start Quiz"):
            if job_role:
                st.session_state['quiz_questions'] = fetch_quiz_questions_gemini(job_role, difficulty_level)
                st.session_state['current_question_index'] = 0
                st.session_state['score'] = 0
                st.session_state['chat_history'] = []
                st.session_state['quiz_active'] = True

                if st.session_state['quiz_questions'] is not None:
                    st.success("Quiz started! Chat with the AI below.")
                    display_chat_interface()
                else:
                    st.warning("No questions available. Please try again.")
            else:
                st.warning("Please enter a job role for the quiz.")
    else:
        display_chat_interface()


def display_chat_interface():
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Display chat history
    for entry in st.session_state['chat_history']:
        if entry['role'] == 'ai':
            st.markdown(f"**AI:** {entry['content']}")
        else:
            st.markdown(f"**You:** {entry['content']}")

    if 'current_question_index' in st.session_state and st.session_state['quiz_active']:
        question = st.session_state['quiz_questions'][st.session_state['current_question_index']]
        st.markdown(f"**Q{st.session_state['current_question_index'] + 1}: {question['question']}**")

        options = question['options']
        selected_option = st.selectbox("Choose an option:", options, key="option_selector")

        if st.button("Submit Answer"):
            # Log user's answer
            st.session_state['chat_history'].append({'role': 'user', 'content': selected_option})

            # Check if the answer is correct
            if selected_option == question['correct_answer']:
                st.session_state['score'] += 1

            # Log AI's response
            ai_response = chat_with_gemini(question, selected_option)
            st.session_state['chat_history'].append({'role': 'ai', 'content': ai_response})

            # Move to the next question
            st.session_state['current_question_index'] += 1

            # Check if there are more questions
            if st.session_state['current_question_index'] < len(st.session_state['quiz_questions']):
                # No need to rerun the script, Streamlit will automatically re-run when the button is clicked
                pass
            else:
                st.success("Quiz completed!")
                st.write(f"You scored {st.session_state['score']}/{len(st.session_state['quiz_questions'])}!")
                st.session_state['quiz_active'] = False  # End quiz

# Main App
def main():
    st.title("LearnMate.ai")

    menu = ["Home", "Study Planner", "Resume Analysis", "Quiz"]
    choice = st.sidebar.selectbox("Select a section", menu)

    if choice == "Home":
        st.write("Welcome to LearnMate.ai! Please select an option from the sidebar.")

        st.subheader("About LearnMate.ai")
        st.write("""
        **LearnMate.ai** is an AI-powered learning and career assistant designed to help students and professionals excel in their academic and career journeys. With the integration of advanced language models like Gemini and LLaMA, LearnMate.ai offers personalized study plans, résumé analysis, and interactive quizzes to streamline your preparation for exams or job interviews.

        ### Key Features:
        - **Study Planner**: Create tailored study schedules based on your subjects, preparation level, and exam dates. Get personalized resource recommendations to optimize your learning in the time you have.

        - **Résumé Analyzer**: Upload your résumé and receive a detailed skills gap analysis. Based on the job role you're targeting, our AI provides feedback on how to improve your résumé and offers learning resources to fill any knowledge gaps.

        - **Interactive Quizzes**: Test your knowledge with custom quizzes based on your job role or subject. Each quiz is dynamically generated with questions of varying difficulty, providing immediate feedback to help you gauge your understanding.

        ### Why LearnMate.ai?
        - **Personalized Recommendations**: Whether you’re a student preparing for exams or a professional looking to upskill, LearnMate.ai offers customized study and career guidance tailored to your needs.

        - **AI-Driven Insights**: Using cutting-edge AI models, LearnMate.ai analyzes your résumé, helping you highlight your strengths and improve areas where you may need more expertise.

        - **Interactive Learning**: Engaging quizzes make learning fun and effective, while real-time AI feedback ensures continuous improvement.

        Whether you’re preparing for exams, applying for jobs, or simply enhancing your knowledge, LearnMate.ai is your companion in achieving success!
        """)

    elif choice == "Study Planner":
        num_subjects = st.number_input("Enter number of subjects:", min_value=1, value=1)
        subjects = []
        levels = []
        exam_dates = []

        for i in range(num_subjects):
            subject = st.text_input(f"Enter subject {i + 1}:")
            level = st.selectbox(f"Select your preparation level for {subject}:", ["beginner", "intermediate", "advanced"], key=f"level_{i}")
            exam_date = st.date_input(f"Select your exam date for {subject}:", key=f"exam_date_{i}")
            subjects.append(subject)
            levels.append(level)
            exam_dates.append(exam_date)

        if st.button("Generate Study Schedule"):
            if subjects and levels and exam_dates:
                schedule = generate_study_schedule(subjects, levels, exam_dates)
                display_study_schedule(schedule)

    elif choice == "Resume Analysis":
        st.subheader("Résumé Analyzer")

        resume_file = st.file_uploader("Upload your résumé", type=["pdf", "docx"])
        job_role = st.text_input("Enter the job role you're applying for:")

        if st.button("Analyze Résumé"):
            if resume_file and job_role:
                resume_text = extract_resume_text(resume_file)
                analysis = get_resume_analysis(resume_text, job_role)
                st.markdown(analysis)

    elif choice == "Quiz":
        quiz_app()

if __name__ == "__main__":
    main()
