import json
import re
from datetime import datetime
from io import BytesIO
from uuid import uuid4
from streamlit import button
from streamlit_card import card
import google.generativeai as genai
import requests
import streamlit as st
from PIL import Image
from streamlit_card import card
from streamlit_option_menu import option_menu
from pypdf import PdfReader

st.set_page_config(
	page_title="LearnMate.ai", page_icon="✧˖°📖🌐"
)

with st.sidebar:
	pages = option_menu("Navigate to",["Intro", "About", "Exam Prepation Sources", "Resume Analyzer", "Quiz Practice"])
API_KEY = st.sidebar.text_input(
	"Enter the Google Gemini api key (You can get or create gemini api key [here](https://makersuite.google.com/app/apikey)): ",
	type="password")

genai.configure(api_key=API_KEY)


def load_gemini_model():
	return genai.GenerativeModel('gemini-pro')


model = load_gemini_model()


def parse_duration(duration_str):
	match = re.search(r'\d+', duration_str)
	if match:
		return int(match.group())
	return 60


def get_gemini_ai_recommendations(subject, level, days_left):
	prompt = f"""
    Suggest 3 study resources for a student with the following criteria:
    - Subject: {subject}
    - Preparation level: {level}
    - Days left until exam: {days_left}

    Consider the time constraint and preparation level.
    If time is short, prioritize valid and available quick review materials from valid websites.
    For longer time frames, suggest more available and accurate comprehensive resources.
    Please don't give unavailable resources appropriate (youtube videos, course, article)
    Use the following JSON format:
    [
        {{
            "title": "Resource Title",
            "type": "Resource Type (e.g., youtube video, course, article)",
            "duration": "Estimated study time in minutes (just the number)",
            "url": "URL of the resource",
            "image_url": "Url of an image representing the resource"
        }},
		{{
            // Second recommendation
        }},
        {{
            // Third recommendation
        }}
    ]
    """
	
	response = model.generate_content(prompt)
	
	try:
		recommendations = json.loads(response.text)
		for rec in recommendations:
			rec['duration'] = parse_duration(str(rec['duration']))
		return recommendations
	except json.JSONDecodeError:
		st.error("Failed to parse AI response. Please try again.")
		return []


def generate_study_schedule(subjects, levels, exam_dates):
	schedule = []
	start_date = datetime.now().date()
	
	for subject, level, exam_date in zip(subjects, levels, exam_dates):
		days_until_exam = (exam_date - start_date).days
		recommendations = get_gemini_ai_recommendations(subject, level, days_until_exam)
		for rec in recommendations:
			schedule.append({
				'subject': subject,
				'title': rec['title'],
				'duration': rec['duration'],
				'url': rec['url'],
				'image_url': rec['image_url'],
				'type': rec['type']
			})
	
	st.session_state['study_schedule'] = schedule
	return schedule


# return schedule

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
				key=f"card_{index}_{item['title']}_{uuid4()}",  # Ensure the key is unique
				styles={"card": {"width": "100%", "height": "100%", "border-radius": "10px",
								 "box-shadow": "0 0 10px rgba(0,0,0,0.1)"}}
			)
			with st.expander("More Info", expanded=False):
				st.write(f"Subject: {item['subject']}")
				st.write(f"Duration: {item['duration']} minutes")
				st.write(f"Type: {item['type']}")
				st.write(f"URL: {item['url']}")



def extract_resume_text(file):
	"""Extract text from PDF or DOCX files."""
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
	
	try:
		response = model.generate_content(prompt)
		return response.text
	except Exception as e:
		st.error(f"Error processing the AI request: {e}")
		return "No analysis available."


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
			st.session_state['chat_history'].append({'role': 'user', 'content': selected_option})
			
			if selected_option == question['correct_answer']:
				st.session_state['score'] += 1
			
			ai_response = chat_with_gemini(question, selected_option)
			st.session_state['chat_history'].append({'role': 'ai', 'content': ai_response})
			
			st.session_state['current_question_index'] += 1
			
			if st.session_state['current_question_index'] < len(st.session_state['quiz_questions']):
				pass
			else:
				st.success("Quiz completed!")
				st.write(f"You scored {st.session_state['score']}/{len(st.session_state['quiz_questions'])}!")
				st.session_state['quiz_active'] = False

def main():
	if 'study_schedule' not in st.session_state:
		st.session_state['study_schedule'] = None
	
	if pages == "Intro":
		st.snow()
		st.title("LearnMate.ai: :rainbow[Study smarter with an AI study assistant]")
		
		st.subheader("Are you ready to elevate your "
					 "learning to the next level? Welcome to the "
					 "future of education with LearnMate.ai, your "
					 "personal AI learning buddy")
		
		st.write(
			"""
			**LearnMate.ai** is inspired by the challenges that students
			face while preparing for multiple exams across various subjects.
			We recognized the need for a personalized, AI-driven solution
			that could help students to organize their study time efficiently,
			taking into account their current knowledge level, preparation level
			and the time available before exams.
			
			This also provides additional features like Resume Analysis and Quiz practices
			"""
		)
	
	elif pages == "About":
		st.subheader("What it does?")
		st.write(
			"""
			**LearnMate.ai** is a revolutionary study planning tool that empowers
			students to achieve academic success. By inputting their subjects,
			preparation levels, and exam dates, students can harness the power
			of Google's Gemini Al to receive personalized study resource
			recommendations. The tool then generates a visually appealing and
			Interactive study schedule, complete with a variety of resources such
			as videos, articles, and practice problems. To enhance engagement and
			understanding, study materials are presented in an engaging card format,
			accompanied by informative Images and estimated completion times.
			Aso this integrates resume analyzer and quiz practice features.
			"""
		)
		st.markdown(
			"""
			---
			"""
		)
		st.subheader("LearnMate.ai takes study planning to the next level. Here's how:")
		st.write(
			"""
			1) Seamless Al Integration: We leverage Google's powerful Gemini Al to analyze
			your inputs, creating a smooth and transparent bridge between user data and
			personalized recommendations.

			2) Intuitive Interface, Clear Information: Our user interface is designed with
			simplicity in mind. Even complex information is presented in a way that's easy
			to understand and navigate, keeping you focused on your goals.

			3) Relevant, Diverse Recommendations: LearnMate.al goes beyond the obvious.
			We ensure the Al recommendations are not only relevant to your learning style
			and needs but also diverse, offering a variety of resources to keep your studies engaging.

			4) Visually Appealing Cards: Forget boring text lists! LearnMate.al uses engaging card formats
			for study materials. These cards consistently display image URLS, providing a visually stimulating
			experience with estimated completion times for informed scheduling.

			5) Balance Is Key: We understand the importance of providing detailed information without overwhelming you.
			LearnMate.al offers a clean and uncluttered interface, striking the perfect balance between content richness
			and user experience.
			
			6) This provides Resume Analysis as an additional feature which is crucial to get
			shortlisted for the interviews. This also suggests **key skills lacking, resume
			improvement suggestions and learning resources.
			
			7) In the Quiz Section, you can select the job role to practice the quiz and also select the difficulty level
			With LearnMate.al, you get a study planning tool that's as powerful as it is user- friendly, empowering you to
			conquer your academic journey!
			""")
	
	
	elif pages == "Exam Prepation Sources":
		
		st.header("Get started")
		st.markdown(
			"""
			---
			"""
		)
		
		min_year = datetime(2021, 1, 1)
		max_year = datetime(2056, 12, 31)
		acdemic_year = st.date_input("Select the academic year", min_value=min_year, max_value=max_year)
		
		num_subjects = st.number_input("Number of subjects", min_value=1, max_value=10, value=3)
		subjects = []
		levels = []
		exam_dates = []
		
		for i in range(num_subjects):
			col1, col2, col3 = st.columns(3)
			with col1:
				subject = st.text_input(f"Subject {i + 1}")
				subjects.append(subject)
			with col2:
				level = st.selectbox(f"Preparation level for {subject}", ["bad", "good", "great"], key=f"level_{i}")
				levels.append(level)
			with col3:
				exam_date = st.date_input(f"Exam date for {subject}", key=f"exam_date_{i}")
				exam_dates.append(exam_date)
		
		if st.button("Find Study Resources"):
			if all(subjects) and all(exam_date > datetime.now().date() for exam_date in exam_dates):
				with st.spinner("Generating study schedule..."):
					schedule = generate_study_schedule(subjects, levels, exam_dates)
				# display_study_schedule(schedule)
			else:
				st.error("Please fill in all subjects and select future exam dates.")
		
		if st.session_state['study_schedule']:
			display_study_schedule(st.session_state['study_schedule'])
	
	elif pages == "Resume Analyzer":
		st.subheader("Resume Analyzer")
		
		uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
		
		job_role = st.text_input("Enter the job role you are applying for")
		if st.button("Analyze your resume"):
			resume_text = extract_resume_text(uploaded_file)
			
			with st.spinner("Analyzing résumé..."):
				analysis = get_resume_analysis(resume_text, job_role)
			
			st.markdown(f"### Résumé Analysis for {job_role}")
			st.markdown(analysis)

			
		else:
			st.info("Please upload a resume and enter the job role.")
	
	elif pages == "Quiz Practice":
		quiz_app()


if __name__ == "__main__":
	main()
