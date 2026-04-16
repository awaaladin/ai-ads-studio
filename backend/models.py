from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    business_name = Column(String, nullable=False)
    industry = Column(String)
    audience = Column(String)
    tone = Column(String)
    colors = Column(String)
    goal = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    ad_creatives = relationship("AdCreative", back_populates="project", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    file_type = Column(String)  # image, video, pdf
    file_url = Column(String)
    extracted_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="assets")

class AdCreative(Base):
    __tablename__ = "ad_creatives"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    copy = Column(Text)
    social_posts = Column(JSON) # e.g., list of strings or dicts
    pdf_brochure_url = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    project = relationship("Project", back_populates="ad_creatives")
