# from pinecone import Pinecone, ServerlessSpec
# # Wait for the upserted vectors to be indexed
# import time
# time.sleep(10)

# pc = Pinecone(api_key="pcsk_24ef7E_HZRn5Mg43hMaLp5ZizPx4Zf2WLm686Zy5Z5yxiLhpKGghdYzGr3X2LPc8P2fTP6")

# index_name = "developer-quickstart-py"

# if not pc.has_index(index_name):
#     pc.create_index_for_model(
#         name=index_name,
#         cloud="aws",
#         region="us-east-1",
#         embed={
#             "model":"llama-text-embed-v2",
#             "field_map":{"text": "chunk_text"}
#         }
#     )

# records = [
#     { "_id": "rec1", "chunk_text": "The Eiffel Tower was completed in 1889 and stands in Paris, France.", "category": "history" },
#     { "_id": "rec2", "chunk_text": "Photosynthesis allows plants to convert sunlight into energy.", "category": "science" },
#     { "_id": "rec3", "chunk_text": "Albert Einstein developed the theory of relativity.", "category": "science" },
#     { "_id": "rec4", "chunk_text": "The mitochondrion is often called the powerhouse of the cell.", "category": "biology" },
#     { "_id": "rec5", "chunk_text": "Shakespeare wrote many famous plays, including Hamlet and Macbeth.", "category": "literature" },
#     { "_id": "rec6", "chunk_text": "Water boils at 100°C under standard atmospheric pressure.", "category": "physics" },
# ]

# # Target the index
# dense_index = pc.Index(index_name)

# # Upsert the records into a namespace
# dense_index.upsert_records("example-namespace", records)

# # View stats for the index
# # stats = dense_index.describe_index_stats()
# # # print(stats)

# # # Define the query
# # query = "Famous historical structures and monuments"

# # # Search the dense index
# # results = dense_index.search(
# #     namespace="example-namespace",
# #     query={
# #         "top_k": 10,
# #         "inputs": {
# #             'text': query
# #         }
# #     },
# #     rerank={
# #         "model": "bge-reranker-v2-m3",
# #         "top_n": 10,
# #         "rank_fields": ["chunk_text"]
# #     }
# # )

# # # Print the results
# # for hit in results['result']['hits']:
# #         print(f"id: {hit['_id']:<5} | score: {round(hit['_score'], 2):<5} | category: {hit['fields']['category']:<10} | text: {hit['fields']['chunk_text']:<50}")

# # print(results)