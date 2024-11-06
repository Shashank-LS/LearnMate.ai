<img src="https://github.com/user-attachments/assets/394e565e-c569-4ea2-b13c-2b4ef7266afa" style="width:700px;height:400px;"> 

[![language](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=black&labelColor=green)](https://www.jetbrains.com/pycharm/)
[![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
<a href="https://mail.google.com/mail/?view=cm&fs=1&to=hegdeanirudh2003@gmail.com">
  <img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white">
</a>

## Overview
**LearnMate.ai** is inspired by the challenges that students face while preparing for multiple exams across various subjects.
We recognized the need for a personalized, AI-driven solution that could help students to organize their study time efficiently,
taking into account their current knowledge level, preparation level and the time available before exams.
This also provides additional features like Resume Analysis and Quiz practices


## Demo
https://youtu.be/E4OwwxeHJ3Q


## Intro
**LearnMate.ai** is a revolutionary study planning tool that empowers students to achieve academic success. By inputting their subjects,
preparation levels, and exam dates, students can harness the power of Google's Gemini Al to receive personalized study resource
recommendations. The tool then generates a visually appealing and Interactive study schedule, complete with a variety of resources such
as videos, articles, and practice problems. To enhance engagement and understanding, study materials are presented in an engaging card format,
accompanied by informative Images and estimated completion times. Aso this integrates resume analyzer and quiz practice features.


## Features
### LearnMate.ai takes study planning to the next level. Here's how:
1) Seamless Al Integration: We leverage Google's powerful Gemini Al to analyze
   your inputs, creating a smooth and transparent bridge between user data and
   personalized recommendations.

3) Intuitive Interface, Clear Information: Our user interface is designed with
   simplicity in mind. Even complex information is presented in a way that's easy
   to understand and navigate, keeping you focused on your goals.

4) Relevant, Diverse Recommendations: LearnMate.al goes beyond the obvious.
   We ensure the Al recommendations are not only relevant to your learning style
   and needs but also diverse, offering a variety of resources to keep your studies engaging.

5) Visually Appealing Cards: Forget boring text lists! LearnMate.al uses engaging card formats
   for study materials. These cards consistently display image URLS, providing a visually stimulating
   experience with estimated completion times for informed scheduling.

6) Balance Is Key: We understand the importance of providing detailed information without overwhelming you.
   LearnMate.al offers a clean and uncluttered interface, striking the perfect balance between content richness
   and user experience.
			
7) This provides Resume Analysis as an additional feature which is crucial to get shortlisted for the interviews.
   This also suggests **key skills lacking**, **resume improvement suggestions** and **learning resources**.
			
8) In the Quiz Section, you can select the job role to practice the quiz and also select the difficulty level
   With LearnMate.al, you get a study planning tool that's as powerful as it is user-friendly, empowering you to
   conquer your academic journey!


## AWS Diagram:
![image](https://github.com/user-attachments/assets/018e2593-8815-4caa-ad4f-1a61c36fc103)

The application has been deployed on AWS Elastic BeansTalk using Docker image.
You can check out the deployed link: [learnmate-ai.us-east-1.elasticbeanstalk.com](http://learnmate-ai.us-east-1.elasticbeanstalk.com/) or [http://50.19.33.106](http://50.19.33.106)


## Getting Started
### Prerequisites
- Python 3.9+
- Streamlit
- Google Generative AI API access
- Docker
### API/Service Details
- Go to https://aistudio.google.com/app/apikey
- Create API key.
- Navigate to Google Cloud->Actvate your account->Under API & Services->Enable Generative Language API.
- Copy the API key in the application.


### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/anirudh-hegde/LearnMate.ai.git
   cd LearnMate.ai
   python3 -m venv venv
   pip install -r requirements.txt
   
2. Run the app:
   ```bash
   python3 -m streamlit run learnmate.py

Also you can checkout Docker image on DockerHub: [learnmate-ai](https://hub.docker.com/repository/docker/anirudh06/learnmate-ai/general)


## Conclusion
Congratulations! You have successfully run the application 🚀️.

To view the LearnMate.ai app 👉 https://learnmate-ai.streamlit.app/
