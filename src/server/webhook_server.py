from flask import Flask, request, jsonify
from src.core.job_parser import extract_job_details
from src.core.document_handler import save_cover_letter_documents
from src.api.notion_client import update_notion_database, is_page_archived, unarchive_page
from src.core.cover_letter import generate_cover_letter
from src.utils.config import logger

app = Flask(__name__)

@app.route('/')
def home():
    """
    Home route for the Flask application.

    Returns:
        str: A simple greeting message.
    """
    return "Hello, Flask!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint to process incoming job data.

    This function handles POST requests, extracts job details from the provided URL,
    generates a cover letter, saves the documents, and updates the Notion database.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    try:
        # Parse JSON data from the request
        data = request.json
       
        logger.info(f"Received webhook data: {data}")
        url = data['Job URL']
        page_id = data['ID']

        # Check if the Notion page is archived and unarchive if necessary
        if is_page_archived(page_id):
            unarchive_page(page_id)
            logger.info(f"Page {page_id} was archived. It has been unarchived.")

        # Extract job details from the provided URL
        job_details = extract_job_details(url)
        job_details['Job URL'] = url  # Ensure the URL is included in the job details
        logger.info(f"Extracted job details: {job_details}")

        # Generate a cover letter based on the job details
        cover_letter = generate_cover_letter(job_details)
       
        # Save the cover letter documents and get their paths
        docker_folder_path, doc_path, pdf_path, windows_folder_path, windows_doc_path, windows_pdf_path = save_cover_letter_documents(job_details, cover_letter)
       
        logger.info(f"Documents saved in Docker path: {docker_folder_path}")
        logger.info(f"Documents should appear in Windows path: {windows_folder_path}")
        logger.info(f"Updating Notion with: {job_details}")

        # Update the Notion database with the job details and document paths
        update_notion_database(page_id, job_details, windows_folder_path, windows_doc_path, windows_pdf_path)
       
        return jsonify({
            'status': 'success',
            'documents_folder': windows_folder_path
        })
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Start the Flask application
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)