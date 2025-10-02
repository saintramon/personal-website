import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from pinecone import Pinecone

class AskRequest(BaseModel):
    question: str

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(host=os.getenv("PINECONE_HOST"))

MAX_CHARS_PER_CHUNK = 1000
TOP_K = 3

def answer_query(query: str) -> str:
    results = index.search(
        namespace=os.getenv("PINECONE_NAMESPACE"),
        query={"inputs": {"text": query}, "top_k": TOP_K},
        fields=["text", "source", "category"]
    )

    hits = results["result"]["hits"]
    context = "No relevant information found." if not hits else "\n".join([
        hit["fields"]["text"][:MAX_CHARS_PER_CHUNK]
        for hit in hits if "fields" in hit and "text" in hit["fields"]
    ])

    prompt = (
        f"Answer as if you are Ramon Emmiel Jasmin, in first person, casual, "
        f"friendly, and concise. Use context only, 1–2 sentences.\n\n"
        f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    )

    response = client.responses.create(
        model=os.getenv("MODEL_NAME"),
        instructions="Answer as if you are Ramon Emmiel Jasmin in first person, casual, friendly, and short.",
        input=prompt
    )

    return response.output_text.strip()

@app.post("/api/thanatos")
def thanatos(req: AskRequest):
    q = req.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Missing question")
    answer = answer_query(q)
    return {"answer": answer}
