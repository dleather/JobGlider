# tests/integration/test_job_parser_integration.py
import pytest
import responses
from types import SimpleNamespace
import src.utils.config as config
import src.core.job_parser as job_parser

from src.core.job_parser import extract_job_details, fetch_job_posting_text

def fake_create(**kwargs):
    # A fake response simulating OpenAI's API response
    class FakeMessage:
        def __init__(self, content):
            self.content = content

    class FakeChoice:
        def __init__(self, message_content):
            self.message = FakeMessage(message_content)

    fake_text = "\n".join([
        "Job Title: Senior Developer",
        "Company: ACME Corp",
        "Location: Some City",
        "Experience Level: Mid-Level",
        "Application Deadline: ",
        "Salary Range: "
    ])
    # Return an object with a 'choices' attribute containing our fake choice
    return type("FakeResponse", (), {"choices": [FakeChoice(fake_text)]})

# Patch openai_client so that its chat.completions.create method returns our fake response
config.openai_client = SimpleNamespace(
    chat=SimpleNamespace(
        completions=SimpleNamespace(
            create=fake_create
        )
    )
)

# <-- Add these two lines to propagate the patch into job_parser.
job_parser.openai_client = config.openai_client

def test_extract_job_details_live():
    """
    A more integrated test that hits a real website or a local test server.

    NOTE: This test requires internet if you're hitting a real URL, or
    running a local dev server with a known page. If you do not want to make
    live calls, spin up a local test HTTP server that serves a sample HTML
    file so you're still 'integrating' but not relying on external sites.
    """
    TEST_URL = "http://127.0.0.1:8000/test_job_page.html"
    # Or a real staging site, or a local test server, etc.

    job_details = extract_job_details(TEST_URL)
    assert "Job Title" in job_details
    assert job_details["Job Title"] == "Senior Developer"
    assert "Company" in job_details
    assert job_details["Company"] == "ACME Corp"
    assert "Location" in job_details
    assert job_details["Location"] == "Some City"
    assert "Experience Level" in job_details
    assert job_details["Experience Level"] == "Mid-Level"
    assert "Application Deadline" in job_details
    assert job_details["Application Deadline"] == ""
    assert "Salary Range" in job_details
    assert job_details["Salary Range"] == ""

@responses.activate
def test_fetch_job_posting_text_live():
    """
    Similar to above, fetch actual HTML content from a live or local URL,
    verifying we get expected text back. 
    """
    TEST_URL = "http://127.0.0.1:8000/test_job_page.html"
    expected_html = """
    <html>
      <head><title>Test Job Page</title></head>
      <body>
        <h1>Senior Developer</h1>
        <div>Location: Some City</div>
        <div>Experience Level: Mid-Level</div>
      </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        TEST_URL,
        body=expected_html,
        status=200,
        content_type='text/html'
    )
    
    text = fetch_job_posting_text(TEST_URL)
    assert "Senior Developer" in text
    assert "Location: Some City" in text
    assert "Experience Level: Mid-Level" in text

