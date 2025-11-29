import os
import dotenv
from openai import OpenAI

def main():
    dotenv.load_dotenv(override=True)
    base = os.getenv("OPENAI_API_BASE")
    key = os.getenv("OPENAI_API_KEY")
    print("BASE:", base)
    print("KEY_LEN:", len(key or ""))
    client = OpenAI(base_url=base, api_key=key)
    try:
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL") or "qwen-coder-turbo",
            messages=[{"role": "user", "content": "hello"}],
        )
        print("OK choices:", hasattr(resp, "choices"))
        print("OK usage:", hasattr(resp, "usage"))
        print("MODEL:", getattr(resp, "model", ""))
        print("USAGE:", getattr(resp, "usage", None))
        print("FIRST MSG:", resp.choices[0].message.content if hasattr(resp, "choices") else "")
    except Exception as e:
        print("ERR:", type(e).__name__, str(e))

if __name__ == "__main__":
    main()