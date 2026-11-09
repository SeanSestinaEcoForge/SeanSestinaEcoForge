"""Optional Grok chat example (needs xai_sdk + XAI_API_KEY).

Run from the repository root:  python src/tools/examples/simple_grok_chat.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.core.xai_client import create_chat, run_cli  # noqa: E402


def _demo():
    chat = create_chat()
    chat.append({"role": "user", "content": "Explain closed-loop homestead in 2 sentences."})
    print("Response:", chat.sample().content)


if __name__ == "__main__":
    run_cli(_demo)
