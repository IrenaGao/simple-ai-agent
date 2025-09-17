from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2024")

async def main():
    thread = await client.threads.create({})
    tid = thread["thread_id"]
    async for chunk in client.runs.stream(
        tid,  # Threadless run
        "agent", # Name of assistant. Defined in langgraph.json.
        input={
        "messages": [{
            "role": "user",
            "content": "What is LangGraph?",
            }],
        },
        config={"configurable": {"thread_id": tid}}
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)
        print("\n\n")

asyncio.run(main())