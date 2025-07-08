import json
import random
from django.http import JsonResponse
from django.shortcuts import render, redirect
import spacy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from django.conf import settings
import re
import spacy
from typing import Dict
from pdfminer.high_level import extract_text
from .models import CandidateInterview


nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = set(["overfitting" ,"limited labeled data","LLMs","SQL","debugging","statistical","backend"
    "python", "java", "javascript", "react", "node.js", "aws", "azure", "gcp", "sql", "nosql",
    "docker", "kubernetes", "git", "api", "rest", "graphql", "frontend", "backend", "fullstack",
    "machine learning", "ai", "deep learning", "data science", "cloud", "agile", "scrum", "devops",
    "testing", "security", "linux", "windows", "mobile", "web", "database", "design patterns",
    "architecture", "communication", "teamwork", "problem solving", "leadership", "management",
    "analytical", "critical thinking", "collaboration", "mentoring", "debugging", "scalability",
    "performance", "optimization", "microservices", "ci/cd", "data structures", "algorithms", "oop"

])

POSITIVE_REMARKS = [
    "Great explanation!", "Excellent clarity!", "That's a strong answer!",
    "Well said!", "Impressive experience!", "You've demonstrated solid understanding!"
]

def home(request):
    return render(request, 'ai_int_app/home.html')

def extract_skills_from_jd(text):
    doc = nlp(text.lower())
    found = set()
    for token in doc:
        if token.text in SKILL_KEYWORDS:
            found.add(token.text)
    for chunk in doc.noun_chunks:
        if chunk.text.strip() in SKILL_KEYWORDS:
            found.add(chunk.text.strip())
    return sorted(found)

def generate_question(topic):
    templates = [
        f"Can you explain your experience with {topic}?",
        # f"What challenges have you faced while working with {topic}?",
        f"How would you rate your proficiency in {topic} and why?",
        # f"Can you share a project where you used {topic}?",
        # f"What are some best practices you follow in {topic}?"
    ]

    return random.choice(templates)

def is_response_good(topic, response):
    keywords = topic.split()
    return all(word.lower() in response.lower() for word in keywords)

def provide_feedback(is_good: bool) -> str:
    if is_good:
        return random.choice(POSITIVE_REMARKS)
    else:
        return "okay....! Consider including more specific key words and details or examples."

data_store ={}

@csrf_exempt
@require_POST
def interview_api(request):
    data = json.loads(request.body)
    jd_text = data.get("jd")
    user_response = data.get("response")
    topic = data.get("topic")

    data_store[topic]=topic 
    
    if jd_text and not topic:
        skills = extract_skills_from_jd(jd_text)
        return JsonResponse({"topics": skills})

    if topic and not user_response:
        question = generate_question(topic)
        data_store[question]=question
        return JsonResponse({"question": question})

    if topic and user_response:
        good = is_response_good(topic, user_response)
        feedback = provide_feedback(good)
        data_store[feedback]=feedback
        return JsonResponse({"feedback": feedback})
    


    return JsonResponse({"feedback": data_store})

    # return JsonResponse({"error": "Invalid input."}, status=400)

# ---------------------
from django.shortcuts import render
from .models import CandidateInterview

def interview_results(request):
    responses = data_store
    return render(request, 'ai_int_app/s.html', {'responses': responses})
# ---------------------

from django.shortcuts import render

def index(request):
    return render(request, "ai_int_app/index.html")

def personal_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        credentials = {
            'interview_01': '123@interview',
            'interview_02': '122@interview',
            'interview_03': '1222@interview',
            'interview_04': '12222@interview'
        }

        if credentials.get(username) == password:
            return redirect('interview_dashboard')
        else:
            return render(request, 'ai_int_app/branch_login.html', {'error': 'Invalid credentials'})

    return render(request, 'ai_int_app/branch_login.html')


def interview_dashboard(request):
    return render(request, "ai_int_app/index.html")

from django.shortcuts import render

def extract_text_from_pdf(file_path: str) -> str:
        """Extracts text from a PDF file."""
        return extract_text(file_path)

def extract_email(text: str) -> str:
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    match = re.search(r"\+?\d[\d\-\s]{8,}\d", text)
    return match.group(0) if match else ""

def extract_name(text: str) -> str:
    doc = nlp(text[:200])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_skills(text: str, skill_list=None) -> list:
    if skill_list is None:
        skill_list = ["python", "java", "sql", "machine learning", "excel", "tensorflow"]
    found = [skill for skill in skill_list if skill.lower() in text.lower()]
    return found

def parse_resume(text: str) -> Dict:
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        # "phone": extract_phone(text),
        "skills": extract_skills(text)
    }


def upload_file(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return render(request, 'ai_int_app/resume.html', {'error': 'No file uploaded'})
        
        uploaded_file = request.FILES['file']
        if not uploaded_file.name.lower().endswith(('.pdf', '.docx')):
            return render(request, 'ai_int_app/resume.html', {'error': 'Invalid file type. Please upload a PDF or DOCX file.'})
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            resume_text = extract_text_from_pdf(file_path) 
            parsed_data = parse_resume(resume_text)
            mail = parsed_data['email']

            if len(parsed_data) > 2:
                return render(request, 'ai_int_app/resume.html', {'file_name': 'pass','mail': mail})
            else:
                return render(request, 'ai_int_app/resume.html', {'error': 'Resume parsing failed. Please check the file.'})
        except Exception as e:
            print(f"Error processing file: {e}")
            return render(request, 'ai_int_app/resume.html', {'error': 'Error processing the file. Please try again.'})
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    return render(request, 'ai_int_app/resume.html')