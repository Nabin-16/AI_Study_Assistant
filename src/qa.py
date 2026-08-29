import os
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


def answer_question(text, question, model="openai/gpt-oss-120b", api_key=None):
    client = _get_client(api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful study tutor. "
                    "Answer the student's question based ONLY on the provided study material. "
                    "If the answer is not in the material, state that clearly. "
                    "Give clear, direct educational explanations."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Study Material:\n{text}\n\n"
                    f"Question: {question}"
                )
            }
        ],
        temperature=0.3,
        max_tokens=5000,
    )
    
    raw_content = response.choices[0].message.content
    return strip_thinking(raw_content)
