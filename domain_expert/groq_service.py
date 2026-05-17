import json
import urllib.request
import os
from admin_panel.models import AptitudeQuestion
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

def generate_aptitude_questions(domain: str, distributions: list = None) -> bool:
    """
    Calls Groq API to generate MCQ arrays based on distributions and stores them in DB.
    Returns True on success, False on error.
    """
    # Attempt to get API key from DB or OS env
    api_key, model_name = _get_api_config()
    if not api_key:
        print("Error: GROQ_API_KEY not found.")
        return False
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Handle optional distributions fallback
    if not distributions:
        distributions = [
            {'topic': 'Mathematics / Numerical Aptitude', 'count': 5},
            {'topic': 'English Language / Grammar', 'count': 5},
            {'topic': f'Basic Coding and specific technical logic for {domain}', 'count': 10}
        ]
        
    total_count = sum(d['count'] for d in distributions)
    constraints_str = "\n".join([f"- {d['count']} questions covering {d['topic']}." for d in distributions])

    prompt = f"""
    Generate exactly {total_count} multiple choice aptitude questions for a candidate in the '{domain}' domain.
    The distribution of the {total_count} questions MUST strictly follow this exact layout:
    {constraints_str}
    
    Return a JSON object containing a single key "questions" which maps to an array of objects.
    Each object must have exactly these keys: 'question', 'option1', 'option2', 'option3', 'option4', 'correct_answer'.
    The 'correct_answer' must perfectly match the exact text of one of the 4 options.
    """
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
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
            
            # Extract content text
            content_str = response_data['choices'][0]['message']['content']
            parsed_json = json.loads(content_str)
            
            questions = parsed_json.get('questions', [])
            
            # Save to DB
            for q in questions:
                AptitudeQuestion.objects.create(
                    domain=domain,
                    question=q.get('question'),
                    option1=q.get('option1'),
                    option2=q.get('option2'),
                    option3=q.get('option3'),
                    option4=q.get('option4'),
                    correct_answer=q.get('correct_answer')
                )
            return True
            
    except Exception as e:
        print("Error calling Groq API:", e)
        return False
