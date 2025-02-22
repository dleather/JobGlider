import requests
from bs4 import BeautifulSoup
from typing import Dict
import torch
from src.utils.config import openai_client, logger, model, tokenizer
from src.utils.text_processing import expand_job_title_acronyms, clean_job_title

def extract_job_details(url):
    """
    Extract job details from a given job posting URL.

    This function sends a GET request to the specified URL, processes the HTML content
    to remove unnecessary elements, and extracts relevant job information using an AI model.
    The extracted details include the job title, company, location, experience level, 
    application deadline, and salary range. The function ensures that all required fields 
    are present in the returned dictionary, even if some information is not available.

    Args:
        url (str): The URL of the job posting to extract details from.

    Returns:
        dict: A dictionary containing the extracted job details with keys such as 'Job Title',
              'Company', 'Location', 'Experience Level', 'Application Deadline', 'Salary Range',
              and 'Job URL'.
    """
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
    response = openai_client.chat.completions.create(
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

def fetch_job_posting_text(url: str) -> str:
    """
    Fetch and clean the text content of a job posting from a given URL.

    This function sends a GET request to the specified URL, retrieves the HTML content,
    and processes it to remove script and style elements. It then extracts and cleans
    the text content, removing unnecessary whitespace and formatting, and returns the
    cleaned text.

    Args:
        url (str): The URL of the job posting to fetch.

    Returns:
        str: The cleaned text content of the job posting. If an error occurs during
             the fetching process, an empty string is returned.
    """
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

def answer_question(question: str, context: str) -> Dict[str, float]:
    """
    Generate an answer to a given question based on the provided context using a pre-trained language model.

    This function utilizes a tokenizer and a language model to process the input question and context,
    and then predicts the most likely answer span within the context. It also calculates a confidence
    score for the predicted answer based on the model's output logits.

    Args:
        question (str): The question for which an answer is sought.
        context (str): The context or passage of text within which the answer is to be found.

    Returns:
        Dict[str, float]: A dictionary containing the predicted answer and its confidence score.
                          The dictionary has two keys:
                          - "answer": A string representing the extracted answer from the context.
                          - "confidence": A float representing the confidence score of the answer,
                            derived from the model's logits.

    Note:
        The function assumes that the tokenizer and model are pre-initialized and available in the
        global scope. It also assumes the use of PyTorch for tensor operations.
    """
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
    
    # Convert confidence to float explicitly
    return {"answer": answer, "confidence": float(confidence.item())}

def clean_job_details(job_details):
    """
    Clean and format job details extracted from a job posting.

    This function processes a dictionary of job details, removing unnecessary
    formatting and ensuring that key information such as 'Job Title' and 'Company'
    are correctly formatted and present.

    Args:
        job_details (dict): A dictionary containing raw job details with potential
                            formatting issues.

    Returns:
        dict: A cleaned dictionary with properly formatted job details.
    """
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