import json
from datetime import datetime
from src.utils.config import openai_client, logger

def generate_cover_letter(job_details):
    """
    Generate a concise and professional cover letter based on the provided job details.

    Args:
        job_details (dict): A dictionary containing job-related information such as 
                            'Job Title', 'Company', 'Location', 'Experience Level', 
                            'Application Deadline', and 'Salary Range'.

    Returns:
        str: A string representing the generated cover letter.
    """
    # Add these print statements at the beginning of the function
    print("Debug: job_details passed to generate_cover_letter:")
    print(json.dumps(job_details, indent=2))
    logger.info(f"Debug: job_details passed to generate_cover_letter: {json.dumps(job_details, indent=2)}")

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

    response = openai_client.chat.completions.create(
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