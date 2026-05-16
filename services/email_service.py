import os
import smtplib
from email.message import EmailMessage
import mimetypes

def send_email(name: str, to_email: str, company_name: str, pdf_path: str):
    """Sends the generated PDF report via email."""
    
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    
    if not sender_email or not sender_password or sender_email == "your_email@gmail.com":
        print(f"Warning: Email credentials not configured. Skipping email to {to_email}.")
        print(f"[MOCK EMAIL] To: {to_email} | Subject: Your AI Readiness Audit | Attachment: {pdf_path}")
        return
        
    msg = EmailMessage()
    msg['Subject'] = f"Your AI Readiness Audit - {company_name}"
    msg['From'] = sender_email
    msg['To'] = to_email
    
    body = f"""Hi {name},

Thank you for your interest in AutoLead AI!

We have analyzed {company_name}'s digital presence and compiled a personalized AI Readiness Audit for your review. 
Please find the report attached to this email.

Best regards,
The AutoLead AI Team
"""
    msg.set_content(body)
    
    # Attach the PDF
    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            
        msg.add_attachment(
            pdf_data, 
            maintype='application', 
            subtype='pdf', 
            filename=os.path.basename(pdf_path)
        )
    except Exception as e:
        print(f"Error attaching PDF: {e}")
        return

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Successfully sent email to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
