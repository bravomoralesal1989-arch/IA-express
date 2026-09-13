import asyncio
import httpx
from app.db import Base, engine, SessionLocal
from app.models import Business, GeneratedContent, IndexJob
from app.services.content_generator import generate_rag_micro_article
from app.services.indexnow_service import submit_url_to_indexnow
from app.services.chat_engine import process_express_chat

async def run_full_audit():
    print("==================================================================")
    print("      AUDITORÍA INTERNA DE SISTEMA & TEST DE FLUJO COMPLETO       ")
    print("==================================================================")

    db = SessionLocal()
    audit_results = []

    # TEST 1: Base de datos IA EXPRESS
    businesses = db.query(Business).all()
    print(f"\n[AUDITORÍA 1] Negocios Registrados en IA EXPRESS: {len(businesses)}")
    for b in businesses:
        print(f"  - #{b.id} | {b.name} ({b.town}) -> {b.category}")
    
    if len(businesses) >= 3:
        audit_results.append(("IA EXPRESS Database Registry", "PASSED", f"{len(businesses)} negocios listos"))
    else:
        audit_results.append(("IA EXPRESS Database Registry", "FAILED", "Menos de 3 negocios"))

    # TEST 2: Marcado JSON-LD Schema.org y Contenido RAG
    print("\n[AUDITORÍA 2] Verificación de Marcado JSON-LD Schema.org:")
    contents = db.query(GeneratedContent).all()
    valid_schemas = 0
    for c in contents:
        has_schema = "@context" in c.schema_jsonld and "schema.org" in c.schema_jsonld
        if has_schema:
            valid_schemas += 1
            print(f"  - [OK] {c.title[:60]}... -> JSON-LD válido")
        else:
            print(f"  - [ERROR] {c.title[:60]}... -> Sin JSON-LD")
    
    if valid_schemas == len(contents) and valid_schemas > 0:
        audit_results.append(("Schema.org JSON-LD Generator", "PASSED", f"{valid_schemas}/{len(contents)} esquemas válidos"))
    else:
        audit_results.append(("Schema.org JSON-LD Generator", "FAILED", "Esquemas inválidos"))

    # TEST 3: Protocolo IndexNow Exprés
    print("\n[AUDITORÍA 3] Verificación del Disparador IndexNow (Bing/Perplexity Gateway):")
    test_url = "http://localhost:8050/sites/la-choza-manuela-bormujos/index.html"
    index_res = await submit_url_to_indexnow(test_url)
    print(f"  - Envío IndexNow Status: {index_res['status']} | HTTP Code: {index_res['http_code']}")
    if index_res['status'] == "success":
        audit_results.append(("Protocolo IndexNow Gateway", "PASSED", f"HTTP Code {index_res['http_code']}"))
    else:
        audit_results.append(("Protocolo IndexNow Gateway", "FAILED", f"Error {index_res['http_code']}"))

    # TEST 4: Motor 2 Chatbot RAG (4 Pruebas de Recomendación)
    print("\n[AUDITORÍA 4] Verificación de Recomendaciones del Chatbot (Motor 2 RAG):")
    test_cases = [
        ("¿Dónde ir a cenar hoy en Bormujos?", "La Choza Manuela"),
        ("¿Dónde ir a desayunar o tapear en Villanueva del Ariscal?", "Bar Los Mayores by La Extremeña"),
        ("Recomiéndame una bodega tradicional en Villanueva del Ariscal", "Bodegas Góngora"),
        ("¿Dónde comer un buen solomillo en Tomares?", "Bar El Arriero Exprés")
    ]

    chatbot_passed = 0
    for query, expected_name in test_cases:
        res = process_express_chat(db, query)
        matched = res['matched_business']['name'] if res['matched_business'] else "Ninguno"
        is_ok = matched == expected_name
        if is_ok:
            chatbot_passed += 1
            print(f"  - [OK] Consulta: '{query}' -> Recomienda: {matched}")
        else:
            print(f"  - [FAIL] Consulta: '{query}' -> Recomienda: {matched} (Esperado: {expected_name})")

    if chatbot_passed == len(test_cases):
        audit_results.append(("Motor 2 Chatbot RAG Injection", "PASSED", f"{chatbot_passed}/{len(test_cases)} coincidencia exacta 1s"))
    else:
        audit_results.append(("Motor 2 Chatbot RAG Injection", "FAILED", f"{chatbot_passed}/{len(test_cases)} coincidencia"))

    # RESUMEN FINAL DE AUDITORÍA
    print("\n==================================================================")
    print("                    RESUMEN DE AUDITORÍA INTERNA                  ")
    print("==================================================================")
    all_passed = True
    for item, status, detail in audit_results:
        symbol = "[PASSED]" if status == "PASSED" else "[FAILED]"
        print(f"  {symbol} {item:<35} | {detail}")
        if status != "PASSED":
            all_passed = False

    print("==================================================================")
    if all_passed:
        print("  SISTEMA AUDITADO CON ÉXITO - LISTO PARA PRODUCCIÓN EN MÁQUINA NUEVA  ")
    else:
        print("  SE DETECTARON ERRORES EN LA AUDITORÍA  ")
    print("==================================================================\n")

if __name__ == "__main__":
    asyncio.run(run_full_audit())
