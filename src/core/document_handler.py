# src/core/document_handler.py
import os
from datetime import datetime
from docx import Document
from jinja2 import Environment, FileSystemLoader
from src.utils.text_processing import escape_latex
from PyPDF2 import PdfReader
import subprocess
from src.utils.config import BASE_DOCKER_PATH, COVER_LETTERS_DIR, logger

def save_cover_letter_documents(job_details, cover_letter):
    """
    Save the cover letter and job details in multiple formats and locations.

    This function creates a directory named after the company, job title, and current timestamp.
    It saves the cover letter as a Word document, a LaTeX document, and a PDF. It also saves
    the job details in a text file within the created directory.

    Args:
        job_details (dict): A dictionary containing job-related information such as 'Company',
                            'Job Title', and 'Location'.
        cover_letter (str): The content of the cover letter to be saved.

    Returns:
        tuple: A tuple containing the paths to the created directory, Word document, and PDF.
    """
    company_name = job_details.get('Company', 'Unknown Company').replace(' ', '_')
    job_title = job_details.get('Job Title', 'Unknown Position').replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{company_name}_{job_title}_{timestamp}"
   
    docker_folder_path = os.path.join(COVER_LETTERS_DIR, folder_name)
    os.makedirs(docker_folder_path, exist_ok=True)  
   
    logger.info(f"Creating folder: {docker_folder_path}")
    doc_path = os.path.join(docker_folder_path, "cover_letter.docx")
    tex_path = os.path.join(docker_folder_path, "cover_letter.tex")
    pdf_path = os.path.join(docker_folder_path, "cover_letter.pdf")
    
    # Save as Word document
    doc = Document()
    doc.add_paragraph(cover_letter)
    doc.save(doc_path)
   
    logger.info(f"Saved Word document: {doc_path}")
    
    # Create LaTeX document using Jinja2 template
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates', 'latex')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('awesome_cv_cover_letter_template.tex')
   
    logger.info(f"Loaded LaTeX template: awesome_cv_cover_letter_template.tex")
    
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
    
    logger.info(f"Defined content")
    rendered_tex = template.render(context)
   
    logger.info(f"Rendered context")
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
        logger.info(f"LaTeX compilation output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"LaTeX compilation error:\nStdout: {e.stdout}\nStderr: {e.stderr}")
        raise
    
    # Save job details
    job_details_path = os.path.join(docker_folder_path, "job_details.txt")
    with open(job_details_path, 'w') as f:
        for key, value in job_details.items():
            f.write(f"{key}: {escape_latex(str(value))}\n")
   
    logger.info(f"Saved job details: {job_details_path}")
    
    return docker_folder_path, doc_path, pdf_path

def is_one_page_pdf(pdf_path):
    """
    Check if a PDF file contains only one page.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        bool: True if the PDF contains exactly one page, False otherwise.
    """
    reader = PdfReader(pdf_path)
    return len(reader.pages) == 1
