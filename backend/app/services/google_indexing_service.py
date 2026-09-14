import httpx
import logging
from app.config import settings

logger = logging.getLogger("google_indexing")

async def submit_to_google(target_url: str, base_url: str = None) -> dict:
    """
    Notifica a Google mediante el endpoint oficial de Ping de Sitemap y Googlebot.
    """
    if not base_url:
        base_url = settings.BASE_URL.rstrip('/')

    sitemap_url = f"{base_url}/sitemap.xml"
    google_ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(google_ping_url)
            
            logger.info(f"Google Sitemap Ping enviado: {google_ping_url} | HTTP {resp.status_code}")
            
            return {
                "engine": "Google Search / Googlebot",
                "status": "success" if resp.status_code in [200, 204] else "queued",
                "http_code": resp.status_code,
                "ping_url": google_ping_url,
                "target_url": target_url
            }
    except Exception as e:
        logger.error(f"Error enviando ping a Google: {e}")
        return {
            "engine": "Google Search / Googlebot",
            "status": "error",
            "http_code": 500,
            "error": str(e),
            "target_url": target_url
        }
