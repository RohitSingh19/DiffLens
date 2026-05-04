import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_code(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict code reviewer. Analyze the provided code and identify potential issues, bugs, or areas for improvement. Provide specific feedback and suggestions for each identified issue."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0
    )
    return response.choices[0].message.content.strip()

