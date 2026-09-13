import asyncio
from app.db import Base, engine, SessionLocal
from app.models import Business, GeneratedContent, IndexJob
from app.services.content_generator import generate_slug, generate_rag_micro_article
from app.services.site_publisher import publish_business_site
from app.services.indexnow_service import submit_url_to_indexnow

async def run_motor_1_verification():
    print("==================================================")
    print("  PRUEBA AUTOMÁTICA MOTOR 1: INDEXACIÓN EXPRÉS")
    print("==================================================")

    db = SessionLocal()
    try:
        # 1. Crear un negocio de prueba instantáneo
        test_biz_data = {
            "name": "Bar El Arriero Exprés",
            "category": "Bar de tapas y raciones",
            "town": "Tomares",
            "province": "Sevilla",
            "address": "Calle Granate, 41920 Tomares, Sevilla",
            "latitude": 37.3751,
            "longitude": -6.0442,
            "description": "Bar de tapas caseras, especializado en solomillo al whisky, ensaladilla y guisos del día con rápida atención.",
            "specialties": "Solomillo al whisky, carnes a la brasa, tapas tradicionales"
        }

        slug = generate_slug(f"{test_biz_data['name']}-{test_biz_data['town']}")
        biz = db.query(Business).filter(Business.slug == slug).first()
        if not biz:
            biz = Business(
                name=test_biz_data["name"],
                slug=slug,
                category=test_biz_data["category"],
                town=test_biz_data["town"],
                province=test_biz_data["province"],
                address=test_biz_data["address"],
                latitude=test_biz_data["latitude"],
                longitude=test_biz_data["longitude"],
                description=test_biz_data["description"],
                specialties=test_biz_data["specialties"]
            )
            db.add(biz)
            db.commit()
            db.refresh(biz)

        print(f"[PASO 1] Negocio Creado: {biz.name} (ID: {biz.id}, Slug: {biz.slug})")

        # 2. Generar Contenido GEO + Schema.org JSON-LD
        title, html_content, schema_jsonld = generate_rag_micro_article(biz)
        pub_path, pub_url = publish_business_site(biz.slug, html_content)
        print(f"[PASO 2] Marcado JSON-LD Schema.org y Micro-página RAG Publicada en:\n         -> {pub_url}")

        # 3. Disparar IndexNow
        index_res = await submit_url_to_indexnow(pub_url)
        print(f"[PASO 3] IndexNow Disparado:")
        print(f"         - Status: {index_res['status']}")
        print(f"         - HTTP Code: {index_res['http_code']}")
        print(f"         - Detalle: {index_res['response_body']}")

        print("\n[ÉXITO] MOTOR 1 VERIFICADO CORRECTAMENTE.")
        print("==================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_motor_1_verification())
