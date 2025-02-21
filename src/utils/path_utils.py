from pathlib import Path
from src.utils.config import BASE_DOCKER_PATH, BASE_LOCAL_PATH  

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