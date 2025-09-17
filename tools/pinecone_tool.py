# tools/pinecone_tool.py
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "developer-quickstart-py")
NAMESPACE  = os.environ.get("PINECONE_NAMESPACE", "example-namespace")
PC_API_KEY = os.environ["PINECONE_API_KEY"]

_pc = Pinecone(api_key=PC_API_KEY)
_index = _pc.Index(INDEX_NAME)

def search_kb(query: str, top_k: int = 5) -> str:
    """
    Semantic search against Pinecone using server-side embeddings + (optional) rerank.
    Returns a compact context string the agent can read.
    """
    results = _index.search(
        namespace=NAMESPACE,
        query={
            "top_k": top_k,
            "inputs": {"text": query}
        },
        rerank={
            "model": "bge-reranker-v2-m3",
            "top_n": top_k,
            "rank_fields": ["chunk_text"]
        }
    )
    hits = results.get("result", {}).get("hits", []) or []
    lines = []
    for hit in hits:
        fields = hit.get("fields", {}) or {}
        cat = fields.get("category", "unknown")
        txt = fields.get("chunk_text", "")
        lines.append(f"[{cat}] {txt}")
    return "\n".join(lines) if lines else "No results found."
