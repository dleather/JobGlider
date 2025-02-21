import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.utils.notion_utils import (
    docker_to_local_path, 
    update_notion_database, 
    is_page_archived, 
    unarchive_page
)

# ---------------- Fixtures ---------------- #
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