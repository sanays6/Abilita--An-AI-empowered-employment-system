import json
import urllib.request
import os
from django.conf import settings

def _get_api_config():
    api_key = None
    model_name = "llama-3.1-8b-instant"
    try:
        from admin_panel.models import AIConfiguration
        config = AIConfiguration.objects.first()
        if config:
            if config.api_key:
                api_key = config.api_key
            if config.model_name:
                model_name = config.model_name
    except Exception:
        pass
        
    if not api_key:
        api_key = getattr(settings, 'GROQ_API_KEY', None) or os.environ.get('GROQ_API_KEY')
        
    return api_key, model_name

def _call_groq_api(prompt, json_response=True):
    api_key, model_name = _get_api_config()
    if not api_key:
        print("Error: GROQ_API_KEY not found.")
        return None
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    if json_response:
        payload["response_format"] = {"type": "json_object"}
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            content_str = response_data['choices'][0]['message']['content']
            if json_response:
                return json.loads(content_str)
            return content_str
    except Exception as e:
        print("Error calling Groq API:", e)
        return None

def evaluate_resume(resume_text, domain):
    """
    Evaluates the resume against the selected domain and returns ATS score and feedback.
    Returns: dict {"ats_score": int, "missing_keywords": [str], "suggestions": str}
    """
    prompt = f"""
    You are an ATS (Applicant Tracking System) evaluating a resume for the domain / job role: "{domain}".
    Read the following resume text carefully.

    Resume Text:
    {resume_text}

    Evaluate the resume based on keyword matches, relevance, and overall structure for this domain.
    Return ONLY a JSON object exactly with these keys:
    'ats_score': an integer from 0 to 100 representing the score.
    'missing_keywords': a list of important keywords for "{domain}" that are missing.
    'suggestions': a brief paragraph of suggestions for improvement.
    """
    
    res = _call_groq_api(prompt, json_response=True)
    if res and 'ats_score' in res:
        return res
    return {"ats_score": 0, "missing_keywords": [], "suggestions": "Could not evaluate resume."}

def evaluate_interview(qa_list, domain):
    """
    Evaluates a series of interview answers.
    qa_list should be a list of dicts: [{"question": "...", "answer": "..."}]
    Returns: list of dicts [{"question": "...", "user_answer": "...", "llm_evaluation": "...", "score": 0-10}]
    """
    qa_str = json.dumps(qa_list)
    prompt = f"""
    You are an expert interviewer evaluating a candidate for the "{domain}" domain.
    You will receive a JSON list of questions and the candidate's answers.
    
    Input data:
    {qa_str}

    Evaluate each answer given the question context.
    Return ONLY a JSON object containing a single key 'evaluations', which is an array of objects.
    Each object in the array must map to the questions in the EXACT SAME ORDER and MUST have the following keys:
    'question': the original question text.
    'user_answer': the candidate's original answer.
    'llm_evaluation': your detailed feedback on the answer (what was good, what was missing).
    'score': an integer score from 0 to 10.
    """
    
    res = _call_groq_api(prompt, json_response=True)
    if res and 'evaluations' in res:
        return res['evaluations']
    return []

def analyze_general_cv(resume_text):
    """
    Evaluates a general CV to extract summary, strengths, and suitable roles.
    Returns: dict {"summary": str, "strengths": [str], "suitable_roles": [str]}
    """
    prompt = f"""
    You are an expert career counselor and HR professional. Read this resume text carefully:
    
    Resume Text:
    {resume_text}
    
    Provide a brief report evaluating the resume. Highlight the top strengths of the candidate, and suggest 3-4 suitable job roles or domains they should apply for.
    Return ONLY a JSON object exactly with these keys:
    'summary': a brief paragraph summarizing their professional profile.
    'strengths': a list of strings representing their key strengths/skills.
    'suitable_roles': a list of strings representing suitable job roles or domains.
    """
    
    res = _call_groq_api(prompt, json_response=True)
    if res and 'summary' in res:
        return res
    return {"summary": "Could not analyze the CV due to an error or empty content.", "strengths": [], "suitable_roles": []}
