# Conector Journey

API proxy en FastAPI que actúa como intermediario entre aplicaciones cliente y flujos de [Langflow](https://github.com/logspace-ai/langflow). Recibe un payload, lo reenvía al flujo correspondiente, y devuelve la respuesta parseada y limpia.

## Stack

- Python + FastAPI
- Uvicorn (ASGI server)
- Desplegado en [Render](https://render.com)

## Endpoints

### `GET /conector/health`
Verifica que el servicio esté activo.

**Response**
```json
{ "status": "ok" }
```

---

### `POST /crm/customer`
Llama al flujo fijo configurado por variables de entorno.

**Request body**
```json
{
  "dni": "12345678",
  "ip": "192.168.0.1",
  "screenId": 147,
  "branch": { "id": 64 }
}
```

**Response**
```json
[
  {
    "firstName": "Juan",
    "lastName": "Pérez",
    "dni": "12345678",
    "email": "juan.perez@mail.com",
    "customerType": { "id": "2" }
  }
]
```

---

### `POST /conector/{flow_id}/{apikey}`
Llama a cualquier flujo de Langflow dinámicamente.

**Parámetros de ruta**
| Parámetro | Descripción |
|-----------|-------------|
| `flow_id` | ID del flujo en Langflow |
| `apikey`  | API key del flujo |

**Request / Response**: igual que `/crm/customer`.

---

## Variables de entorno

Crear un archivo `.env` en la raíz (ver `.env.example`):

| Variable | Descripción |
|----------|-------------|
| `LANGFLOW_BASE_URL` | URL base de la API de Langflow (ej: `https://host/api/v1/run`) |
| `LANGFLOW_FIXED_FLOW_ID` | ID del flujo usado por `/crm/customer` |
| `LANGFLOW_FIXED_API_KEY` | API key del flujo usado por `/crm/customer` |
| `PORT` | Puerto del servidor (default: `8000`) |

## Correr localmente

```bash
pip install -r requirements.txt
python -m uvicorn conector:app --host 0.0.0.0 --port 8000 --reload
```

Documentación interactiva disponible en `http://localhost:8000/docs`.

## Deploy en Render

El repositorio incluye `render.yaml` con la configuración del servicio. Al conectar el repo en Render:

1. Render detecta el `render.yaml` automáticamente.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn conector:app --host 0.0.0.0 --port $PORT`
4. Configurar las variables de entorno en el dashboard de Render.
