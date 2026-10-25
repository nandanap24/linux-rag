import csv, sys, ast

path = sys.argv[1]
rows = list(csv.DictReader(open(path, encoding="utf-8")))

def is_true(v):
    return str(v).strip().lower() == "true"

def failed(r):
    return is_true(r.get("error", "")) or r["answer"].startswith("The model is busy")

ok = [r for r in rows if not failed(r)]
errors = len(rows) - len(ok)

ans = [r for r in ok if is_true(r["answerable"])]
unans = [r for r in ok if not is_true(r["answerable"])]

answered = [r for r in ans if not is_true(r["refused"])]
wrongly_refused = [r for r in ans if is_true(r["refused"])]
correctly_refused = [r for r in unans if is_true(r["refused"])]
hallucinated = [r for r in unans if not is_true(r["refused"])]

print(f"File: {path}")
print(f"Total rows: {len(rows)}   API errors (excluded): {errors}")
print(f"Answerable:   {len(answered)} answered, {len(wrongly_refused)} refused (of {len(ans)})")
print(f"Unanswerable: {len(correctly_refused)} refused correctly, "
      f"{len(hallucinated)} answered anyway (of {len(unans)})")

found = [r for r in rows if r["expected_page_found"] != ""]
print("Errors to rerun:", [r["question"] for r in rows if failed(r)])
hits = [r for r in found if is_true(r["expected_page_found"])]
print(f"Expected page in top 6: {len(hits)} of {len(found)}")