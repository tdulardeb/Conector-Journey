import uvicorn
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL")
LANGFLOW_FIXED_FLOW_ID = os.getenv("LANGFLOW_FIXED_FLOW_ID")
LANGFLOW_FIXED_API_KEY = os.getenv("LANGFLOW_FIXED_API_KEY")


def _call_langflow(flow_url: str, api_key: str, payload: dict) -> JSONResponse:
    body = {
        "input_value": "trigger",
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "Mock Buscar Cliente por Pantalla": {
                "payload": payload,
                "nombre_mock": "Nicolas Ferreyra"
            }
        }
    }

    resp = requests.post(
        flow_url,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
        json=body,
        timeout=30,
    )

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    data = resp.json()

    try:
        outputs = data["outputs"][0]["outputs"]
        raw = None

        for item in outputs:
            if item.get("name") == "raw_json":
                raw = item["results"]["data"]["response"]
                break

        if raw is None:
            raise ValueError("No se encontró raw_json en la respuesta de Langflow")

        return JSONResponse(content=raw, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No pude extraer el JSON crudo: {e}")


@app.post("/crm/customer")
def crm_customer(payload: dict):
    url = f"{LANGFLOW_BASE_URL}/{LANGFLOW_FIXED_FLOW_ID}"
    return _call_langflow(url, LANGFLOW_FIXED_API_KEY, payload)


@app.post("/conector/{flow_id}/{apikey}")
def conector_dynamic(flow_id: str, apikey: str, payload: dict):
    url = f"{LANGFLOW_BASE_URL}/{flow_id}"
    return _call_langflow(url, apikey, payload)


if __name__ == "__main__":
    uvicorn.run("conector:app", host="0.0.0.0", port=8000, reload=True)