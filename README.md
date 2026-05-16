# AutoLead AI - Automated Lead Enrichment Engine

AutoLead AI is a full-stack automated workflow designed to instantly process new business leads. When a prospective client submits their information, the system automatically scrapes their company website, uses Google's Gemini 1.5 Flash LLM to generate a personalized "AI Readiness Audit," converts the analysis into a professionally styled PDF, and emails it back to the prospect—all without human intervention.

## Features
- **Instant Web Scraping:** Extracts context directly from the prospect's submitted URL.
- **AI-Powered Insights:** Utilizes Gemini 1.5 Flash to synthesize website data and generate actionable business insights and tailored AI automation proposals.
- **Automated PDF Rendering:** Converts the LLM-generated Markdown into a clean, styled PDF document dynamically using `xhtml2pdf`.
- **Automated Email Delivery:** Secures and sends the generated PDF directly to the lead via SMTP.
- **Asynchronous Architecture:** Built on FastAPI using `BackgroundTasks` so the frontend remains incredibly fast and responsive while the heavy processing happens behind the scenes.
- **Cloud Integrations:** Logs all processed leads to Google Sheets and archives all generated PDFs to Google Drive via Service Account credentials.
- **Graceful Fallbacks:** Handles missing API keys or scraping blocks elegantly with built-in mock data to ensure the workflow never breaks.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shanksreddy005/AutoLead-AI.git
   cd AutoLead-AI
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables:**
   - Copy `.env.example` to `.env`.
   - Add your Gemini API key (`GEMINI_API_KEY`).
   - Add your Gmail credentials (`EMAIL_ADDRESS`, `EMAIL_PASSWORD`) using an App Password.
   - (Bonus) Add a `service_account.json` file to the root directory for Google Sheets & Drive logging. Set the respective IDs in `.env`.

5. **Run the Application:**
   ```bash
   uvicorn app:app --reload
   ```
6. **Access the Application:** Open `http://localhost:8000` in your web browser.

## Tech Stack
- **Backend:** Python, FastAPI, Pydantic
- **AI / LLM:** Google Generative AI (Gemini 1.5 Flash)
- **Scraping:** Requests, BeautifulSoup4
- **PDF Generation:** Markdown, xhtml2pdf
- **Integrations:** smtplib (Email), Google Sheets API, Google Drive API
- **Frontend:** HTML5, Tailwind CSS
