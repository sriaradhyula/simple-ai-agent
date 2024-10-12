import requests
import json

url = "localhost:8000/question"

payload = json.dumps({
  "question": "get repo description for simple-ai-agent repo  in sriaradhyula org"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)