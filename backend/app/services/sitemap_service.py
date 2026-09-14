import xml.etree.ElementTree as ET
from xml.dom import minidom
from sqlalchemy.orm import Session
from app.models import Business, GeneratedContent
from app.config import settings

def generate_sitemap_xml(db: Session, base_url: str = None) -> str:
    """Genera un archivo sitemap.xml compatible con Googlebot y Bingbot."""
    if not base_url:
        base_url = settings.BASE_URL.rstrip('/')

    urlset = ET.Element("urlset", xmlns="http://www.sitemapimages.org/schemas/sitemap/0.9")

    # URL principal del sitio
    url_main = ET.SubElement(urlset, "url")
    ET.SubElement(url_main, "loc").text = f"{base_url}/"
    ET.SubElement(url_main, "changefreq").text = "daily"
    ET.SubElement(url_main, "priority").text = "1.0"

    # URLs de negocios registrados
    businesses = db.query(Business).all()
    for biz in businesses:
        content = db.query(GeneratedContent).filter(GeneratedContent.business_id == biz.id).order_by(GeneratedContent.created_at.desc()).first()
        target_url = content.published_url if content else f"{base_url}/sites/{biz.slug}/index.html"
        
        url_elem = ET.SubElement(urlset, "url")
        ET.SubElement(url_elem, "loc").text = target_url
        ET.SubElement(url_elem, "changefreq").text = "always"
        ET.SubElement(url_elem, "priority").text = "0.9"

    xml_str = minidom.parseString(ET.tostring(urlset)).toprettyxml(indent="  ")
    return xml_str

def generate_robots_txt(base_url: str = None) -> str:
    """Genera robots.txt permitiendo acceso total a Googlebot, PerplexityBot, ChatGPT-User y declarando el Sitemap."""
    if not base_url:
        base_url = settings.BASE_URL.rstrip('/')

    return f"""User-agent: *
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: GPTBot
Allow: /

Sitemap: {base_url}/sitemap.xml
"""
