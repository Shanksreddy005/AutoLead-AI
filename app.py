import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, EmailStr
from dotenv import load_dotenv

# Import services
from services.enrichment import scrape_and_generate
from services.pdf_generator import generate_pdf
from services.email_service import send_email
from services.google_integration import log_and_upload

load_dotenv()

app = FastAPI(title="AutoLead AI Lead Automation Workflow")

# Ensure static directory exists for serving index.html
if not os.path.exists("static"):
    os.makedirs("static")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class LeadData(BaseModel):
    name: str
    email: EmailStr
    company_name: str
    company_url: HttpUrl

def process_lead(lead: LeadData):
    """
    Background task to process the lead end-to-end.
    """
    print(f"Starting workflow for {lead.company_name}...")
    try:
        # 1. Enrich data and generate report (LLM)
        report_markdown = scrape_and_generate(lead.company_url, lead.company_name)
        
        # 2. Generate PDF
        pdf_path = generate_pdf(report_markdown, lead.company_name)
        
        # 3. Send Email
        send_email(lead.name, lead.email, lead.company_name, pdf_path)
        
        # 4. Google Integrations (Bonus)
        log_and_upload(lead, pdf_path)
        
        print(f"Workflow completed successfully for {lead.company_name}")
    except Exception as e:
        print(f"Error processing lead {lead.company_name}: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    """Serve the frontend form."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/submit")
async def submit_lead(lead: LeadData, background_tasks: BackgroundTasks):
    """Receive lead information and trigger the automation workflow."""
    background_tasks.add_task(process_lead, lead)
    return JSONResponse(content={
        "status": "success", 
        "message": f"Lead for {lead.company_name} received. Processing workflow in background."
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
