import os
os.environ["PYTEST"] = "1"

import pytest
from unittest.mock import MagicMock
from pathlib import Path
import subprocess
import time
import shutil
import tempfile
import os
import pytest
import tempfile
from tests.fake_notion import FakeNotionClient
from src.api import notion_client
from src.server.webhook_server import app
import torch

@pytest.fixture
def mock_notion_client():
    """Mock Notion client with API behavior."""
    client = MagicMock()
    client.pages.retrieve.return_value = {"archived": False}
    client.pages.update.return_value = {"status": "success"}
    return client

@pytest.fixture
def temp_paths():
    """Fixture for test paths."""
    return {
        "docker_path": "/app/some_folder/file.txt",
        "local_path": "C:/Users/davle/Dropbox (Personal)/some_folder/file.txt"
    }

@pytest.fixture
def raw_job_titles():
    return [
        "VP of Marketing",
        "COO at ExampleCorp",
        "SVP or Executive VP",
        "Senior PM and BA",
        "CTO / CFO",
        "General Manager",
    ]

@pytest.fixture
def raw_text():
    return (
        "LinkedIn is a platform. Skip to main content "
        "Here is some text with parentheses (remove me) "
        "and [delete me as well]. "
        "Agree & Join LinkedIn Something about Cookie Policy."
    )

@pytest.fixture
def latex_strings():
    return [
        "&special",
        "Look 50% better!",
        "Price is $100",
        "Use #this for something",
        "Curly braces { and }",
        "File_name_with_underscore",
        r"Already \escaped slash"
    ]

@pytest.fixture
def base_paths():
    return {
        "BASE_DOCKER_PATH": "/app",
        "BASE_LOCAL_PATH": "C:/Users/davle/Dropbox (Personal)"
    }

@pytest.fixture
def mock_openai_client():
    client = MagicMock()
    # Add mock responses as needed
    return client

@pytest.fixture
def mock_mistral_model():
    model = MagicMock()
    # Add mock responses as needed
    return model

@pytest.fixture
def mock_html_content():
    """
    Return a small snippet of HTML that might be returned by a job URL.
    """
    return """
    <html>
      <head><title>Test Job Page</title></head>
      <body>
        <h1>Senior Developer</h1>
        <div>Company: ACME Corp</div>
        <div>Location: Some City</div>
        <p>Experience Level: Mid-Level</p>
        <p>Application Deadline: </p>
        <p>Salary Range: Not specified</p>
      </body>
    </html>
    """


@pytest.fixture
def mock_openai_response():
    """
    Return a mocked response object that simulates the structure
    from openai_client.chat.completions.create(...)
    """
    class MockChoice:
        def __init__(self, content):
            self.message = MagicMock(content=content)

    class MockOpenAIResponse:
        def __init__(self, text):
            self.choices = [MockChoice(text)]

    return MockOpenAIResponse


@pytest.fixture
def mock_model_output():
    """
    Return a mock object simulating model output for `answer_question`.
    """
    mock_output = MagicMock()
    mock_output.start_logits = torch.tensor([0, 0, 10])  # Convert to tensor
    mock_output.end_logits = torch.tensor([0, 0, 12])
    return mock_output

@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.isdir(static_dir):
        os.makedirs(static_dir, exist_ok=True)
        # Create a minimal test file
        with open(os.path.join(static_dir, "test_job_page.html"), "w") as f:
            f.write("<html><head><title>Test Job Page</title></head><body><h1>Senior Developer</h1><div>Company: ACME Corp</div><div>Location: Some City</div><p>Experience Level: Mid-Level</p></body></html>")
    proc = subprocess.Popen(["python", "-m", "http.server", "8000"], cwd=static_dir)
    time.sleep(1)  # Allow the server time to start up
    yield
    proc.terminate()
    
@pytest.fixture
def job_details_fixture():
    """A fixture returning a minimal job details dictionary."""
    return {
        "Company": "TestCorp",
        "Job Title": "TestEngineer",
        "Location": "TestCity",
        "Job URL": "http://example.com"
    }

@pytest.fixture
def cover_letter_text_fixture():
    """A fixture returning a minimal cover letter text."""
    return "This is a test cover letter."

@pytest.fixture
def temp_output_dir():
    """
    Create a temporary directory for test outputs and yield the path.
    After test completion, remove it to keep things clean.
    """
    temp_dir = tempfile.mkdtemp(prefix="cover_letter_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)
    

@pytest.fixture
def one_page_pdf_fixture():
    """
    Create a temporary 1-page PDF file.
    We'll use PyPDF2 or a minimal approach to generate it in-memory.
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_file_name = tmp_file.name
    tmp_file.close()

    # Create a minimal 1-page PDF using PyPDF2
    from PyPDF2 import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)  # 1-inch by 1-inch blank page
    with open(tmp_file_name, "wb") as f:
        writer.write(f)
    yield tmp_file_name

    # Cleanup
    if os.path.exists(tmp_file_name):
        os.remove(tmp_file_name)

@pytest.fixture
def two_page_pdf_fixture():
    """
    Create a temporary 2-page PDF file.
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_file_name = tmp_file.name
    tmp_file.close()

    from PyPDF2 import PdfWriter
    writer = PdfWriter()
    # Create 2 blank pages
    writer.add_blank_page(width=72, height=72)
    writer.add_blank_page(width=72, height=72)
    with open(tmp_file_name, "wb") as f:
        writer.write(f)
    yield tmp_file_name

    if os.path.exists(tmp_file_name):
        os.remove(tmp_file_name)
        

@pytest.fixture
def dummy_job_details():
    """Provide a sample job details dictionary."""
    return {
        "Job Title": "Software Engineer",
        "Company": "Acme Corp",
        "Location": "San Francisco",
        "Experience Level": "Mid-Level",
        "Application Deadline": "2025-03-01",
        "Salary Range": "$100k-$150k"
    }
    
    # Fixture that provides our fake notion client.
@pytest.fixture
def fake_notion_client():
    return FakeNotionClient()

# Patch the global notion_client in the module so that all functions use our fake.
@pytest.fixture(autouse=True)
def patch_notion_client(monkeypatch, fake_notion_client):
    monkeypatch.setattr(notion_client, "notion_client", fake_notion_client)
    
@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Simulate that the Notion page is not archived.
    monkeypatch.setattr(
        "src.server.webhook_server.is_page_archived", 
        lambda page_id: False
    )
    # Simulate that unarchiving does nothing.
    monkeypatch.setattr(
        "src.server.webhook_server.unarchive_page", 
        lambda page_id: None
    )
    # Return a dummy set of job details.
    dummy_job_details = {
        "Job Title": "Test Job",
        "Company": "Test Company",
        "Location": "Test Location",
        "Experience Level": "Mid-Level",
        "Application Deadline": "",
        "Salary Range": ""
    }
    monkeypatch.setattr(
        "src.server.webhook_server.extract_job_details", 
        lambda url: dummy_job_details
    )
    # Return a dummy cover letter.
    monkeypatch.setattr(
        "src.server.webhook_server.generate_cover_letter",
        lambda job_details: "Dummy Cover Letter"
    )
    # Return dummy file paths for documents.
    dummy_paths = (
        "/dummy/docker_folder",
        "/dummy/doc_path.docx",
        "/dummy/pdf_path.pdf",
        "C:/dummy/windows_folder",
        "C:/dummy/windows_doc.docx",
        "C:/dummy/windows_pdf.pdf"
    )
    monkeypatch.setattr(
        "src.server.webhook_server.save_cover_letter_documents",
        lambda jd, cl: dummy_paths
    )
    # Simulate a successful Notion update.
    monkeypatch.setattr(
        "src.server.webhook_server.update_notion_database",
        lambda page_id, jd, wf, wd, wp: None
    )

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client