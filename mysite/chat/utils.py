
from django.contrib.postgres.search import SearchVector
import requests


def search_documents(question):
    from chat.models import Documents
    search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
    documents = Documents.objects.annotate(search=search_vector).filter(search=question)
    relevant_content = " ".join(doc.content for doc in documents)
    return relevant_content

def get_chatgpt_response(question, context="", max_tokens=60):
    # Configuration for API access
    api_key = '#PLACE your ChatGPT API KEY #'
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    messages = []
    if context:
        messages.append({
            "role": "system",
            "content": str(context).strip()
        })

    messages.append({
        "role": "user",
        "content": str(question).strip()
    })

    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
        'max_tokens': max_tokens
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except KeyError:
            return "Error while parsing response."
    else:
        return f"Error: API request failed with status {response.status_code}."

