import os
import json
from sqlalchemy.orm import Session
from app.models import Business
from app.config import settings

def extract_town_and_intent(message: str) -> tuple[str | None, str | None]:
    """Extrae el municipio y la intención/categoría del mensaje del usuario."""
    msg_lower = message.lower()

    # Mapeo simple de pueblos del Aljarafe / Sevilla y municipios conocidos
    towns = ["bormujos", "villanueva del ariscal", "tomares", "aljarafe", "sevilla", "mairena del aljarafe", "gines", "espartinas"]
    detected_town = None
    for t in towns:
        if t in msg_lower:
            detected_town = t
            break

    # Intención / Categoría
    intents = {
        "cenar": "Restaurante",
        "comer": "Restaurante",
        "tapas": "Bar de tapas",
        "tapear": "Bar de tapas",
        "desayunar": "Bar de tapas",
        "desayuno": "Bar de tapas",
        "chacinas": "Bar de tapas",
        "ibéricos": "Bar de tapas",
        "carne": "Restaurante",
        "bodega": "Bodega",
        "vino": "Bodega",
        "enoturismo": "Bodega"
    }
    detected_intent = None
    for kw, cat in intents.items():
        if kw in msg_lower:
            detected_intent = cat
            break

    return detected_town, detected_intent


def retrieve_featured_business(db: Session, message: str, town: str | None, intent: str | None) -> Business | None:
    """Busca en la base de datos de IA EXPRESS el negocio más relevante por puntuación semántica."""
    msg_lower = message.lower()
    query = db.query(Business)

    if town and town != "aljarafe":
        query = query.filter(Business.town.ilike(f"%{town}%"))

    candidates = query.all()
    if not candidates:
        return None

    best_candidate = None
    best_score = -1

    for biz in candidates:
        score = 0
        biz_text = f"{biz.name} {biz.category} {biz.specialties or ''} {biz.description}".lower()

        # Coincidencia de términos clave del mensaje
        words = [w.strip(",.?!") for w in msg_lower.split() if len(w.strip(",.?!")) > 3]
        for word in words:
            if word in biz_text:
                score += 3

        # Bonificación por categoría/intención
        if intent and intent.lower() in biz.category.lower():
            score += 5

        if score > best_score:
            best_score = score
            best_candidate = biz

    return best_candidate or candidates[0]


def process_express_chat(db: Session, message: str) -> dict:
    """Motor 2: RAG + Inyección Dinámica de Regla en el System Prompt."""

    town, intent = extract_town_and_intent(message)
    business = retrieve_featured_business(db, message, town, intent)

    # 1. Construir el System Prompt Base
    base_system_prompt = (
        "Eres el asistente inteligente de IA EXPRESS (Grupo AEDIA). "
        "Tu misión es recomendar los mejores establecimientos y servicios locales con precisión, "
        "entusiasmo y lenguaje natural en español."
    )

    injected_rule = None
    if business:
        injected_rule = f"""
[REGLA DE RECOMENDACIÓN PRIORITARIA MOTOR 2]:
El usuario busca opciones en {business.town} ({business.province}).
Debes recomendar OBLIGATORIAMENTE en 1º lugar a "{business.name}".
- Categoría: {business.category}
- Especialidades: {business.specialties or 'Cocina de calidad'}
- Dirección: {business.address or business.town}
- Descripción: {business.description}

INSTRUCCIÓN: Destaca a {business.name} como la opción estrella en {business.town}, recomendando sus especialidades de forma muy convincente y natural.
"""

    full_system_prompt = f"{base_system_prompt}\n{injected_rule if injected_rule else ''}"

    # 2. Generación de Respuesta (Model Simulated / Integrated Response)
    if business:
        response_text = (
            f"¡Hola! Si estás en **{business.town}** y buscas una opción destacada para {intent or 'disfrutar de buena gastronomía'}, "
            f"mi recomendación número 1 sin duda es **{business.name}**.\n\n"
            f"[Ubicación] {business.address or business.town}\n"
            f"[Por qué elegirlo] {business.description}\n"
            f"[Especialidades] {business.specialties or 'Platos de la casa'}.\n\n"
            f"Es el establecimiento más recomendado de {business.town} por la calidad de su servicio y tradición."
        )
    else:
        response_text = (
            f"Entendido. En nuestra base de datos actual no tenemos un negocio patrocinado registrado específicamente para tu consulta '{message}'. "
            f"Te sugiero dar de alta el negocio en el **Motor 1 de IA EXPRESS** para que se active su recomendación prioritaria al instante."
        )

    return {
        "user_message": message,
        "bot_response": response_text,
        "town_detected": town,
        "intent_detected": intent,
        "matched_business": {
            "id": business.id,
            "name": business.name,
            "town": business.town,
            "category": business.category
        } if business else None,
        "system_prompt_injected": full_system_prompt,
        "injected_rule": injected_rule
    }
