# tests/unit/test_notion_client.py

import os
from pathlib import Path
import tempfile
import pytest
from notion_client import APIResponseError

# Import the module under test.
from src.api import notion_client

# ------------------
# Tests for docker_to_local_path
# ------------------

def test_docker_to_local_path_matching():
    """
    When the docker_path starts with the base_docker_path, the function should
    return the local path with the relative part appended.
    """
    docker_path = "/app/some/dir/file.txt"
    base_docker_path = "/app"
    base_local_path = "/local"
    result = notion_client.docker_to_local_path(docker_path, base_docker_path, base_local_path)
    expected = Path("/local/some/dir/file.txt")
    assert result == expected

def test_docker_to_local_path_non_matching():
    """
    When the docker_path does not start with base_docker_path, the function should
    fallback to using the full docker_path (appended to base_local_path).
    Note: If the docker_path is absolute, Path concatenation returns the docker_path.
    """
    docker_path = "/other/dir/file.txt"
    base_docker_path = "/app"
    base_local_path = "/local"
    result = notion_client.docker_to_local_path(docker_path, base_docker_path, base_local_path)
    # Because Path("/local") / Path("/other/dir/file.txt") yields Path("/other/dir/file.txt")
    expected = Path("/other/dir/file.txt")
    assert result == expected

# ------------------
# Tests for update_notion_database
# ------------------

def test_update_notion_database_success(fake_notion_client, tmp_path):
    """
    Test that update_notion_database converts Docker paths to local URIs
    and calls notion_client.pages.update with the expected properties.
    """
    # Define dummy job details.
    job_details = {
        "Company": "Test Company",
        "Location": "Test Location",
        "Job URL": "http://example.com",
        "Salary Range": "$100k",
        "Experience Level": "Mid-Level",
        "Application Deadline": "2025-03-01"
    }
    # Create temporary paths for the folder, doc, and pdf.
    folder = tmp_path / "cover_letters" / "TestCompany_TestJob_20250101_123456"
    folder.mkdir(parents=True, exist_ok=True)
    doc_path = folder / "cover_letter.docx"
    pdf_path = folder / "cover_letter.pdf"

    # Call the function.
    notion_client.update_notion_database("page123", job_details, str(folder), str(doc_path), str(pdf_path))
    # Retrieve the update call stored in our fake client.
    update_call = fake_notion_client.pages.last_update
    assert update_call["page_id"] == "page123"
    properties = update_call["properties"]
    # Check that the Company and Location are set correctly.
    assert properties["Company"]["rich_text"][0]["text"]["content"] == job_details["Company"]
    assert properties["Location"]["rich_text"][0]["text"]["content"] == job_details["Location"]

    # Verify that the file URIs are valid (we at least check the scheme is "file").
    from urllib.parse import urlparse
    folder_uri = properties["Cover Letter Directory"]["url"]
    parsed = urlparse(folder_uri)
    assert parsed.scheme in ("file",)

def test_update_notion_database_invalid_date(monkeypatch, fake_notion_client, tmp_path, capsys):
    """
    When the Application Deadline is invalid, it should be omitted and a warning printed.
    """
    job_details = {
        "Company": "Test Company",
        "Location": "Test Location",
        "Job URL": "http://example.com",
        "Salary Range": "$100k",
        "Experience Level": "Mid-Level",
        "Application Deadline": "invalid-date"
    }
    folder = tmp_path / "cover_letters" / "TestCompany_TestJob_20250101_123456"
    folder.mkdir(parents=True, exist_ok=True)
    doc_path = folder / "cover_letter.docx"
    pdf_path = folder / "cover_letter.pdf"

    notion_client.update_notion_database("page123", job_details, str(folder), str(doc_path), str(pdf_path))
    update_call = fake_notion_client.pages.last_update
    properties = update_call["properties"]
    # "Application Deadline" should not be present because date parsing failed.
    assert "Application Deadline" not in properties
    captured = capsys.readouterr().out
    assert "Warning: Could not parse Application Deadline as date" in captured

def test_update_notion_database_api_error(monkeypatch, fake_notion_client, tmp_path):
    """
    Simulate an APIResponseError when updating the Notion page.
    """
    class FakeAPIError(APIResponseError):
        def __init__(self):
            self.code = "error_code"
            self.message = "error message"
            self.status = 400

    def fake_update(*args, **kwargs):
        raise FakeAPIError()

    monkeypatch.setattr(fake_notion_client.pages, "update", fake_update)
    job_details = {
        "Company": "Test Company",
        "Location": "Test Location",
        "Job URL": "http://example.com",
        "Salary Range": "$100k",
        "Experience Level": "Mid-Level",
        "Application Deadline": "2025-03-01"
    }
    folder = tmp_path / "cover_letters" / "TestCompany_TestJob_20250101_123456"
    folder.mkdir(parents=True, exist_ok=True)
    doc_path = folder / "cover_letter.docx"
    pdf_path = folder / "cover_letter.pdf"

    with pytest.raises(FakeAPIError):
        notion_client.update_notion_database("page123", job_details, str(folder), str(doc_path), str(pdf_path))

# ------------------
# Tests for is_page_archived
# ------------------

def test_is_page_archived_returns_false(fake_notion_client, monkeypatch):
    """
    When notion_client.pages.retrieve returns a page with archived False, is_page_archived should return False.
    """
    def fake_retrieve(page_id):
        return {"archived": False}
    monkeypatch.setattr(fake_notion_client.pages, "retrieve", fake_retrieve)
    result = notion_client.is_page_archived("page123")
    assert result is False

def test_is_page_archived_not_found(monkeypatch, fake_notion_client):
    """
    If notion_client.pages.retrieve raises an APIResponseError with status 404,
    is_page_archived should raise an Exception with an appropriate message.
    """
    class FakeAPIError(APIResponseError):
        def __init__(self):
            self.status = 404
    def fake_retrieve(page_id):
        raise FakeAPIError()
    monkeypatch.setattr(fake_notion_client.pages, "retrieve", fake_retrieve)
    with pytest.raises(Exception, match="Page with ID page123 not found"):
        notion_client.is_page_archived("page123")

# ------------------
# Tests for unarchive_page
# ------------------

def test_unarchive_page_success(fake_notion_client):
    """
    unarchive_page should call notion_client.pages.update with archived=False.
    """
    # Reset any previous update call.
    fake_notion_client.pages.last_update = None
    notion_client.unarchive_page("page123")
    update_call = fake_notion_client.pages.last_update
    assert update_call is not None
    assert update_call["archived"] is False

def test_unarchive_page_permission_error(monkeypatch, fake_notion_client):
    """
    If updating the page raises an APIResponseError with a permission error, unarchive_page should raise an Exception.
    """
    class FakeAPIError(APIResponseError):
        def __init__(self):
            self.code = "permission_error"
    def fake_update(*args, **kwargs):
        raise FakeAPIError()
    monkeypatch.setattr(fake_notion_client.pages, "update", fake_update)
    with pytest.raises(Exception, match="You don't have permission to unarchive page"):
        notion_client.unarchive_page("page123")
