import json, time, csv, sys
sys.path.append(".")
from rag import ask

questions = json.load(open("eval/questions.json"))
rows = []
for item in questions:
    
    answer, sources = ask(item["q"])
    pages = sorted({m["page"] for _, m in sources})
    refused = "i don't know" in answer.lower()
    rows.append({
        "question": item["q"],
        "answerable": item["answerable"],
        "refused": refused,
        "retrieved_pages": pages,
        "expected_page_found": (item["page"] in pages) if item["page"] else "",
        "answer": answer.replace("\n", " ")[:300],
    })
    print(item["q"], "->", "refused" if refused else "answered")
    time.sleep(5)

with open("eval/results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)