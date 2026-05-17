import urllib.request
import urllib.error
import json

url = 'https://api.groq.com/openai/v1/chat/completions'
headers = {
    'Authorization': 'Bearer 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',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}
payload = {
    'model': 'llama-3.1-8b-instant',
    'messages': [{'role': 'user', 'content': '{"questions": [{"question": "q", "option1": "1", "option2": "2", "option3": "3", "option4": "4", "correct_answer": "1"}]}'}],
    'response_format': {'type': 'json_object'},
    'temperature': 0.3
}
req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method='POST')

try:
    urllib.request.urlopen(req)
    print('Success')
except urllib.error.HTTPError as e:
    print('HTTP Error', e.code, e.reason)
    print(e.read().decode())
