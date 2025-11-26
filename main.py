from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pydantic import BaseModel
from groq import Groq
import os,json, re
from fastapi.responses import FileResponse
from dotenv import load_dotenv

app = FastAPI(
    title="Monthly Budger Planner",
    contact={
    "name": "Aiman Hayat",
    "email": "aiman@iciltek.com",
    }  
)
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class VoiceText(BaseModel):
    text: str

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.post("/parse_voice")
async def parse_voice(data: VoiceText):
    prompt = f"""
    You are a smart finance assistant.
    Analyze the following text and extract every transaction with:
    - category: one of ["expenses", "income", "bills", "savings", "debt"]
    - description: what it was for just one or two words for description
    - amount: numeric value

    Return as a JSON array.
    Text: {data.text}
    """

    try:
        response = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct-0905",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        content = response.choices[0].message.content.strip()
        # Try to extract pure JSON (Groq returns markdown sometimes)
        import json, re
        json_str = re.search(r'\[.*\]', content, re.S)
        if not json_str:
            raise ValueError("No JSON detected.")
        transactions = json.loads(json_str.group(0))
        return {"transactions": transactions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
