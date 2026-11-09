"""ARCHIVED (pre-Nov 2026): original toy FastAPI stub, kept for history.

Replaced by the tested pilot planning API in api/. Its alk_meq units and the
exponential worm-consumption curve were toy placeholders, not physical claims.
To run it anyway, copy it to the repository root next to throttles.py.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from throttles import apply_throttles, vermi_solids_consumption

app = FastAPI(title="EcoForge Aquaponics API", version="1.0")

class SimRequest(BaseModel):
    pH: float = 7.0
    temp_C: float = 25.0
    alk_meq: float = 80.0
    nitrate_mgL: float = 5.0
    DO_mgL: float = 8.0
    solids_kg: float = 10.0
    days: int = 7

@app.post("/simulate")
async def simulate(req: SimRequest):
    base_rate = 1.0
    throttled_rate = apply_throttles(base_rate, req.pH, req.temp_C, req.alk_meq, req.nitrate_mgL, req.DO_mgL)
    vermi_eaten = vermi_solids_consumption(req.solids_kg, req.days)
    
    # Quick plot
    fig, ax = plt.subplots()
    ax.plot([0, req.days], [req.solids_kg, req.solids_kg - vermi_eaten], label="Vermi consumption")
    ax.set_title("Throttled Nutrient Cycle")
    ax.set_xlabel("Days")
    ax.legend()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_b64 = base64.b64encode(buf.read()).decode()
    
    return JSONResponse({
        "throttled_rate": round(throttled_rate, 4),
        "vermi_eaten_kg": round(vermi_eaten, 2),
        "metrics_met": req.nitrate_mgL < 6.0 and req.DO_mgL > 7.0,
        "plot_base64": plot_b64
    })

@app.get("/health")
async def health():
    return {"status": "Supernova ready 🚀"}
