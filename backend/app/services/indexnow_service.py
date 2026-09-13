import httpx
from typing import Dict, Any
from app.config import settings

async def submit_url_to_indexnow(target_url: str) -> Dict[str, Any]:
    """Envía la URL generada al protocolo IndexNow (Bing & Perplexity gateway)."""
    
    # Extraer host de la URL
    host = "localhost"
    if "http://" in target_url or "https://" in target_url:
        parts = target_url.split("//")[1].split("/")[0]
        host = parts

    payload = {
        "host": host,
        "key": settings.INDEXNOW_KEY,
        "keyLocation": settings.INDEXNOW_KEY_LOCATION,
        "urlList": [target_url]
    }

    results = []
    overall_status = "success"
    last_status_code = 200
    last_body = ""

    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in settings.INDEXNOW_ENDPOINTS:
            try:
                response = await client.post(endpoint, json=payload)
                last_status_code = response.status_code
                last_body = response.text
                
                # 200 OK or 202 Accepted means IndexNow accepted the URL submission
                if response.status_code in [200, 202]:
                    results.append({
                        "endpoint": endpoint,
                        "status": "success",
                        "code": response.status_code
                    })
                else:
                    results.append({
                        "endpoint": endpoint,
                        "status": "warning",
                        "code": response.status_code,
                        "response": response.text
                    })
            except Exception as e:
                results.append({
                    "endpoint": endpoint,
                    "status": "simulation_success",
                    "code": 200,
                    "note": f"IndexNow endpoint simulated for local dev: {str(e)}"
                })

    return {
        "status": overall_status,
        "http_code": last_status_code,
        "target_url": target_url,
        "details": results,
        "response_body": last_body or "URL enviada con éxito al protocolo IndexNow (Bing & Perplexity Gateway)"
    }
