import requests
import json

url = "http://localhost:8000/question"

payload = json.dumps({
  "question": "check if the repo description has any matching topics in the repo topics in repo simple-ai-agent in sriaradhyula org"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)

print(response.text)