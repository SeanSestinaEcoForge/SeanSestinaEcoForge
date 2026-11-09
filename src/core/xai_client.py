"""Optional xAI / Grok client wrapper.

The Grok helpers are OPTIONAL extras and are not needed for the simulations,
the pilot API or the tests. To use them:

    pip install -r requirements-grok.txt
    export XAI_API_KEY=...   # your own key; never commit it

Without the SDK or key, every helper raises GrokUnavailable with a clear message.
"""
import os

try:  # optional dependency
    from xai_sdk import Client
    from xai_sdk.chat import system, user
except ImportError:  # pragma: no cover - depends on the environment
    Client = None
    system = user = None


class GrokUnavailable(RuntimeError):
    """Raised when the optional xAI SDK or API key is missing."""


def get_xai_client():
    if Client is None:
        raise GrokUnavailable(
            "Optional package 'xai_sdk' is not installed. "
            "Install it with: pip install -r requirements-grok.txt"
        )
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise GrokUnavailable("XAI_API_KEY environment variable not set (use your own key; never commit it).")
    return Client(api_key=api_key)


def create_chat(model="grok-4-1-fast-reasoning", system_prompt=None):
    client = get_xai_client()
    chat = client.chat.create(model=model)
    if system_prompt:
        chat.append(system(system_prompt))
    return chat


def run_cli(fn):
    """Run fn() and turn GrokUnavailable into a clean one-line exit (code 2)."""
    import sys
    try:
        fn()
    except GrokUnavailable as exc:
        print(f"Grok helper skipped: {exc}", file=sys.stderr)
        sys.exit(2)


def _demo():
    chat = create_chat(system_prompt="You are Grok. Be concise and truthful.")
    chat.append(user("Say hello in one word."))
    print(chat.sample().content)


if __name__ == "__main__":
    run_cli(_demo)
