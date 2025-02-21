from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import requests
from openai import OpenAI
from notion_client import Client
import os
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch
from notion_client import APIResponseError
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from dotenv import load_dotenv
import logging
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black
from PyPDF2 import PdfReader
from jinja2 import Environment, FileSystemLoader
import subprocess
import json
import re
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration
ROOT_DIR = os.path.abspath(r"C:/Users/davle/Dropbox (Personal)/Jobs 2024")
COVER_LETTERS_DIR = os.path.join(ROOT_DIR, "cover_letters")


# Ensure the root and cover letters directories exist
os.makedirs(COVER_LETTERS_DIR, exist_ok=True)

# Set up OpenAI API
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Set up Notion API
notion = Client(auth=os.getenv('NOTION_API_KEY'))

# Function to extract job details using Beautiful Soup
# def extract_job_details_bs(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
   
#     job_title = soup.find('h1', class_='job-title')
#     company = soup.find('a', class_='company-name')
#     location = soup.find('div', class_='job-location')
#     requirements = soup.find('div', class_='job-requirements')
#     experience_level = soup.find('div', class_='experience-level')
#     application_deadline = soup.find('div', class_='application-deadline')
#     salary_range = soup.find('div', class_='salary-range')  # Add this line
   
#     if not all([job_title, company, location, requirements]):
#         return None

#     return {
#         'Job Title': job_title.text.strip() if job_title else 'N/A',
#         'Company': company.text.strip() if company else 'N/A',
#         'Location': location.text.strip() if location else 'N/A',
#         'Job URL': url,
#         'Requirements': requirements.text.strip() if requirements else 'N/A',
#         'Experience Level': experience_level.text.strip() if experience_level else 'N/A',
#         'Application Deadline': application_deadline.text.strip() if application_deadline else 'N/A',
#         'Salary Range': salary_range.text.strip() if salary_range else 'N/A'  # Add this line
#     }

def split_text(text: str, max_length: int = 384, stride: int = 128) -> List[str]:
    """Split the text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_length - stride):
        chunk = " ".join(words[i:i + max_length])
        chunks.append(chunk)
    return chunks

def answer_question(question: str, context: str) -> Dict[str, float]:
    """Get the answer for a single question-context pair."""
    inputs = tokenizer(question, context, return_tensors="pt", max_length=384, truncation=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.decode(inputs["input_ids"][0][answer_start:answer_end])
    
    confidence = torch.max(outputs.start_logits) + torch.max(outputs.end_logits)
    
    print(f"Raw answer: {answer}")
    print(f"Answer start: {answer_start}, Answer end: {answer_end}")
    
    # Remove special tokens from the answer
    answer = answer.replace("<s>", "").replace("</s>", "").strip()
    
    return {"answer": answer, "confidence": confidence.item()}

def expand_job_title_acronyms(title):
    # Dictionary of common job title acronyms and their expansions
    acronyms = {
        "VP": "Vice President",
        "CEO": "Chief Executive Officer",
        "CFO": "Chief Financial Officer",
        "CTO": "Chief Technology Officer",
        "COO": "Chief Operating Officer",
        "CIO": "Chief Information Officer",
        "CMO": "Chief Marketing Officer",
        "HR": "Human Resources",
        "PM": "Project Manager",
        "BA": "Business Analyst",
        "QA": "Quality Assurance",
        "UI": "User Interface",
        "UX": "User Experience",
        "PR": "Public Relations",
        "IT": "Information Technology",
        "SVP": "Senior Vice President",
        "EVP": "Executive Vice President",
        "AVP": "Assistant Vice President",
        "MD": "Managing Director",
        "GM": "General Manager",
    }
    
    # Split the title into words
    words = title.split()
    
    # Replace acronyms with their full forms
    expanded_words = [acronyms.get(word.upper(), word) for word in words]
    
    # Join the words back into a title
    expanded_title = " ".join(expanded_words)
    
    return expanded_title

def escape_latex(text):
    """
    Escape special LaTeX characters in a string, avoiding double escaping.
    """
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    
    # Use regex to find characters to replace
    pattern = '|'.join(re.escape(key) for key in latex_special_chars.keys())
    
    # Replace function
    def replace(match):
        char = match.group(0)
        # Check if the character is already escaped
        if char == '\\' and match.start() > 0 and text[match.start()-1] == '\\':
            return char
        return latex_special_chars[char]
    
    return re.sub(pattern, replace, text)

def clean_job_title(title):
    # Remove content within parentheses and the parentheses themselves
    title = re.sub(r'\([^)]*\)', '', title)
    
    # Remove content within square brackets and the brackets themselves
    title = re.sub(r'\[[^]]*\]', '', title)
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    return title.strip()

def extract_job_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
   
    soup = BeautifulSoup(response.content, 'html.parser')
   
    for script in soup(["script", "style"]):
        script.decompose()
   
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    limited_text = text[:14000]
    prompt = f"""
    Extract the following information from the job posting at {url}:
    1. Job Title
    2. Company
    3. Location
    4. Experience Level Required
    5. Application Deadline
    6. Salary Range (if available)
    Here's the content of the webpage:
    {limited_text}
    Provide the information in the following format:
    Job Title: [extracted job title]
    Company: [extracted company name]
    Location: [extracted location]
    Experience Level: [extracted experience level]
    Application Deadline: [extracted deadline]
    Salary Range: [extracted salary range or "Not specified" if not found]
    Ensure each piece of information is on a separate line and follows the exact format specified above.
    Do not include any additional text, explanations, or formatting.
    Only include the requested information as provided in the job description. No fake companies.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts job details from web pages."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )
    extracted_text = response.choices[0].message.content.strip()
   
    job_details = {}
    for line in extracted_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            job_details[key.strip()] = value.strip() if value.strip() != 'Not specified' else ''
   
    job_details['Job URL'] = url
   
    # Clean the job title
    if 'Job Title' in job_details and job_details['Job Title']:
        job_details['Job Title'] = expand_job_title_acronyms(clean_job_title(job_details['Job Title']))
   
    # Ensure all required fields are present
    required_fields = ['Job Title', 'Company', 'Location', 'Experience Level', 'Application Deadline', 'Salary Range']
    for field in required_fields:
        if field not in job_details:
            job_details[field] = ''
    
    return job_details


# Function to generate cover letter
def generate_cover_letter(job_details):
     # Add these print statements at the beginning of the function
    print("Debug: job_details passed to generate_cover_letter:")
    print(json.dumps(job_details, indent=2))
    logging.info(f"Debug: job_details passed to generate_cover_letter: {json.dumps(job_details, indent=2)}")

    current_date = datetime.now().strftime('%B %d, %Y')
    
    prompt = f"""
    Generate a very concise and professional cover letter for the following job:

    Job Title: {job_details.get('Job Title', 'Unknown Position')}
    Company: {job_details.get('Company', 'Unknown Company')}
    Location: {job_details.get('Location', 'N/A')}
    Experience Level: {job_details.get('Experience Level', 'N/A')}
    Application Deadline: {job_details.get('Application Deadline', 'N/A')}
    Salary Range: {job_details.get('Salary Range', 'N/A')}

    Candidate's information:
    Dr. David Leather is an Assistant Professor of Real Estate and Finance at Chapman University's Argyros School of Business and Economics. He holds a Ph.D. in Economics from the University of North Carolina at Chapel Hill, with concentrations in Macroeconomics and Finance. His research interests include Real Estate, Asset Pricing, Monetary Policy, and Macroeconomics. Dr. Leather has strong technical skills in programming, econometrics, and financial modeling, and has published research on land use uncertainty, real estate prices, and housing affordability.

    Guidelines:
    1. Do not include a saultation or header. Start with the body.
    2. Maintain a business professional tone throughout the letter.
    3. Highlight the candidate's relevant experience and skills that match the job requirements.
    4. Keep the letter concise, focusing on the most important qualifications.
    5. Demonstrate enthusiasm for the position and the company.
    6. Conclude with a call to action, expressing interest in an interview.
    7. Use varied sentence structures and avoid repetitive phrasing to create a more engaging letter.
    8. Be as concise as possible, while maintaining relevant details.
    9. Use the phrase "conducted extensive research" instead of "published" when referring to research.

    The cover letter should be 1-3 short paragraphs total.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional cover letter writer with expertise in academic and business writing."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )

    # Extract the cover letter text from the response and clean it
    cover_letter = response.choices[0].message.content.strip()
    
    # Remove any extraneous text or formatting
    cover_letter = cover_letter.split("```")[0].strip()

    return cover_letter


# Function to update Notion database

def update_notion_database(page_id, job_details, folder_path, doc_path, pdf_path):
    
    # Convert Docker paths to local Windows paths
    local_folder_path = folder_path.replace('/app/', 'C:/Users/davle/Dropbox (Personal)/')
    local_doc_path = doc_path.replace('/app/', 'C:/Users/davle/Dropbox (Personal)/')
    local_pdf_path = pdf_path.replace('/app/', 'C:/Users/davle/Dropbox (Personal)/')

    # Ensure Windows-style path separators
    local_folder_path = local_folder_path.replace('/', '\\')
    local_doc_path = local_doc_path.replace('/', '\\')
    local_pdf_path = local_pdf_path.replace('/', '\\')
    logger.info(f"Setting Job URL in Notion to: {job_details['Job URL']}")
    properties = {
        'Company': {
            'type': 'rich_text',
            'rich_text': [{'text': {'content': job_details.get('Company', 'N/A')}}]
        },
        'Location': {
            'type': 'rich_text',
            'rich_text': [{'text': {'content': job_details.get('Location', 'N/A')}}]
        },
        'Job URL': {
            'type': 'url',
            'url': job_details['Job URL']
        },
        'Status': {
            'type': 'select',
            'select': {'name': 'New'}
        },
        'Salary Range': {
            'type': 'rich_text',
            'rich_text': [{'text': {'content': job_details.get('Salary Range', 'N/A')}}]
        },
        'Bonus?': {
            'type': 'checkbox',
            'checkbox': False
        },
        'Notes': {
            'type': 'rich_text',
            'rich_text': [{'text': {'content': 'Auto-generated cover letter'}}]
        },
        'Experience Level': {
            'type': 'rich_text',
            'rich_text': [{'text': {'content': job_details.get('Experience Level', 'N/A')}}]
        },
        'Cover Letter Directory': {
            'type': 'url',
            'url': f"file:///{local_folder_path}"
        },
        'Word Document': {
            'type': 'url',
            'url': f"file:///{local_doc_path}"
        },
        'PDF Document': {
            'type': 'url',
            'url': f"file:///{local_pdf_path}"
        }
    }
    
    if 'Application Deadline' in job_details and job_details['Application Deadline'] != 'N/A':
        try:
            # Use dateutil parser which is more flexible in parsing date strings
            deadline_date = date_parser.parse(job_details['Application Deadline']).date()
            properties['Application Deadline'] = {
                'type': 'date',
                'date': {'start': deadline_date.isoformat()}
            }
        except ValueError:
            print(f"Warning: Could not parse Application Deadline as date: {job_details['Application Deadline']}. Omitting this field.")
    else:
        # If Application Deadline is not provided or is 'N/A', we omit it entirely
        print("Application Deadline not provided or set to 'N/A'. Omitting this field.")

    try:
        notion.pages.update(page_id=page_id, properties=properties)
    except APIResponseError as e:
        print(f"Notion API Error: {e.code} - {e.message}")
        raise
    except Exception as e:
        print(f"Error updating Notion: {str(e)}")
        raise
    
def clean_job_details(job_details):
    cleaned = {}
    for key, value in job_details.items():
        if key.startswith('- **'):
            clean_key = key.replace('- **', '').replace(':**', '').strip()
            clean_value = value.strip()
            if clean_value.startswith('**'):
                clean_value = clean_value[2:].strip()
            cleaned[clean_key] = clean_value
        elif key in ['Job URL']:
            cleaned[key] = value
    
    # Ensure we have the correct Job Title and Company
    if 'Job Title' in cleaned and cleaned['Job Title'] != 'Unknown Position':
        cleaned['Job Title'] = cleaned['Job Title']
    if 'Company' in cleaned and cleaned['Company'] != 'Unknown Company':
        cleaned['Company'] = cleaned['Company']
    
    return cleaned

def save_cover_letter_documents(job_details, cover_letter):
    company_name = job_details.get('Company', 'Unknown Company').replace(' ', '_')
    job_title = job_details.get('Job Title', 'Unknown Position').replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{company_name}_{job_title}_{timestamp}"
   
    docker_folder_path = os.path.join('/app/Jobs 2024/cover_letters', folder_name)
    os.makedirs(docker_folder_path, exist_ok=True)  
   
    logging.info(f"Creating folder: {docker_folder_path}")
    doc_path = os.path.join(docker_folder_path, "cover_letter.docx")
    tex_path = os.path.join(docker_folder_path, "cover_letter.tex")
    pdf_path = os.path.join(docker_folder_path, "cover_letter.pdf")
    
    # Save as Word document
    doc = Document()
    doc.add_paragraph(cover_letter)
    doc.save(doc_path)
   
    logging.info(f"Saved Word document: {doc_path}")
    
    # Create LaTeX document using Jinja2 template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('awesome_cv_cover_letter_template.tex')
   
    logging.info(f"Loaded LaTeX template: awesome_cv_cover_letter_template.tex")
    
    context = {
        'first_name': escape_latex('David'),
        'last_name': escape_latex('Leather'),
        'position': escape_latex('Assistant Professor of Real Estate and Finance'),
        'address': escape_latex('1 University Drive, Orange, CA 92866'),
        'phone': escape_latex('(+1) 508-648-6628'),
        'email': escape_latex('david.a.leather@gmail.com'),
        'website': escape_latex('www.daveleather.com'),
        'github': escape_latex('dleather'),
        'linkedin': escape_latex('dleather'),
        'recipient': escape_latex('Hiring Committee'),
        'date': escape_latex(datetime.now().strftime('%B %d, %Y')),
        'job_title': escape_latex(f"Job Application for {job_details.get('Job Title', 'N/A')}"),
        'opening': escape_latex('Dear Hiring Committee,'),
        'cover_letter_content': escape_latex(cover_letter)
    }

    # Only add company_address if both Company and Location are available
    company = job_details.get('Company', '').strip()
    location = job_details.get('Location', '').strip()
    if company and location:
        context['company_address'] = escape_latex(f"{company}\\\\{location}")
    elif company:
        context['company_address'] = escape_latex(company)
    elif location:
        context['company_address'] = escape_latex(location)
    
    logging.info(f"Defined content")
    rendered_tex = template.render(context)
   
    logging.info(f"Rendered context")
    with open(tex_path, 'w') as f:
        f.write(rendered_tex)
    
    # Compile LaTeX to PDF
    try:
        result = subprocess.run(
            ['xelatex', '-output-directory', docker_folder_path, tex_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info(f"LaTeX compilation output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"LaTeX compilation error:\nStdout: {e.stdout}\nStderr: {e.stderr}")
        raise
    
    # Save job details
    job_details_path = os.path.join(docker_folder_path, "job_details.txt")
    with open(job_details_path, 'w') as f:
        for key, value in job_details.items():
            f.write(f"{key}: {escape_latex(str(value))}\n")
   
    logging.info(f"Saved job details: {job_details_path}")
    
    windows_folder_path = os.path.join(r'C:\Users\davle\Dropbox (Personal)\Jobs 2024\cover_letters', folder_name)
    windows_doc_path = os.path.join(windows_folder_path, "cover_letter.docx")
    windows_pdf_path = os.path.join(windows_folder_path, "cover_letter.pdf")
   
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Contents of {docker_folder_path}:")
    logging.info(os.listdir(docker_folder_path))
   
    return docker_folder_path, doc_path, pdf_path, windows_folder_path, windows_doc_path, windows_pdf_path

def is_one_page_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return len(reader.pages) == 1


def is_page_archived(page_id):
    try:
        page = notion.pages.retrieve(page_id=page_id)
        return page.get('archived', False)
    except APIResponseError as e:
        if e.status == 404:
            raise Exception(f"Page with ID {page_id} not found. Make sure you're using the correct page ID.")
        else:
            raise

def unarchive_page(page_id):
    try:
        notion.pages.update(page_id=page_id, archived=False)
    except APIResponseError as e:
        if e.code == 'permission_error':
            raise Exception(f"You don't have permission to unarchive page {page_id}")
        else:
            raise

def fetch_job_posting_text(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        logger.info(f"Fetching job posting from URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully fetched job posting. Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        logger.info(f"Extracted text (first 500 chars): {text[:500]}...")
        return text
    except Exception as e:
        logger.error(f"Error fetching job posting: {str(e)}", exc_info=True)
        return ""

def clean_text(text):
    # Remove common LinkedIn boilerplate text
    text = re.sub(r'LinkedIn.*?Skip to main content', '', text, flags=re.DOTALL)
    text = re.sub(r'Agree & Join LinkedIn.*?Cookie Policy\.', '', text, flags=re.DOTALL)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
       
        logger.info(f"Received webhook data: {data}")
        url = data['Job URL']
        page_id = data['ID']

        if is_page_archived(page_id):
            unarchive_page(page_id)
            logger.info(f"Page {page_id} was archived. It has been unarchived.")

        # Fetch the job posting text
        job_details = extract_job_details(url)
        job_details['Job URL'] = url  # Make sure to add the URL to the job details
        logger.info(f"Extracted job details: {job_details}")

        cover_letter = generate_cover_letter(job_details)
       
        docker_folder_path, doc_path, pdf_path, windows_folder_path, windows_doc_path, windows_pdf_path = save_cover_letter_documents(job_details, cover_letter)
       
        logger.info(f"Documents saved in Docker path: {docker_folder_path}")
        logger.info(f"Documents should appear in Windows path: {windows_folder_path}")
        logger.info(f"Updating Notion with: {job_details}")
        update_notion_database(page_id, job_details, windows_folder_path, windows_doc_path, windows_pdf_path)
       
        return jsonify({
            'status': 'success',
            'documents_folder': windows_folder_path
        })
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)