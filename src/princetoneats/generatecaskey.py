import os
import secrets
from pathlib import Path


def generate_secret_key():
    """Generate a secure random secret key."""
    return secrets.token_hex(32)  # 64 character hex string


def save_to_env_file(key, env_file=".env"):
    """Save the secret key to a .env file.

    If the file exists, it will look for APP_SECRET_KEY and update it,
    otherwise it will append the key to the file.
    If the file doesn't exist, it will create it.
    """
    env_path = Path(env_file)
    key_found = False

    if env_path.exists():
        # Read the existing file
        with open(env_path, "r") as file:
            lines = file.readlines()

        # Look for existing APP_SECRET_KEY and update it
        with open(env_path, "w") as file:
            for line in lines:
                if line.startswith("APP_SECRET_KEY="):
                    file.write(f'APP_SECRET_KEY="{key}"\n')
                    key_found = True
                else:
                    file.write(line)

            # If the key wasn't found, append it
            if not key_found:
                file.write(f'\nAPP_SECRET_KEY="{key}"\n')

        print(f"Updated APP_SECRET_KEY in {env_file}")
    else:
        # Create a new .env file
        with open(env_path, "w") as file:
            file.write(f'APP_SECRET_KEY="{key}"\n')
        print(f"Created new {env_file} file with APP_SECRET_KEY")

    # Set file permissions to be readable only by the owner
    os.chmod(env_path, 0o600)
    print(f"Set {env_file} permissions to be readable only by you")


def main():
    # Generate a new secret key
    secret_key = generate_secret_key()

    # Save it to the .env file
    save_to_env_file(secret_key)

    print(f"\nGenerated new APP_SECRET_KEY: {secret_key}")
    print("This key has been saved to your .env file.")


if __name__ == "__main__":
    main()
