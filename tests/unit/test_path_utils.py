from pathlib import Path
from src.utils.path_utils import docker_to_local_path

def test_docker_to_local_path_standard():
    """
    When docker_path starts with base_docker_path, the function should
    return the local path with the relative part appended.
    """
    docker_path = "/app/data/file.txt"
    base_docker_path = "/app"
    base_local_path = "/local"
    expected = Path("/local/data/file.txt")
    result = docker_to_local_path(docker_path, base_docker_path, base_local_path)
    assert result == expected

def test_docker_to_local_path_non_matching():
    """
    When docker_path does not start with base_docker_path, the function
    should fallback to using the full docker_path.
    """
    docker_path = "/other/data/file.txt"
    base_docker_path = "/app"
    base_local_path = "/local"
    expected = Path("/other/data/file.txt")
    result = docker_to_local_path(docker_path, base_docker_path, base_local_path)
    assert result == expected

def test_docker_to_local_path_relative_paths():
    """
    When using relative paths for docker_path and base_docker_path,
    the relative part should be correctly appended to base_local_path.
    """
    docker_path = "app/data/file.txt"
    base_docker_path = "app"
    base_local_path = "local"
    expected = Path("local/data/file.txt")
    result = docker_to_local_path(docker_path, base_docker_path, base_local_path)
    assert result == expected

def test_docker_to_local_path_trailing_slashes():
    """
    Trailing slashes in base paths should not affect the outcome.
    """
    docker_path = "/app/data/file.txt"
    base_docker_path = "/app/"
    base_local_path = "/local/"
    expected = Path("/local/data/file.txt")
    result = docker_to_local_path(docker_path, base_docker_path, base_local_path)
    assert result == expected

def test_docker_to_local_path_with_fixture(temp_paths):
    """
    Using the temp_paths fixture from conftest.py, ensure that a docker_path
    is converted to the expected local path.
    """
    # temp_paths fixture provides:
    #   "docker_path": "/app/some_folder/file.txt"
    #   "local_path": "C:/Users/davle/Dropbox (Personal)/some_folder/file.txt"
    docker_path = temp_paths["docker_path"]
    expected_local = Path(temp_paths["local_path"])
    
    # We assume the base_docker_path is "/app" and base_local_path is the
    # local part up to "Dropbox (Personal)".
    base_docker_path = "/app"
    base_local_path = "C:/Users/davle/Dropbox (Personal)"
    
    result = docker_to_local_path(docker_path, base_docker_path, base_local_path)
    assert result == expected_local
