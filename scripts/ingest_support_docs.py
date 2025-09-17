import os
import time
import glob
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "developer-quickstart-py")
NAMESPACE  = os.environ.get("PINECONE_NAMESPACE", "kb-namespace")
PC_API_KEY = os.environ["PINECONE_API_KEY"]
CLOUD      = os.environ.get("PINECONE_CLOUD", "aws")
REGION     = os.environ.get("PINECONE_REGION", "us-east-1")
EMBED_MODEL= os.environ.get("PINECONE_EMBED_MODEL", "llama-text-embed-v2")

DOCS_DIR = Path(__file__).resolve().parents[1] / "support_docs"

# --- 1) Init Pinecone
pc = Pinecone(api_key=PC_API_KEY)

# --- 2) Create index if missing (server-side embeddings)
existing = [i["name"] for i in pc.list_indexes()]
if INDEX_NAME not in existing:
    print(f"Creating index '{INDEX_NAME}' with server-side embeddings: {EMBED_MODEL}")
    pc.create_index_for_model(
        name=INDEX_NAME,
        cloud=CLOUD,
        region=REGION,
        embed={
            "model": EMBED_MODEL,
            # Tell Pinecone which field contains the raw text to embed
            "field_map": {"text": "chunk_text"}
        }
    )
    # wait until ready
    while not pc.has_index(INDEX_NAME):
        time.sleep(1)

index = pc.Index(INDEX_NAME)

# --- 3) Gather files
paths = sorted(list(glob.glob(str(DOCS_DIR / "**" / "*.txt"), recursive=True)) +
               list(glob.glob(str(DOCS_DIR / "**" / "*.md"),  recursive=True)))

if not paths:
    raise SystemExit(f"No .txt/.md files found in {DOCS_DIR}. Add your articles and re-run.")

# --- 4) Split files into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,     # tweak: ~500-1200 chars is common
    chunk_overlap=120,  # small overlap preserves continuity
    separators=["\n\n", "\n", " ", ""]
)

records = []
rid = 1
for p in paths:
    with open(p, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        continue

    chunks = splitter.split_text(raw)
    source  = str(Path(p).relative_to(DOCS_DIR))
    category = source.split("/")[0] if "/" in source else "support"

    for i, chunk in enumerate(chunks):
        records.append({
            "_id": f"{Path(source).stem}-{i:04d}",
            "chunk_text": chunk,
            "category": category,
            "source": source
        })
        rid += 1

print(f"Prepared {len(records)} chunks from {len(paths)} files.")

# --- 5) Upsert with server-side embeddings
#    Because we created the index via `create_index_for_model(..., embed=...)`,
#    we can upsert *records* (Pinecone will embed the `chunk_text` field server-side).
BATCH = 200
for i in range(0, len(records), BATCH):
    batch = records[i:i+BATCH]
    index.upsert_records(NAMESPACE, batch)
    print(f"Upserted {i + len(batch)}/{len(records)}")
# print("Records", records)

print(f"Done. Namespace: {NAMESPACE}")

# --- 6) Optional: quick sanity query
try:
    query = "How do I set up Intercom?"
    res = index.search(
        namespace=NAMESPACE,
        query={
            "top_k": 5,
            "inputs": {"text": query}
        },
        # Uncomment to enable reranking (requires server support)
        rerank={"model": "bge-reranker-v2-m3", "top_n": 5, "rank_fields": ["chunk_text"]}
    )
    hits = (res.get("result", {}) or {}).get("hits", []) or []
    print("\nTop matches:")
    for h in hits:
        fields = h.get("fields", {}) or {}
        print(f"- {fields.get('source','?')} | {fields.get('category','?')}: {fields.get('chunk_text','')[:120]}...")
except Exception as e:
    print("Sanity search skipped:", e)
