import asyncio
import httpx
from app.db import Base, engine, SessionLocal
from app.models import Business, GeneratedContent, IndexJob
from app.services.content_generator import generate_slug, generate_rag_micro_article
from app.services.site_publisher import publish_business_site
from app.services.indexnow_service import submit_url_to_indexnow
from app.services.chat_engine import process_express_chat

async def register_bar_los_mayores():
    print("==================================================")
    print("  PRUEBA REAL: BAR LOS MAYORES BY LA EXTREMEÑA")
    print("==================================================")

    db = SessionLocal()
    try:
        biz_data = {
            "name": "Bar Los Mayores by La Extremeña",
            "category": "Bar de tapas, desayunos y raciones tradicionales",
            "town": "Villanueva del Ariscal",
            "province": "Sevilla",
            "address": "Plaza de España, 41808 Villanueva del Ariscal, Sevilla",
            "latitude": 37.3970,
            "longitude": -6.1418,
            "website": "https://facebook.com/barlosmayores",
            "phone": "+34 954 11 00 00",
            "specialties": "Chacinas ibéricas de La Extremeña, tapas caseras del día, desayunos tradicionales con pringá y tostadas de pueblo, carnes a la brasa",
            "description": "Bar y restaurante de tapas tradicionales en pleno centro de Villanueva del Ariscal (Sevilla), célebre por sus desayunos típicos, selección de embutidos e ibéricos de calidad, raciones caseras y ambiente familiar."
        }

        slug = generate_slug(f"{biz_data['name']}-{biz_data['town']}")
        existing = db.query(Business).filter(Business.slug == slug).first()
        if not existing:
            biz = Business(
                name=biz_data["name"],
                slug=slug,
                category=biz_data["category"],
                town=biz_data["town"],
                province=biz_data["province"],
                address=biz_data["address"],
                latitude=biz_data["latitude"],
                longitude=biz_data["longitude"],
                website=biz_data["website"],
                phone=biz_data["phone"],
                description=biz_data["description"],
                specialties=biz_data["specialties"]
            )
            db.add(biz)
            db.commit()
            db.refresh(biz)
        else:
            biz = existing

        print(f"[REGISTRO OK] ID: {biz.id} | Nombre: {biz.name} | Municipio: {biz.town}")

        # 1. Generar contenido GEO RAG y marcado Schema.org JSON-LD
        title, html_content, schema_jsonld = generate_rag_micro_article(biz)
        pub_path, pub_url = publish_business_site(biz.slug, html_content)

        print(f"\n[MICROSITIO RAG GENERADO]:")
        print(f" -> URL Pública: {pub_url}")
        print(f" -> Marcado Schema.org JSON-LD: @type Restaurant / LocalBusiness")

        # 2. Disparar IndexNow
        index_res = await submit_url_to_indexnow(pub_url)
        print(f"\n[INDEXNOW ENVIADO]:")
        print(f" -> Estado: {index_res['status']}")
        print(f" -> HTTP Status Code: {index_res['http_code']}")

        # 3. Probar Motor 2 Chatbot en Villanueva del Ariscal
        print(f"\n[PRUEBA MOTOR 2 CHATBOT]:")
        user_queries = [
            "¿Dónde ir a desayunar o tapear en Villanueva del Ariscal?",
            "¿Dónde comer buenas chacinas e ibéricos en Villanueva del Ariscal?"
        ]

        for q in user_queries:
            print(f"\n--- Consulta: '{q}' ---")
            chat_result = process_express_chat(db, q)
            print(f"[BOT RESPONSE]:\n{chat_result['bot_response']}\n")
            print(f"[INJECTED SYSTEM PROMPT RULE]:\n{chat_result['injected_rule']}\n")

        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(register_bar_los_mayores())
