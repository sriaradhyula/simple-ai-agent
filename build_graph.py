from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from simple_ai_agent import SimpleAIAgent
import uuid

store = InMemoryStore()
checkpointer = None
checkpointer = MemorySaver()

sample_ai_agent = SimpleAIAgent(uuid.uuid4().hex)
graph = sample_ai_agent.get_graph()