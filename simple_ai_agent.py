from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
import asyncio

from fastapi import FastAPI

import uvicorn
import os
import datetime
from pydantic import BaseModel
import requests
import json
import uuid

# Define tools
@tool
def get_github_repo_description(repo_name: str, org_name: str) -> str:
  """
  Fetches the description of a GitHub repository.

  Args:
  repo_name (str): The name of the repository.
  org_name (str): The name of the organization or user that owns the repository.

  Returns:
  str: The description of the repository if available, otherwise a message indicating
      that no description is available or an error message if the request fails.

  Raises:
  requests.exceptions.RequestException: If there is an issue with the HTTP request.
  """
  url = f"https://api.github.com/repos/{org_name}/{repo_name}"
  headers = {
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
  }
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    repo_info = response.json()
    return repo_info['description'] if repo_info['description'] else f"No description available for {repo_name} in {org_name}"
  else:
    return f"Failed to fetch description for {repo_name} in {org_name}. Status code: {response.status_code}"

@tool
def get_github_repo_topics(repo_name: str, org_name: str) -> str:
  """
  Fetches the topics of a GitHub repository.

  Args:
  repo_name (str): The name of the repository.
  org_name (str): The name of the organization or user that owns the repository.

  Returns:
  str: A comma-separated string of topics if available, otherwise a message indicating
      that no topics are available or an error message if the request fails.

  Raises:
  requests.exceptions.RequestException: If there is an issue with the HTTP request.
  """
  url = f"https://api.github.com/repos/{org_name}/{repo_name}/topics"
  headers = {
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github.mercy-preview+json"
  }
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    repo_info = response.json()
    topics = repo_info.get('names', [])
    return ", ".join(topics) if topics else f"No topics available for {repo_name} in {org_name}"
  else:
    return f"Failed to fetch topics for {repo_name} in {org_name}. Status code: {response.status_code}"

class SimpleAIAgent():
  '''
  Simple AI Agent is a class that initializes and configures an AI assistant using LLMs.
  '''
  def __init__(self, thread_id: str):
    # Specify a thread
    self.config = {"configurable": {"thread_id": thread_id}}

    # Initialize LLMFactory with the desired model name
    model_name = os.getenv("LLM_MODEL_NAME", "openai")

    if model_name == "azure_openai":
      deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
      api_version = os.getenv("AZURE_OPENAI_API_VERSION")
      llm = AzureChatOpenAI(
        azure_deployment=deployment,
        api_version=api_version,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
      )
    elif model_name == "openai":
      llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
      )

    tools = [
      get_github_repo_description,
      get_github_repo_topics
    ]

    llm_with_tools = llm.bind_tools(tools)

    # System message
    sys_msg = SystemMessage(content=(
      "You are a helpful Assistant tasked with performing tasks.\n"
      "You can assist with github repo operations \n"
    ), pretty_repr=True)

    # Node
    def assistant(state: MessagesState):
      return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

    # Graph
    self.builder = StateGraph(MessagesState)

    # Define nodes: They do the actual work
    self.builder.add_node("simple_ai_agent", assistant)
    self.builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    self.builder.add_edge(START, "simple_ai_agent")

    # Add conditional edges
    self.builder.add_conditional_edges(
      "simple_ai_agent",
      tools_condition,
      "tools"
    )

    # Add an edge to the tool node
    self.builder.add_edge("tools", "simple_ai_agent")

    checkpointer = MemorySaver()
    self.react_graph_memory = self.builder.compile(checkpointer=checkpointer)

    self.react_graph_memory = self.builder.compile(checkpointer=checkpointer)

  def interact(self, human_message:str):
    try:
      # Specify an input
      messages = [HumanMessage(content=human_message)]

      # return messages
      messages = self.react_graph_memory.invoke({"messages": messages}, self.config)

      # print messages
      for message in messages['messages']:
        print("-" * 80)
        print(f"Type: {type(message).__name__}, Content: {message.content}")
        if message.additional_kwargs and 'tool_calls' in message.additional_kwargs:
            print(f"Tool Call ID: {message.additional_kwargs['tool_calls'][0]['id']}, Name: {message.additional_kwargs['tool_calls'][0]['function']['name']}, Arguments: {message.additional_kwargs['tool_calls'][0]['function']['arguments']}")
        print("-" * 80)

      return messages['messages'][-1].content
    except Exception as e:
      print(e)

  def create_graph_image(self):
    graph_image = self.react_graph_memory.get_graph(xray=1).draw_mermaid_png()
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"simple_ai_agent_{timestamp}.png"
    with open(filename, "wb") as f:
      f.write(graph_image)
    print(f"Graph image saved as '{filename}'. Open this file to view the graph.")

  def print_message_history(self, thread_id: str):
    message_history = [s for s in self.react_graph_memory.get_state_history(self.config)]
    print(f"Message history for thread_id {thread_id}: {json.dumps(message_history, default=str, indent=2)}")
    print(json.dumps(message_history, default=str, indent=2))

class ChatBotQuestion(BaseModel):
  question: str

def get_uuid() -> str:
  unique_id = str(uuid.uuid4())
  print(f"Generated UUID: {unique_id}")
  return unique_id

# Initialize the SimpleAIAgent
agent = SimpleAIAgent(get_uuid())

app = FastAPI()

@app.post("/question")
def ask_question(question: ChatBotQuestion):
  """
  Interacts with a chatbot agent to ask a question and retrieve the response.

  Args:
    question (ChatBotQuestion): An object containing the question text and chat session ID.

  Returns:
    str: The content of the second message in the response from the chatbot agent.

  Note:
    The function returns the content of the message at index 1 because the response
    is expected to be a list of messages, where the first message (index 0) is a HumanMessages,
    and the second message is an AIMessage.
  """
  response = agent.interact(question.question)
  return str(response)

async def main():
  config = uvicorn.Config(app, host="localhost", port=8000)
  server = uvicorn.Server(config)
  await server.serve()

if __name__ == '__main__':
  # Uncomment the line below to create the langgraph image
  # agent.create_graph_image()
  asyncio.run(main())