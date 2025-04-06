import os
import re
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from .models import JobRole, Resume, ResumeScore
import groq
import json

def index(request):
    job_roles = JobRole.objects.all()
    # If no job roles exist, create some sample ones
    if not job_roles.exists():
        sample_roles = [
            {
                "name": "Software Engineer",
                "description": "Develops software solutions and applications."
            },
            {
                "name": "Data Scientist",
                "description": "Analyzes and interprets complex data."
            },
            {
                "name": "Product Manager",
                "description": "Oversees product development and strategy."
            },
            {
                "name": "UX/UI Designer",
                "description": "Designs user experiences and interfaces."
            },
            {
                "name": "DevOps Engineer",
                "description": "Manages infrastructure and deployment processes."
            }
        ]
        for role in sample_roles:
            JobRole.objects.create(name=role["name"], description=role["description"])
        job_roles = JobRole.objects.all()
    
    return render(request, 'scorer/index.html', {'job_roles': job_roles})

def extract_text_from_resume(uploaded_file):
    # In a real implementation, you'd use libraries like PyPDF2, docx2txt, etc.
    # For this example, we'll assume the file is plain text or handle it simplistically
    try:
        content = uploaded_file.read().decode('utf-8')
        return content
    except:
        # If decoding fails, return empty string
        return ""

def score_resume(request):
    if request.method == 'POST':
        try:
            job_role_id = request.POST.get('job_role')
            experience_years = request.POST.get('experience_years')
            resume_file = request.FILES.get('resume')
            
            if not all([job_role_id, experience_years, resume_file]):
                messages.error(request, "All fields are required")
                return redirect('scorer:index')
            
            # Get the job role
            job_role = JobRole.objects.get(id=job_role_id)
            
            # Extract text from resume
            resume_content = extract_text_from_resume(resume_file)
            
            # Save the resume
            resume = Resume.objects.create(
                file=resume_file,
                content=resume_content
            )
            
            # Score the resume using Groq
            score, feedback = analyze_resume_with_groq(
                resume_content, 
                job_role.name, 
                job_role.description, 
                experience_years
            )
            
            # Save the score
            resume_score = ResumeScore.objects.create(
                resume=resume,
                job_role=job_role,
                experience_years=int(experience_years),
                score=score,
                feedback=feedback
            )
            
            return redirect('scorer:result', score_id=resume_score.id)
        
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('scorer:index')
    
    return redirect('scorer:index')

def analyze_resume_with_groq(resume_content, job_role, job_description, experience_years):
    try:
        # Initialize the Groq client
        client = groq.Groq(api_key=settings.GROQ_API_KEY)
        
        # Prepare the prompt
        prompt = f"""
        You are an expert resume evaluator. Analyze the following resume for a {job_role} position requiring {experience_years} years of experience.
        
        Job Description: {job_description}
        
        Resume Content:
        {resume_content}
        
        Please evaluate this resume on a scale of 0-100, where 100 is perfect for the role. Consider:
        1. Relevant skills for the role
        2. Experience matching the required {experience_years} years
        3. Education and certifications
        4. Overall fit for the position
        
        Provide a numeric score and detailed feedback in JSON format as follows:
        {{
            "score": [numeric score between 0-100],
            "feedback": [detailed feedback with strengths and areas for improvement]
        }}
        """
        
        # Use Groq with Llama 3 model
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert resume evaluator."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",  # Using Llama 3 model
            max_tokens=2000
        )
        
        # Extract JSON response
        response_text = chat_completion.choices[0].message.content
        
        # Try to extract JSON from the response
        json_match = re.search(r'{.*}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            return result.get("score", 50), result.get("feedback", "No detailed feedback provided")
        else:
            return 50, "Could not extract structured feedback. Please try again."
    
    except Exception as e:
        # Log the error and return default values
        print(f"Error in Groq analysis: {str(e)}")
        return 50, f"Error analyzing resume: {str(e)}"

def result(request, score_id):
    try:
        score = ResumeScore.objects.get(id=score_id)
        return render(request, 'scorer/result.html', {'score': score})
    except ResumeScore.DoesNotExist:
        messages.error(request, "Score not found")
        return redirect('scorer:index')