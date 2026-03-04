# examples/tool_calling_demo.py
from src.core.xai_client import create_chat
from xai_sdk.tools import tool

@tool
def get_chp_metrics(power: float, fuel: str = "propane") -> dict:
    """Get CHP performance metrics"""
    from src.tools.energy import chp_efficiency_calc
    return chp_efficiency_calc(power, fuel)

# Create chat instance (assuming create_chat returns a chat object with append/sample)
chat = create_chat()

# Register tool
chat.register_tools([get_chp_metrics])

# Add user message - fixed format
chat.append({"role": "user", "content": "What are realistic CHP metrics for a 8kW propane system?"})

response = chat.sample()
print("Response:", response.content)

if response.tool_calls:
    print("\nTool calls made:", len(response.tool_calls))
    for call in response.tool_calls:
        result = call.execute()
        print("Tool result:", result)
