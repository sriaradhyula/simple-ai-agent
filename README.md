# simple-ai-agent

This repo demonstrates building a simple ReAct AI agent to perform tasks such as retrieving GitHub repo details via REST APIs, using LangGraph to define workflows.

![](docs/ai-agent.svg)

## Jupyter Notebook

- Open [Jupyter Notebook](simple_ai_agent.ipynb) in VS Code

## Run the code locally

```
make run
```

Sample Output:
```
Generated UUID: 4e12e5df-4d95-4c85-a5f5-004f5cffbea9
INFO:     Started server process [74521]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

## Test the code

### Scenario 1: Send a simple question that the agent can answer using a single tool

**Client request code in Python:**

```python
import requests
import json

url = "http://localhost:8000/question"

payload = json.dumps({
  "question": "get repo description for simple-ai-agent repo  in sriaradhyula org"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)

print(response.text)
```
**Sample Output:**
> The description of the repository "simple-ai-agent" in the "sriaradhyula" organization is: "This repo demonstrates building a simple ReAct AI agent to perform tasks such as retrieving GitHub repo details via REST APIs, using LangGraph to define workflows."

**Chain of thought explanation: Annotated with HumanMessage, AIMessage, ToolMessage**

- The user asks the AI agent application: “get repo description for simple-ai-agent repo  in sriaradhyula org”.
- Here, the AI Agent determines the user question needs a single tool invocation - get_github_repo_description.
- The AI agent replies back with the response.

```
--------------------------------------------------------------------------------
Type: HumanMessage, Content: get repo description for simple-ai-agent repo  in sriaradhyula org
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Type: AIMessage, Content:
Tool Call ID: call_HBjY0hWZNR5r0ZFcvlmgN4D7, Name: get_github_repo_description, Arguments: {"repo_name":"simple-ai-agent","org_name":"sriaradhyula"}
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Type: ToolMessage, Content: This repo demonstrates building a simple ReAct AI agent to perform tasks such as retrieving GitHub repo details via REST APIs, using LangGraph to define workflows.
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Type: AIMessage, Content: The description for the "simple-ai-agent" repository in the "sriaradhyula" organization is:

"This repo demonstrates building a simple ReAct AI agent to perform tasks such as retrieving GitHub repo details via REST APIs, using LangGraph to define workflows."
--------------------------------------------------------------------------------
```

### Scenario 2: Send a complex question that the agent needs different tool invocations in a loop until it gets the final answer:

**Client request code in Python:**

```
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
```

**Sample Output:**

>_The description of the repository is: "This repo demonstrates building a simple ReAct AI agent to perform tasks such as retrieving GitHub repo details via REST APIs, using LangGraph to define workflows."_
>
>_The topics of the repository are: "agent, ai, langgraph, python"_
>
>_Matching topics in the description and topics list are: "agent", "ai", and "langgraph"._

**Chain of thought explanation: Annotated with HumanMessage, AIMessage, ToolMessage**

- The user asks the AI agent application: “check if the repo description has any maching topics in the repo topics in repo simple-ai-agent in sriaradhyula org”
- Here, the AI agent determines that the user question needs information from two different tools to answer: get_github_repo_description and get_github_repo_topics
- AI Agent replies back with the response after correlating responses between both tools.

```
--------------------------------------------------------------------------------
Type: HumanMessage, Content: check if the repo description has any matching topics in the repo topics in repo simple-ai-agent in sriaradhyula org
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Type: AIMessage, Content:
Tool Call ID: call_K4aY0WTQxRVJjtQBsnUsjN0A, Name: get_github_repo_description, Arguments: {"repo_name": "simple-ai-agent", "org_name": "sriaradhyula"}
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Type: ToolMessage, Content: This repo demonstrates building a simple ReAct AI agent to perform tasks such as retrieving GitHub repo details via REST APIs, using LangGraph to define workflows.
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Type: ToolMessage, Content: agent, ai, langgraph, python
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Type: AIMessage, Content: The description of the repository "simple-ai-agent" is:

"This repo demonstrates building a simple ReAct AI agent to perform tasks such as retrieving GitHub repo details via REST APIs, using LangGraph to define workflows."

The topics of the repository are:

"agent, ai, langgraph, python"

Matching topics in the description and topics list are:
- "ai"
- "agent"
- "langgraph"
--------------------------------------------------------------------------------
```


### Alternative to Python: curl request as a client

```
curl --location 'http://localhost:8000/question' \
--header 'Content-Type: application/json' \
--data '{
    "question": "Get repo description for simple-ai-agent in sriaradhyula org"
}'
```

---
> _Code Disclaimer:_ The code provided in this repo is for educational and informational purposes only. While every effort is made to ensure the code is functional and accurate, it is provided "as-is" without any guarantees. Use the code at your own risk. The author is not responsible for any damage or data loss caused by implementing the code. Always review and test code in a safe environment before using it in production.
