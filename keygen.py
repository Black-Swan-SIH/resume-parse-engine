import yaml
import secrets

def generate_api_keys(num_keys: int, key_length: int = 32, file_path: str = "api_keys.yaml"):
    """
    Generate a YAML file with secure API keys.

    Args:
        num_keys (int): Number of API keys to generate.
        key_length (int): Length of each API key.
        file_path (str): Path to save the generated YAML file.
    """
    keys = [secrets.token_hex(key_length // 2) for _ in range(num_keys)]
    data = {"api_keys": keys}

    with open(file_path, "w") as file:
        yaml.dump(data, file)

    print(f"API keys generated and saved to {file_path}")

# Generate 5 API keys of length 32 bytes
generate_api_keys(num_keys=5)
