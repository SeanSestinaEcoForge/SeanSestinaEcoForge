"""Optional: ask Grok for advice on a SIM state (needs xai_sdk + XAI_API_KEY).

Run from the repository root:  python src/grok_decision_stub.py
Without the optional SDK or key it exits cleanly with a message (exit code 2).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.core import xai_client  # noqa: E402


def get_grok_advice(sim_results: dict) -> str:
    """Get concise advice from Grok on aquaponics sim state."""
    chat = xai_client.create_chat(
        system_prompt="You are a homestead optimization advisor. Be maximally truthful and practical."
    )
    prompt = f"""
Current aquaponics sim state (SIM, not MEASURED):
{sim_results}

Provide concise advice:
- Is the system stable?
- Any immediate risks (DO crash, pH drift, nutrient imbalance)?
- Suggest one parameter adjustment if needed.
Prioritize family-scale resilience and closed-loop efficiency.
"""
    chat.append(xai_client.user(prompt))
    response = chat.sample(temperature=0.6, max_tokens=250)
    return response.content


def _demo():
    dummy_results = {"ph": 7.2, "do": 5.1, "nitrate": 28.4, "ammonia": 0.12}
    print("Grok advice:", get_grok_advice(dummy_results))


if __name__ == "__main__":
    xai_client.run_cli(_demo)
