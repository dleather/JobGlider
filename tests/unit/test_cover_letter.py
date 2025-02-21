import json
from datetime import datetime
import pytest

# Import the module under test.
from src.core import cover_letter
from tests.fake_openai import FakeResponse


def test_generate_cover_letter_returns_expected_text(monkeypatch, dummy_job_details):
    """
    Test that generate_cover_letter returns the cover letter text
    up to (but not including) any extraneous formatting markers.
    """
    # Create a fake response with our expected content
    def fake_create(*args, **kwargs):
        return FakeResponse("This is the generated cover letter content.")
    
    # Set up the OpenAI client with our fake response
    monkeypatch.setattr(cover_letter, "openai_client", type("FakeClient", (), {
        "chat": type("FakeChat", (), {
            "completions": type("FakeCompletions", (), {
                "create": fake_create
            })()
        })()
    })())
    
    result = cover_letter.generate_cover_letter(dummy_job_details)
    expected = "This is the generated cover letter content."
    assert result == expected

def test_generate_cover_letter_includes_job_details(monkeypatch, dummy_job_details):
    """
    Test that the prompt constructed inside generate_cover_letter includes
    values from the provided job_details. We capture the prompt passed to the fake_create.
    """
    captured_prompt = {}
    
    def fake_create_capture(*args, **kwargs):
        # Extract the 'user' message from the second message
        messages = kwargs.get("messages", [])
        for msg in messages:
            if msg.get("role") == "user":
                captured_prompt["prompt"] = msg.get("content")
        return FakeResponse("Test cover letter output")
    
    # Set up the OpenAI client with our capturing fake
    monkeypatch.setattr(cover_letter, "openai_client", type("FakeClient", (), {
        "chat": type("FakeChat", (), {
            "completions": type("FakeCompletions", (), {
                "create": fake_create_capture
            })()
        })()
    })())
    
    result = cover_letter.generate_cover_letter(dummy_job_details)
    prompt = captured_prompt.get("prompt", "")
    
    # Verify that the prompt includes key details
    assert dummy_job_details["Job Title"] in prompt
    assert dummy_job_details["Company"] in prompt
    assert dummy_job_details["Location"] in prompt
    assert dummy_job_details["Experience Level"] in prompt
    assert dummy_job_details["Application Deadline"] in prompt
    assert dummy_job_details["Salary Range"] in prompt
    
    # Also check that the function returns the simulated response output
    assert result == "Test cover letter output"
