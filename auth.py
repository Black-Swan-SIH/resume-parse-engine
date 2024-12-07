import yaml
from fastapi import HTTPException, status


def load_valid_api_keys(file_path: str = "api_keys.yaml"):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)["api_keys"]
    except Exception as e:
        raise RuntimeError(f"Error loading API keys YAML: {e}")


def validate_api_key(api_key: str):
    valid_api_keys = load_valid_api_keys()
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
