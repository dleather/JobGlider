import pytest
from unittest.mock import patch, MagicMock

from src.core.job_parser import (
    extract_job_details,
    fetch_job_posting_text,
    answer_question,
    clean_job_details,
)

@patch("src.core.job_parser.requests.get")
@patch("src.core.job_parser.openai_client.chat.completions.create")
def test_extract_job_details(mock_openai_call, mock_requests_get, mock_html_content, mock_openai_response):
    """
    Unit test: Mocks out requests and OpenAI calls.
    Ensures `extract_job_details` handles the logic of extracting fields.
    """
    # Mock the requests.get() to return a response with our mock_html_content
    mock_response = MagicMock()
    mock_response.content = mock_html_content.encode("utf-8")
    mock_requests_get.return_value = mock_response

    # Mock the OpenAI call to return a specific structured text
    text_returned_by_openai = (
        "Job Title: Senior Developer\n"
        "Company: ACME Corp\n"
        "Location: Some City\n"
        "Experience Level: Mid-Level\n"
        "Application Deadline: \n"
        "Salary Range: Not specified"
    )
    mock_openai_call.return_value = mock_openai_response(text_returned_by_openai)

    # Call the function under test
    result = extract_job_details("https://fakejob.url")

    # Assertions on the returned dictionary
    assert "Job Title" in result
    assert result["Job Title"] == "Senior Developer"
    assert result["Company"] == "ACME Corp"
    assert result["Location"] == "Some City"
    assert result["Experience Level"] == "Mid-Level"
    # etc.


@patch("src.core.job_parser.requests.get")
def test_fetch_job_posting_text(mock_requests_get, mock_html_content):
    """
    Unit test for fetch_job_posting_text, mocking out the network call.
    """
    mock_response = MagicMock()
    mock_response.content = mock_html_content.encode("utf-8")
    mock_requests_get.return_value = mock_response

    text = fetch_job_posting_text("https://fakejob.url")
    assert "Senior Developer" in text
    assert "Some City" in text
    # and so on


@patch("src.core.job_parser.model")
@patch("src.core.job_parser.tokenizer")
def test_answer_question(mock_tokenizer, mock_model, mock_model_output):
    """
    Unit test: Mocks the local huggingface model and tokenizer so that
    we don't load actual large models in memory.
    """
    # Setup tokenizer and model mocks
    # 1) The tokenizer(...) call
    mock_tokenizer.return_value = {"input_ids": [[101, 102, 103]], "something": "dummy"}
    # Ensure tokenizer.decode returns a string
    mock_tokenizer.decode.return_value = "Developer"
    
    # 2) The model(...) call
    mock_model.__enter__ = MagicMock(return_value=mock_model)
    mock_model.__exit__ = MagicMock()
    mock_model.return_value = mock_model_output

    # Actually call the function
    result = answer_question("What is the role?", "The role is a developer job posting.")

    # Assertions
    assert "answer" in result
    assert "confidence" in result
    assert isinstance(result["answer"], str)
    assert isinstance(result["confidence"], float)


def test_clean_job_details():
    """
    Simple unit test for clean_job_details with a local dictionary.
    """
    raw_details = {
        "- **Job Title:**": "  Senior Developer  ",
        "Job URL": "https://example.com",
        "- **Company:**": "  ACME  "
    }
    cleaned = clean_job_details(raw_details)
    # We expect 'Job Title' => 'Senior Developer', 'Company' => 'ACME'
    assert "Job Title" in cleaned
    assert cleaned["Job Title"] == "Senior Developer"
    assert cleaned["Company"] == "ACME"
    assert cleaned["Job URL"] == "https://example.com"
