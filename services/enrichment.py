import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

def scrape_website(url: str) -> str:
    """Scrape visible text from a given URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        # Limit text length to avoid token limits
        return text[:10000] 
    except Exception as e:
        print(f"Warning: Failed to scrape {url}: {e}")
        return "Could not retrieve website content. Generate a generic report based on the company name."

def generate_insights(company_name: str, website_content: str) -> str:
    """Use Gemini LLM to generate a personalized audit report in Markdown."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("Warning: Valid GEMINI_API_KEY not found. Using fallback mock report.")
        return get_mock_report(company_name)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are a business consultant analyzing a prospective client.
        Company Name: {company_name}
        Website Content: {website_content}
        
        Create a professional, personalized audit report for this company.
        Format your response in Markdown. Do not include raw HTML.
        Include the following sections:
        
        # AI Readiness Audit for {company_name}
        
        ## Executive Summary
        (A brief 2-3 sentence overview of what the company does based on their website and their potential for AI integration.)
        
        ## Key Observations
        (List 3 bullet points of positive aspects about their current offering/website.)
        
        ## Potential Areas for Improvement
        (List 2-3 areas where their operations or customer experience could be optimized.)
        
        ## Proposed AI Automation Solutions
        (Suggest 2 specific, actionable AI tools or automated workflows that would specifically benefit their business model.)
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Warning: LLM generation failed: {e}")
        return get_mock_report(company_name)

def get_mock_report(company_name: str) -> str:
    """Fallback mock report if API fails or key is missing."""
    return f"""
# AI Readiness Audit for {company_name}

## Executive Summary
Based on the initial assessment, {company_name} has established a solid foundation in its market. There are significant opportunities to leverage modern AI technologies to streamline operations and enhance customer engagement.

## Key Observations
* Strong brand presence and clear value proposition.
* Structured service offerings that are well communicated.
* Growing target market with potential for scalable solutions.

## Potential Areas for Improvement
* Lead intake and follow-up processes appear manual.
* Customer support could benefit from 24/7 automated assistance.
* Data from user interactions is not fully utilized for personalized outreach.

## Proposed AI Automation Solutions
* **Automated Lead Enrichment:** Implement a workflow to automatically gather insights on new leads, similar to this very report, allowing the sales team to focus on closing rather than researching.
* **Intelligent Customer Support Chatbot:** Deploy an AI agent trained on your specific documentation to answer common queries instantly.
"""

def scrape_and_generate(url: str, company_name: str) -> str:
    """Orchestrator function for the enrichment step."""
    content = scrape_website(str(url))
    report_markdown = generate_insights(company_name, content)
    return report_markdown
