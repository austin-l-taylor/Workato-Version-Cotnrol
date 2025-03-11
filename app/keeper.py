import base64
import os
from base64 import b64decode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from keeper_secrets_manager_core import SecretsManager
class Keeper:
    client = None

    @classmethod
    def decrypt_data(cls, data, encryption_key):
        key = b64decode(encryption_key)
        iv = (
            b"\x00" * 16
        )  # 16 bytes for AES block size, set to zeros to match the C# example
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(data) + decryptor.finalize()

        # Read padding length and remove padding
        padding_length = decrypted_data[-1]
        return decrypted_data[:-padding_length]

    # Using token only to generate the config
    # requires at least one access operation to bind the token

    @classmethod
    def authorize(cls):
        # Retrieve the encryption key from the environment variable
        encryption_key = os.environ.get("KEEPER_ENCRYPTION_KEY")

        # Read the encrypted file path from the environment variable
        encrypted_file_path = os.environ.get("KEEPER_CONFIG_FILE_PATH")

        if not encryption_key or not encrypted_file_path:
            raise Exception(
                "Unable to locate Keeper configuration file! Have you configured this user for Keeper Secrets Manager?"
            )

        # Read the encrypted configuration file
        with open(encrypted_file_path, "rb") as file:
            encrypted_data = file.read()

        # Decrypt the data
        try:
            decrypted_data = cls.decrypt_data(encrypted_data, encryption_key)
        except Exception as e:
            raise Exception(
                f"Unable to decrypt configuration file! Installation may be corrupt. Please re-configure this user for Keeper Secrets Manager. {str(e)}"
            )

        os.environ["KSM_CONFIG"] = base64.b64encode(decrypted_data).decode()

        # When no arguments are provided, the KSM_CONFIG environment variable is used
        cls.client = SecretsManager()