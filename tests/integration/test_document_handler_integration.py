# tests/integration/test_document_handler_integration.py

import os
import pytest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.document_handler import save_cover_letter_documents

def test_save_cover_letter_documents_happy_path(job_details_fixture,
                                                cover_letter_text_fixture,
                                                temp_output_dir):
    """
    Integration test for save_cover_letter_documents.
    Ensures that Word, TeX, and PDF files get created in the correct location
    and that a job_details.txt file is saved.
    """
    # Patch the COVER_LETTERS_DIR so our function writes into our temp_output_dir
    with patch("src.core.document_handler.COVER_LETTERS_DIR", temp_output_dir), \
         patch("jinja2.Environment.get_template") as mock_get_template:
        
        # Mock the template loading
        mock_template = MagicMock()
        mock_template.render.return_value = "\\documentclass{article}\n\\begin{document}\nTest Content\n\\end{document}"
        mock_get_template.return_value = mock_template

        folder_path, doc_path, pdf_path = save_cover_letter_documents(
            job_details_fixture,
            cover_letter_text_fixture
        )

        # Verify the files were created
        assert os.path.exists(folder_path)
        assert os.path.exists(doc_path)
        assert os.path.exists(os.path.join(folder_path, "job_details.txt"))
        assert os.path.exists(os.path.join(folder_path, "cover_letter.tex"))

def test_save_cover_letter_documents_latex_failure(job_details_fixture,
                                                   cover_letter_text_fixture,
                                                   temp_output_dir):
    """
    Test behavior when LaTeX fails (e.g., xelatex not found or compilation error).
    We mock the subprocess.run to force an error.
    """
    with patch("subprocess.run") as mock_run, \
         patch("src.core.document_handler.COVER_LETTERS_DIR", temp_output_dir), \
         patch("jinja2.Environment.get_template") as mock_get_template:
        
        # Mock the template loading
        mock_template = MagicMock()
        mock_template.render.return_value = "Mocked LaTeX content"
        mock_get_template.return_value = mock_template
        
        # Configure the mock to raise CalledProcessError
        mock_run.side_effect = Exception("LaTeX compilation error")

        with pytest.raises(Exception, match="LaTeX compilation error"):
            save_cover_letter_documents(job_details_fixture, cover_letter_text_fixture)