import os
import sys

from dotenv import load_dotenv

from agent.model_client import ModelClient


def main() -> int:
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    if not api_key:
        print("DEEPSEEK_API_KEY is not set. Put it in .env or your shell environment.")
        return 1

    client = ModelClient(api_key=api_key, base_url=base_url, model=model)

    try:
        reply = client.chat(
            [
                {
                    "role": "system",
                    "content": "You are a concise API connectivity test assistant.",
                },
                {
                    "role": "user",
                    "content": "Reply with exactly: deepseek api ok",
                },
            ]
        )
    except Exception as exc:
        print(f"DeepSeek API test failed: {exc}")
        return 1

    print(f"Model: {model}")
    print(f"Response: {reply.content.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
