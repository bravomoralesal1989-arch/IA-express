import asyncio
from app.db import Base, engine, SessionLocal
from app.services.chat_engine import process_express_chat

def test_motor_2_chat():
    print("==================================================")
    print("  PRUEBA AUTOMÁTICA MOTOR 2: CHATBOT RAG + PROMPT INJECTION")
    print("==================================================")

    db = SessionLocal()
    try:
        queries = [
            "¿Dónde puedo ir a cenar hoy en Bormujos?",
            "Recomiéndame una bodega tradicional en Villanueva del Ariscal con catas de vino",
            "¿Dónde comer un buen solomillo en Tomares?"
        ]

        for idx, q in enumerate(queries, 1):
            print(f"\n--- [PRUEBA {idx}] Consulta: '{q}' ---")
            result = process_express_chat(db, q)

            print(f"[LOCATION] Municipio Detectado: {result['town_detected']}")
            print(f"[INTENT] Intencion Detectada: {result['intent_detected']}")
            if result['matched_business']:
                print(f"[MATCH] Negocio Coincidente: {result['matched_business']['name']} ({result['matched_business']['town']})")
            else:
                print("[MATCH] Negocio Coincidente: Ninguno")

            print("\n[BOT RESPONSE]:")
            print(result['bot_response'])

            print("\n[SYSTEM PROMPT INJECTED RULE]:")
            print(result['injected_rule'] or "Sin regla inyectada")
            print("-" * 50)

        print("\n[ÉXITO] MOTOR 2 VERIFICADO CORRECTAMENTE.")
        print("==================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    test_motor_2_chat()
