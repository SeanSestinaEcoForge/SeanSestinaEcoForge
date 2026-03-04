import os
from xai_sdk import Client
from xai_sdk.chat import user, system

def get_grok_advice(sim_results: dict) -> str:
    """
    Get concise advice from Grok on aquaponics sim state.
    """
    client = Client(api_key=os.getenv("XAI_API_KEY"))
    
    chat = client.chat.create(model="grok-4-1-fast-reasoning")  # or latest model
    
    prompt = f"""
Current aquaponics sim state:
{sim_results}

Provide concise advice:
- Is the system stable?
- Any immediate risks (DO crash, pH drift, nutrient imbalance)?
- Suggest one parameter adjustment if needed.
Prioritize family-scale resilience and closed-loop efficiency.
"""
    
    chat.append(system("You are a homestead optimization advisor. Be maximally truthful and practical."))
    chat.append(user(prompt))
    
    response = chat.sample(temperature=0.6, max_tokens=250)
    
    return response.content

# Example usage
if __name__ == "__main__":
    dummy_results = {
        "ph": 7.2,
        "do": 5.1,
        "nitrate": 28.4,
        "ammonia": 0.12
    }
    
    advice = get_grok_advice(dummy_results)
    print("Grok advice:", advice)
