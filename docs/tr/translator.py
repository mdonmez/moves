import os
import time
from openai import OpenAI

client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key="csk-j2c23jd9d6ny868mk6y4epwhhwdyh9c4wjfcc4hm5fryyeep",
)

PROMPT = """
You are a professional translator and markdown expert. Your task is to translate the given Markdown content into the target language **while preserving the exact Markdown formatting**, including but not limited to:

- Headings (#, ##, ###, etc.)
- Lists (ordered and unordered)
- Code blocks (```), inline code (`code`)
- Bold, italics, strikethrough, blockquotes
- Links and images
- Tables
- Any other Markdown syntax

Instructions:

1. **Do not change any Markdown formatting or structure.**
2. **Only translate the visible text/content**, not code, links, or markdown syntax.
3. Maintain spacing, line breaks, and indentation exactly as in the original.
"""


def translate(text: str, target_lang: str):
    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": f"TARGET: {target_lang}\n\n\nCONTENT:\n\n{text}",
            },
        ],
    )

    return response.choices[0].message.content


def translate_folder(folder_path: str, target_lang: str):
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return

    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".md")
    ]

    if not files:
        print(f"No Markdown files found in '{folder_path}'.")
        return

    for idx, file_name in enumerate(files, start=1):
        file_path = os.path.join(folder_path, file_name)
        print(f"[{idx}/{len(files)}] Translating '{file_name}'...")

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        translated = translate(content, target_lang)

        with open(file_path, "w", encoding="utf-8") as outfile:
            outfile.write(str(translated))

        print(
            f"Finished translating '{file_name}'. Waiting 5 seconds before next file..."
        )
        time.sleep(5)

    print("All files translated successfully.")


if __name__ == "__main__":
    folder_to_translate = "docs/tr"
    translate_folder(folder_to_translate, "TURKISH")
