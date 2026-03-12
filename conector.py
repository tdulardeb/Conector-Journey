import uvicorn
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import json
load_dotenv()

app = FastAPI()

LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL")
LANGFLOW_FIXED_FLOW_ID = os.getenv("LANGFLOW_FIXED_FLOW_ID")
LANGFLOW_FIXED_API_KEY = os.getenv("LANGFLOW_FIXED_API_KEY")


def _call_langflow(flow_url: str, api_key: str, payload: dict) -> JSONResponse:
    body = {
        "input_value": json.dumps(payload),
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {}
    }

    resp = requests.post(
        flow_url,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "origin": "debq2.debmedia.com"
        },
        json=body,
        timeout=30,
    )

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    if not resp.text.strip():
        raise HTTPException(
            status_code=502,
            detail=f"Langflow devolvió respuesta vacía (HTTP {resp.status_code})"
        )

    try:
        data = resp.json()
    except Exception:
        raise HTTPException(
            status_code=502,
            detail=f"Langflow devolvió respuesta no-JSON (HTTP {resp.status_code}): {resp.text[:500]}"
        )

    try:
        text = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]

        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[-1]
            clean = clean.rsplit("```", 1)[0].strip()

        parsed = json.loads(clean)
        return JSONResponse(content=parsed["response"], status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"No pude extraer el texto de Langflow: {e}",
                "langflow_response": data
            }
        )


@app.post("/crm/customer")
def crm_customer(payload: dict):
    url = f"{LANGFLOW_BASE_URL}/{LANGFLOW_FIXED_FLOW_ID}"
    return _call_langflow(url, LANGFLOW_FIXED_API_KEY, payload)

@app.get("/conector/health")
def health():
    return {"status": "ok"}

@app.post("/conector/{flow_id}/{apikey}")
def conector_dynamic(flow_id: str, apikey: str, payload: dict):
    url = f"{LANGFLOW_BASE_URL}/{flow_id}"
    return _call_langflow(url, apikey, payload)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("conector:app", host="0.0.0.0", port=port)