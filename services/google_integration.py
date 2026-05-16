import os
from datetime import datetime

# Optional Google imports
try:
    import gspread
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_LIBS_INSTALLED = True
except ImportError:
    GOOGLE_LIBS_INSTALLED = False


def get_google_credentials():
    """Load Google Service Account credentials."""
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")
    if not os.path.exists(cred_path):
        return None
        
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    return Credentials.from_service_account_file(cred_path, scopes=scopes)


def append_to_sheet(lead_data, status: str):
    """Appends lead data to a Google Sheet."""
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id or sheet_id == "your_google_sheet_id_here":
        print("[MOCK] Sheets API not configured. Skipping sheet log.")
        return
        
    creds = get_google_credentials()
    if not creds:
        print("[MOCK] Google Service Account JSON missing. Skipping sheet log.")
        return
        
    try:
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            lead_data.name,
            str(lead_data.email),
            lead_data.company_name,
            status
        ]
        sheet.append_row(row)
        print(f"Successfully logged {lead_data.company_name} to Google Sheets.")
    except Exception as e:
        print(f"Error logging to Google Sheets: {e}")


def upload_to_drive(pdf_path: str):
    """Uploads the generated PDF to a Google Drive folder."""
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id or folder_id == "your_google_drive_folder_id_here":
        print("[MOCK] Drive API not configured. Skipping PDF upload.")
        return
        
    creds = get_google_credentials()
    if not creds:
        return
        
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': os.path.basename(pdf_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(pdf_path, mimetype='application/pdf', resumable=True)
        
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
        
        print(f"Successfully uploaded PDF to Google Drive with ID: {file.get('id')}")
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")


def log_and_upload(lead_data, pdf_path: str):
    """Main orchestration for Google Integrations."""
    if not GOOGLE_LIBS_INSTALLED:
        print("[MOCK] Google client libraries not installed.")
        return
        
    append_to_sheet(lead_data, "Processed")
    upload_to_drive(pdf_path)
