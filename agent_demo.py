# pip install -qU "langchain[anthropic]" to call the model

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from tools.pinecone_tool import search_kb

model = init_chat_model(
    "anthropic:claude-3-7-sonnet-latest",
    temperature=0.2
)

SYSTEM_PROMPT = """You are a helpful assistant.
- If a question likely requires facts, CALL the `search_kb` tool with a short, targeted query.
- Use ONLY the returned context to answer; cite brief snippets. If not enough info, say so.
"""

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[search_kb],
    prompt="You are a helpful assistant."
)

# Run the agent
resp1 = agent.invoke({"messages": [
    {"role": "user", "content": "Name a famous historical structure and when it was completed."}
]})
print("\nKB answer:\n", resp1)