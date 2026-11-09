"""Optional Grok tool-calling demo (needs xai_sdk + XAI_API_KEY).

Run from the repository root:  python examples/tool_calling_demo.py
The CHP numbers come from a placeholder calculator (src/tools/energy.py), not MEASURED data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.core.xai_client import GrokUnavailable, create_chat, run_cli  # noqa: E402
from src.tools.energy import chp_efficiency_calc  # noqa: E402


def _demo():
    try:
        from xai_sdk.tools import tool
    except ImportError as exc:
        raise GrokUnavailable(
            "Optional package 'xai_sdk' is not installed. Install it with: pip install -r requirements-grok.txt"
        ) from exc

    @tool
    def get_chp_metrics(power: float, fuel: str = "propane") -> dict:
        """Get CHP performance metrics (placeholder calculator)."""
        return chp_efficiency_calc(power, fuel)

    chat = create_chat()
    chat.register_tools([get_chp_metrics])
    chat.append({"role": "user", "content": "What are realistic CHP metrics for a 8kW propane system?"})
    response = chat.sample()
    print("Response:", response.content)
    if response.tool_calls:
        print("\nTool calls made:", len(response.tool_calls))
        for call in response.tool_calls:
            print("Tool result:", call.execute())


if __name__ == "__main__":
    run_cli(_demo)
