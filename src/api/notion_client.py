# src/api/notion_client.py

from pathlib import Path
from notion_client import APIResponseError
from dateutil import parser as date_parser
from src.utils.config import notion_client, logger, BASE_DOCKER_PATH, BASE_LOCAL_PATH


def docker_to_local_path(docker_path: str,
                         base_docker_path: str = BASE_DOCKER_PATH,
                         base_local_path: str = BASE_LOCAL_PATH) -> Path:
    """
    Convert a Docker path inside the container (e.g. /app/...) to a local path
    on the host machine, using pathlib for cross-platform path manipulation.
    """
    docker_path_obj = Path(docker_path)
    base_docker_path_obj = Path(base_docker_path)
    
    try:
        # Remove the leading Docker base path to get the relative part
        relative_path = docker_path_obj.relative_to(base_docker_path_obj)
    except ValueError:
        # In case docker_path doesn't start with /app or base_docker_path
        # fallback to using the full docker_path suffix
        relative_path = docker_path_obj

    # Combine the relative path with the base_local_path
    return Path(base_local_path) / relative_path


def update_notion_database(page_id, job_details, folder_path, doc_path, pdf_path):
    """
    Updates a Notion database page with job details and local file paths.
    This version uses pathlib for cross-platform path handling and converts
    Docker paths to local paths in a more robust way.

    Args:
        page_id (str): The ID of the Notion page to update.
        job_details (dict): A dictionary containing job-related information.
        folder_path (str): The Docker path to the folder containing the cover letter.
        doc_path (str): The Docker path to the Word document of the cover letter.
        pdf_path (str): The Docker path to the PDF document of the cover letter.

    Raises:
        APIResponseError: If there is an error response from the Notion API.
        Exception: For any other errors encountered during the update process.
    """

    # Convert Docker paths to local system paths (cross-platform)
    local_folder_path = docker_to_local_path(folder_path)
    local_doc_path = docker_to_local_path(doc_path)
    local_pdf_path = docker_to_local_path(pdf_path)

    # Convert to file URIs; as_uri() ensures correct formatting for the OS
    folder_uri = local_folder_path.resolve().as_uri()
    doc_uri = local_doc_path.resolve().as_uri()
    pdf_uri = local_pdf_path.resolve().as_uri()

    logger.info(f"Setting Job URL in Notion to: {job_details['Job URL']}")

    # Construct properties dictionary for Notion update
    properties = {
        "Company": {
            "type": "rich_text",
            "rich_text": [{"text": {"content": job_details.get("Company", "N/A")}}]
        },
        "Location": {
            "type": "rich_text",
            "rich_text": [{"text": {"content": job_details.get("Location", "N/A")}}]
        },
        "Job URL": {
            "type": "url",
            "url": job_details["Job URL"]
        },
        "Status": {
            "type": "select",
            "select": {"name": "New"}
        },
        "Salary Range": {
            "type": "rich_text",
            "rich_text": [{"text": {"content": job_details.get("Salary Range", "N/A")}}]
        },
        "Bonus?": {
            "type": "checkbox",
            "checkbox": False
        },
        "Notes": {
            "type": "rich_text",
            "rich_text": [{"text": {"content": "Auto-generated cover letter"}}]
        },
        "Experience Level": {
            "type": "rich_text",
            "rich_text": [{"text": {"content": job_details.get("Experience Level", "N/A")}}]
        },
        "Cover Letter Directory": {
            "type": "url",
            "url": folder_uri
        },
        "Word Document": {
            "type": "url",
            "url": doc_uri
        },
        "PDF Document": {
            "type": "url",
            "url": pdf_uri
        }
    }

    # Handle optional Application Deadline field
    application_deadline = job_details.get("Application Deadline", "N/A")
    if application_deadline != "N/A":
        try:
            deadline_date = date_parser.parse(application_deadline).date()
            properties["Application Deadline"] = {
                "type": "date",
                "date": {"start": deadline_date.isoformat()}
            }
        except ValueError:
            print(
                f"Warning: Could not parse Application Deadline as date: {application_deadline}. "
                "Omitting this field."
            )
    else:
        print("Application Deadline not provided or set to 'N/A'. Omitting this field.")

    # Attempt to update the Notion page with the constructed properties
    try:
        notion_client.pages.update(page_id=page_id, properties=properties)
    except APIResponseError as e:
        print(f"Notion API Error: {e.code} - {e.message}")
        raise
    except Exception as e:
        print(f"Error updating Notion: {str(e)}")
        raise

def is_page_archived(page_id):
    """
    Check if a Notion page is archived.

    Args:
        page_id (str): The ID of the Notion page to check.

    Returns:
        bool: True if the page is archived, False otherwise.

    Raises:
        Exception: If the page is not found or another API error occurs.
    """
    try:
        # Attempt to retrieve the page details from Notion using the page ID
        page = notion_client.pages.retrieve(page_id=page_id)
        # Return the 'archived' status of the page, defaulting to False if not found
        return page.get('archived', False)
    except APIResponseError as e:
        if e.status == 404:
            raise Exception(f"Page with ID {page_id} not found. Make sure you're using the correct page ID.")
        else:
            raise

def unarchive_page(page_id):
    """
    Unarchive a Notion page.

    Args:
        page_id (str): The ID of the Notion page to unarchive.

    Raises:
        Exception: If there is a permission error or another API error occurs.
    """
    try:
        # Attempt to update the page's 'archived' status to False (unarchive)
        notion_client.pages.update(page_id=page_id, archived=False)
    except APIResponseError as e:
        # Handle permission errors specifically
        if e.code == 'permission_error':
            raise Exception(f"You don't have permission to unarchive page {page_id}")
        else:
            raise