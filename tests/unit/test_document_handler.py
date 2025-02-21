# tests/unit/test_document_handler.py

from src.core.document_handler import is_one_page_pdf

def test_is_one_page_pdf_true(one_page_pdf_fixture):
    """
    Unit test: is_one_page_pdf should return True for a single-page PDF.
    """
    assert is_one_page_pdf(one_page_pdf_fixture) is True

def test_is_one_page_pdf_false(two_page_pdf_fixture):
    """
    Unit test: is_one_page_pdf should return False for multiple-page PDF.
    """
    assert is_one_page_pdf(two_page_pdf_fixture) is False
