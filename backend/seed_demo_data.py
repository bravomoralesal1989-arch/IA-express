import asyncio
from app.db import Base, engine, SessionLocal
from app.models import Business, GeneratedContent, IndexJob
from app.services.content_generator import generate_slug, generate_rag_micro_article
from app.services.site_publisher import publish_business_site
from app.services.indexnow_service import submit_url_to_indexnow

async def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        demo_businesses = [
            {
                "name": "La Choza Manuela",
                "category": "Restaurante",
                "town": "Bormujos",
                "province": "Sevilla",
                "address": "Av. de la Diputación, 41930 Bormujos, Sevilla",
                "latitude": 37.3712,
                "longitude": -6.0715,
                "website": "https://lachozamanuela.es",
                "phone": "+34 955 72 40 10",
                "description": "Restaurante de cocina tradicional andaluza, especializado en carnes a la brasa, guisos caseros del día y gran espacio familiar con terraza.",
                "specialties": "Carnes a la brasa, chuletones, guisos caseros, arroces, tapas tradicionales"
            },
            {
                "name": "Bodegas Góngora",
                "category": "Bodega y Enoturismo",
                "town": "Villanueva del Ariscal",
                "province": "Sevilla",
                "address": "Calle Santísimo Cristo de la Vera Cruz, 41808 Villanueva del Ariscal, Sevilla",
                "latitude": 37.3965,
                "longitude": -6.1412,
                "website": "https://bodegasgongora.com",
                "phone": "+34 954 11 30 05",
                "description": "Bodega histórica fundada en 1868 dedicada a la elaboración de vinos finos, amontillados y crianza en soleras tradicionales del Aljarafe.",
                "specialties": "Catas guiadas de vino, crianza en prensa de viga del siglo XVI, enoturismo, soleras históricas"
            }
        ]

        for item in demo_businesses:
            slug = generate_slug(f"{item['name']}-{item['town']}")
            existing = db.query(Business).filter(Business.slug == slug).first()
            if not existing:
                business = Business(
                    name=item["name"],
                    slug=slug,
                    category=item["category"],
                    town=item["town"],
                    province=item["province"],
                    address=item["address"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    website=item["website"],
                    phone=item["phone"],
                    description=item["description"],
                    specialties=item["specialties"]
                )
                db.add(business)
                db.flush()

                # Generar contenido GEO y Schema.org JSON-LD
                title, html_content, schema_jsonld = generate_rag_micro_article(business)
                pub_path, pub_url = publish_business_site(business.slug, html_content)

                content = GeneratedContent(
                    business_id=business.id,
                    title=title,
                    content_html=html_content,
                    schema_jsonld=schema_jsonld,
                    published_path=pub_path,
                    published_url=pub_url
                )
                db.add(content)
                db.commit()

                # Disparar IndexNow de demostración
                res = await submit_url_to_indexnow(pub_url)
                job = IndexJob(
                    business_id=business.id,
                    target_url=pub_url,
                    indexnow_status=res["status"],
                    http_status_code=res["http_code"],
                    response_body=res["response_body"]
                )
                db.add(job)
                db.commit()
                print(f"[OK] Demostración creada e IndexNow disparado para {business.name} ({business.town}) -> {pub_url}")

        print("\n==================================================")
        print("  MOTOR 1: INDEXACIÓN EXPRÉS - SEED DE DATOS LISTO")
        print("==================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
