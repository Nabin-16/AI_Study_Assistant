import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def strip_thinking(text):
    if not text:
        return ""
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def _get_client(api_key=None):
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not set. Please set it in your .env file.")
    return Groq(api_key=key)


def generate_quiz(text, num_questions=5, model="openai/gpt-oss-120b", api_key=None):
    client = _get_client(api_key)
    system_prompt = (
        "You are a quiz generator for students. "
        "Generate multiple-choice questions based on the study material.\n"
        "Return ONLY valid JSON — no extra commentary, no think tags, no markdown text outside the JSON.\n"
        "Format: a JSON array of objects:\n"
        "[\n"
        "  {\n"
        '    "question": "...",\n'
        '    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],\n'
        '    "answer": "A) ..."\n'
        "  }\n"
        "]"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate {num_questions} multiple-choice questions from this study material:\n\n{text}"}
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    
    raw = response.choices[0].message.content.strip()
    
    # 1. Strip reasoning think tags if present
    raw = strip_thinking(raw)
    # 2. Extract JSON code fence if present
    if "```" in raw:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
        if match:
            raw = match.group(1).strip()      
    # 3. Find JSON array boundaries
    start_idx = raw.find('[')
    end_idx = raw.rfind(']')
    if start_idx != -1 and end_idx != -1:
        raw = raw[start_idx:end_idx + 1]
        
    quiz = json.loads(raw)
    return quiz
