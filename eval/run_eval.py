import json, time, csv, sys
sys.path.append(".")
from rag import ask
import os
USE_RERANK = os.environ.get("RERANK", "1") == "1"
OUT = sys.argv[1] if len(sys.argv) > 1 else "eval/results.csv"
questions = json.load(open("eval/questions.json"))
rows = []
for item in questions:
    for attempt in range(3):
        answer, sources = ask(item["q"], rerank=USE_RERANK)
        if not answer.startswith("The model is busy"):
            break
        time.sleep(20)
    error = answer.startswith("The model is busy")
    pages = [m["page"] for _, m in sources]
    refused = any(p in answer.lower() for p in
              ["i don't know", "does not contain", "not mentioned", "no information"])
    rows.append({
        "question": item["q"],
        "answerable": item["answerable"],
        "refused": refused,
        "retrieved_pages": pages,
        "top_page": pages[0],
        "expected_page_found": (item["page"] in pages) if item["page"] else "",
        "answer": answer.replace("\n", " ")[:300],
        "error": error,
    })
    print(item["q"], "->", "ERROR" if error else ("refused" if refused else "answered"))
    time.sleep(5)

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)