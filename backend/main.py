from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import os

from database import engine, Base, get_db
import models
import schemas
from services.llm import generate_ad_copy
from services.pdf import generate_pdf
from services.storage import upload_file_to_supabase

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Ads Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Ads Studio API is running"}

@app.post("/onboarding", response_model=schemas.ProjectResponse)
def onboarding(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project_id = str(uuid.uuid4())
    db_project = models.Project(
        id=project_id,
        business_name=project.business_name,
        industry=project.industry,
        audience=project.audience,
        tone=project.tone,
        colors=project.colors,
        goal=project.goal
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(models.Project.created_at.desc()).all()

@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/projects/{project_id}/generate", response_model=schemas.AdCreativeResponse)
def generate_creatives(project_id: str, file: UploadFile = File(None), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    extracted_text = "Standard asset content extracted here."
    if file:
        extracted_text = f"User uploaded {file.filename}. Assume some assets."
        
    # Generate Ad Copy using Groq
    context = {
        "business_name": project.business_name,
        "industry": project.industry,
        "audience": project.audience,
        "tone": project.tone,
        "goal": project.goal
    }
    
    try:
        gen_result = generate_ad_copy(context, extracted_text)
    except Exception as e:
        print(f"LLM Error: {e}")
        gen_result = {
            "ad_copy": "Sample Headline\\n\\nSample Body\\n\\nCTA",
            "social_posts": ["Sample Short Post 1", "Sample Short Post 2"],
            "brochure_content": "Sample Brochure Details"
        }
    
    # Generate PDF Brochure
    pdf_path = generate_pdf(project.business_name, project.colors, gen_result.get("brochure_content", ""))
    
    # Upload to Supabase Storage
    bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "pdfs")
    pdf_name = f"{project_id}_{uuid.uuid4()}.pdf"
    pdf_url = upload_file_to_supabase(bucket, pdf_path, pdf_name)
        
    # Save to DB
    ad_id = str(uuid.uuid4())
    db_creative = models.AdCreative(
        id=ad_id,
        project_id=project_id,
        copy=gen_result.get("ad_copy", ""),
        social_posts=gen_result.get("social_posts", []),
        pdf_brochure_url=pdf_url
    )
    db.add(db_creative)
    db.commit()
    db.refresh(db_creative)
    
    return db_creative
    
@app.get("/projects/{project_id}/creatives", response_model=list[schemas.AdCreativeResponse])
def get_creatives(project_id: str, db: Session = Depends(get_db)):
    return db.query(models.AdCreative).filter(models.AdCreative.project_id == project_id).order_by(models.AdCreative.created_at.desc()).all()
