# pip install -qU "langchain[anthropic]" to call the model

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from tools.pinecone_tool import search_kb
from langchain.schema import AIMessage
from telemetry import init_logging, start_run, end_run, run_id_var, thread_id_var, with_telemetry

init_logging(level="INFO")

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
    tools=[with_telemetry(search_kb)],
    prompt="You are a helpful assistant."
)

thread_id = "local-thread-1"
run_id = start_run(thread_id=thread_id)

# Run the agent
try:
    data = agent.invoke({"messages": [
        {"role": "user", "content": "How do I set up Intercom?"}
    ]})
    last_ai = next(m for m in reversed(data["messages"]) if isinstance(m, AIMessage))
    answer = last_ai.content  # string or list; if list, filter 'type' == 'text'
    print(answer)
    end_run(status="ok")
except:
    end_run(status="error", error=str(e))
    raise