import os
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, EmailStr
from dotenv import load_dotenv

# Import services
from services.enrichment import scrape_and_generate
from services.pdf_generator import generate_pdf
from services.email_service import send_email
from services.google_integration import log_and_upload
import models
import database

models.Base.metadata.create_all(bind=database.engine)

load_dotenv()

app = FastAPI(title="AutoLead AI Lead Automation Workflow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directories exist
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("reports"):
    os.makedirs("reports")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

class LeadData(BaseModel):
    name: str
    email: EmailStr
    company_name: str
    company_url: HttpUrl
    session_id: str = None

def update_db_status(sid: str, status: str, pdf_path: str = None):
    if not sid: return
    db = database.SessionLocal()
    try:
        db_lead = db.query(models.Lead).filter(models.Lead.session_id == sid).first()
        if db_lead:
            db_lead.status = status
            if pdf_path:
                db_lead.pdf_path = pdf_path
            db.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        db.close()

async def process_lead(lead: LeadData):
    """
    Background task to process the lead end-to-end.
    """
    print(f"Starting workflow for {lead.company_name}...")
    sid = lead.session_id
    try:
        if sid: 
            await manager.send_message("Scraping website and analyzing with AI...", sid)
            await asyncio.to_thread(update_db_status, sid, "Scraping website and analyzing with AI...")
            
        # 1. Enrich data and generate report (LLM)
        report_markdown = await asyncio.to_thread(scrape_and_generate, lead.company_url, lead.company_name)
        
        if sid: 
            await manager.send_message("Generating PDF Audit Report...", sid)
            await asyncio.to_thread(update_db_status, sid, "Generating PDF Audit Report...")
            
        # 2. Generate PDF
        pdf_path = await asyncio.to_thread(generate_pdf, report_markdown, lead.company_name)
        
        if sid: 
            await manager.send_message("Emailing report...", sid)
            await asyncio.to_thread(update_db_status, sid, "Emailing report...", pdf_path)
            
        # 3. Send Email
        await asyncio.to_thread(send_email, lead.name, lead.email, lead.company_name, pdf_path)
        
        if sid: 
            await manager.send_message("Logging to CRM...", sid)
            await asyncio.to_thread(update_db_status, sid, "Logging to CRM...")
            
        # 4. Google Integrations (Bonus)
        await asyncio.to_thread(log_and_upload, lead, pdf_path)
        
        if sid: 
            await manager.send_message("Completed successfully! Check your email.", sid)
            await asyncio.to_thread(update_db_status, sid, "Completed")
            
        print(f"Workflow completed successfully for {lead.company_name}")
    except Exception as e:
        if sid: 
            await manager.send_message(f"Error: {str(e)}", sid)
            await asyncio.to_thread(update_db_status, sid, f"Error: {str(e)}")
        print(f"Error processing lead {lead.company_name}: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    """Serve the frontend form."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/leads")
async def get_leads():
    """Fetch all processed leads for the React Dashboard."""
    db = database.SessionLocal()
    try:
        leads = db.query(models.Lead).order_by(models.Lead.created_at.desc()).all()
        return leads
    finally:
        db.close()

@app.post("/api/submit")
async def submit_lead(lead: LeadData, background_tasks: BackgroundTasks):
    """Receive lead information and trigger the automation workflow."""
    db = database.SessionLocal()
    try:
        db_lead = models.Lead(
            name=lead.name,
            email=lead.email,
            company_name=lead.company_name,
            company_url=str(lead.company_url),
            session_id=lead.session_id,
            status="Received"
        )
        db.add(db_lead)
        db.commit()
    finally:
        db.close()

    background_tasks.add_task(process_lead, lead)
    return JSONResponse(content={
        "status": "success", 
        "message": f"Lead for {lead.company_name} received. Connecting to status tracker..."
    })

@app.websocket("/ws/status/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
