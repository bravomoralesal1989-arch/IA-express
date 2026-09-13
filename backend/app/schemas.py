from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BusinessCreate(BaseModel):
    name: str = Field(..., example="La Choza Manuela")
    category: str = Field(..., example="Restaurante")
    town: str = Field(..., example="Bormujos")
    province: str = Field(default="Sevilla")
    address: Optional[str] = Field(default="Av. de la Diputación, Bormujos")
    latitude: Optional[float] = Field(default=37.3712)
    longitude: Optional[float] = Field(default=-6.0715)
    website: Optional[str] = Field(default="")
    phone: Optional[str] = Field(default="+34 955 00 00 00")
    description: str = Field(..., example="Restaurante tradicional andaluz especializado en carnes a la brasa y guisos caseros.")
    specialties: Optional[str] = Field(default="Carnes a la brasa, guisos caseros, arroces, terraza amplia")

class BusinessOut(BusinessCreate):
    id: int
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True

class IndexTriggerRequest(BaseModel):
    business_id: int
    custom_url: Optional[str] = None

class IndexJobOut(BaseModel):
    id: int
    business_id: int
    target_url: str
    indexnow_status: str
    http_status_code: Optional[int]
    response_body: Optional[str]
    submitted_at: datetime

    class Config:
        from_attributes = True

class ContentOut(BaseModel):
    id: int
    business_id: int
    title: str
    schema_jsonld: str
    published_url: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessageRequest(BaseModel):
    message: str = Field(..., example="¿Dónde puedo ir a cenar hoy en Bormujos?")

class MatchedBusinessOut(BaseModel):
    id: int
    name: str
    town: str
    category: str

class ChatResponse(BaseModel):
    user_message: str
    bot_response: str
    town_detected: Optional[str] = None
    intent_detected: Optional[str] = None
    matched_business: Optional[MatchedBusinessOut] = None
    system_prompt_injected: str
    injected_rule: Optional[str] = None

