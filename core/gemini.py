import google.generativeai as genai
import os
import json

genai.configure(api_key=os.environ.get('API_KEY'))

model = genai.GenerativeModel('gemini-1.5-pro',
                              # Set the `response_mime_type` to output JSON
                              generation_config={"response_mime_type": "application/json"})

times = 0
def generateFacts(state: str):
    global times 
    times += 1
    prompt = f"""Generate 5 one-line hidden or shocking facts about {state},
    without naming the {state}. The response should be in JSON format with the key 'facts' containing a list of facts."""

    response = model.generate_content(prompt)
    print(response.text)
    return json.loads(response.text)['facts']
