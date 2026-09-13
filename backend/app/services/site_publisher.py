import os
from pathlib import Path
from app.config import settings

def publish_business_site(slug: str, html_content: str) -> tuple[str, str]:
    """Guarda la página HTML estática con Schema.org JSON-LD en el directorio público."""
    site_dir = settings.PUBLIC_DIR / "sites" / slug
    site_dir.mkdir(parents=True, exist_ok=True)

    file_path = site_dir / "index.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    public_url = f"{settings.BASE_URL}/sites/{slug}/index.html"
    return str(file_path), public_url
