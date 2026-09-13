from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from pathlib import Path

from app.config import settings
from app.db import Base, engine, get_db
from app.models import Business, GeneratedContent, IndexJob
from app.schemas import BusinessCreate, BusinessOut, IndexJobOut, ContentOut, ChatMessageRequest, ChatResponse
from app.services.content_generator import generate_slug, generate_rag_micro_article
from app.services.site_publisher import publish_business_site
from app.services.indexnow_service import submit_url_to_indexnow
from app.services.chat_engine import process_express_chat

# Crear tablas en SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Motor 1 (Indexación Exprés JSON-LD) + Motor 2 (Chatbot RAG Dinámico)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Garantizar que el directorio público existe
settings.PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
sites_dir = settings.PUBLIC_DIR / "sites"
sites_dir.mkdir(parents=True, exist_ok=True)

# Servir clave IndexNow en la raíz para verificación de Bing/Protocolo
@app.get(f"/{settings.INDEXNOW_KEY}.txt")
async def get_indexnow_key():
    return Response(content=settings.INDEXNOW_KEY, media_type="text/plain")

@app.get("/api/health")
async def health_check():
    return {"status": "online", "app": settings.APP_NAME, "motor_1": "Indexación Exprés", "motor_2": "Chatbot RAG Dinámico"}

# --- ENDPOINTS PARA MOTOR 1: REGISTRO & CONTENIDO GEO ---

@app.post("/api/business", response_model=BusinessOut)
async def create_business(data: BusinessCreate, db: Session = Depends(get_db)):
    base_slug = generate_slug(f"{data.name}-{data.town}")
    slug = base_slug
    counter = 1
    while db.query(Business).filter(Business.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    business = Business(
        name=data.name,
        slug=slug,
        category=data.category,
        town=data.town,
        province=data.province,
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        website=data.website,
        phone=data.phone,
        description=data.description,
        specialties=data.specialties
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    # Auto-generar micro-artículo RAG y Schema.org JSON-LD
    title, html_content, schema_jsonld = generate_rag_micro_article(business)
    published_path, published_url = publish_business_site(business.slug, html_content)

    content = GeneratedContent(
        business_id=business.id,
        title=title,
        content_html=html_content,
        schema_jsonld=schema_jsonld,
        published_path=published_path,
        published_url=published_url
    )
    db.add(content)
    db.commit()

    return business


@app.get("/api/business", response_model=list[BusinessOut])
async def list_businesses(db: Session = Depends(get_db)):
    return db.query(Business).order_by(Business.created_at.desc()).all()


@app.get("/api/business/{business_id}/content", response_model=list[ContentOut])
async def get_business_contents(business_id: int, db: Session = Depends(get_db)):
    return db.query(GeneratedContent).filter(GeneratedContent.business_id == business_id).all()


# --- ENDPOINT MOTOR 1: DISPARADOR EXPRÉS INDEXNOW ---

@app.post("/api/index-now/{business_id}", response_model=IndexJobOut)
async def trigger_index_now(business_id: int, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    content = db.query(GeneratedContent).filter(GeneratedContent.business_id == business_id).order_by(GeneratedContent.created_at.desc()).first()
    target_url = content.published_url if content else f"{settings.BASE_URL}/sites/{business.slug}/index.html"

    # Enviar al protocolo IndexNow
    result = await submit_url_to_indexnow(target_url)

    job = IndexJob(
        business_id=business.id,
        target_url=target_url,
        indexnow_status=result["status"],
        http_status_code=result["http_code"],
        response_body=result["response_body"]
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@app.get("/api/index-jobs", response_model=list[IndexJobOut])
async def list_index_jobs(db: Session = Depends(get_db)):
    return db.query(IndexJob).order_by(IndexJob.submitted_at.desc()).all()


# --- ENDPOINT MOTOR 2: CHATBOT RAG + SYSTEM PROMPT INJECTION ---

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatMessageRequest, db: Session = Depends(get_db)):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    
    result = process_express_chat(db, req.message.strip())
    return result


# Servir páginas web generadas en /sites/
app.mount("/sites", StaticFiles(directory=settings.PUBLIC_DIR / "sites", html=True), name="sites")

# Servir Frontend Dashboard
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

