import os, time
from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from google import genai

load_dotenv()
PDF_PATH = "data/linux_command_line.pdf"
START, END = 20, 150
MODELS = ["gemini-3.8-flash", "gemini-3.8-flash-lite"]

embedder = SentenceTransformer("all-MiniLM-L6-v2")
db = chromadb.PersistentClient(path="chroma_db").get_or_create_collection("docs")
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def build_index():
    reader = PdfReader(PDF_PATH)
    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        if not (START <= i <= END):
            continue
        text = page.extract_text() or ""
        for s in range(0, len(text), 1200):
            piece = text[s:s + 1500]
            if piece.strip():
                chunks.append((piece, i))
    texts = [c[0] for c in chunks]
    db.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=texts,
        embeddings=embedder.encode(texts).tolist(),
        metadatas=[{"page": c[1]} for c in chunks],
    )

if db.count() == 0:
    build_index()

def generate(prompt):
    for name in MODELS:
        for attempt in range(4):
            try:
                return client.models.generate_content(
                    model=name, contents=prompt).text
            except Exception as e:
                if "503" in str(e) or "429" in str(e):
                    time.sleep(2 ** attempt * 3)
                else:
                    break
    return "The model is busy right now. Please try again."

def ask(question, k=6):
    res = db.query(query_embeddings=embedder.encode([question]).tolist(),
                   n_results=k)
    docs, metas = res["documents"][0], res["metadatas"][0]
    context = "\n\n".join(f"[Page {m['page']}] {d}" for d, m in zip(docs, metas))
    prompt = (
        "Answer only from the context. Cite pages like (p. 45). "
        "If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    return generate(prompt), list(zip(docs, metas))