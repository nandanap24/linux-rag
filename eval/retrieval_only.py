import json, sys
sys.path.append(".")
from rag import db, embedder, reranker

for item in json.load(open("eval/questions.json")):
    q = item["q"]
    res = db.query(query_embeddings=embedder.encode([q]).tolist(), n_results=15)
    docs, metas = res["documents"][0], res["metadatas"][0]
    vec = [m["page"] for m in metas[:6]]
    scores = reranker.predict([(q, d) for d in docs])
    order = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)[:6]
    print(q)
    print("  vector :", vec)
    print("  rerank :", [metas[i]["page"] for i in order])