import os
import pandas as pd
from openai import OpenAI

MODEL = "gpt-4.1"
MAX_CHARS = 12000

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def load_prompt():
    prompt = read_file("prompt.txt")
    checklist = read_file("checklist.txt")
    return f"{prompt}\n\nChecklist:\n{checklist}"

def truncate(text):
    return text[:MAX_CHARS]

def review_code(file_path, system_prompt):
    code = truncate(read_file(file_path))
    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review this Java file:\n\n{code}"}
        ]
    )
    return response.output_text

def main():
    system_prompt = load_prompt()
    results = []

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".java"):
                path = os.path.join(root, file)
                try:
                    review = review_code(path, system_prompt)
                    results.append({"file": path, "findings": review})
                except Exception as e:
                    results.append({"file": path, "findings": str(e)})

    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(results)
    df.to_excel("output/ai_code_review.xlsx", index=False)

if __name__ == "__main__":
    main()