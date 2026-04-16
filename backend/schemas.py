from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectBase(BaseModel):
    business_name: str
    industry: Optional[str] = None
    audience: Optional[str] = None
    tone: Optional[str] = None
    colors: Optional[str] = None
    goal: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AssetBase(BaseModel):
    file_type: str
    file_url: str
    extracted_text: Optional[str] = None

class AssetResponse(AssetBase):
    id: str
    project_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdCreativeBase(BaseModel):
    copy: str
    social_posts: Any
    pdf_brochure_url: Optional[str] = None

class AdCreativeResponse(AdCreativeBase):
    id: str
    project_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
