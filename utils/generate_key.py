import base64
import os

# Genera 32 bytes aleatorios y codifícalos en base64
key_bytes = os.urandom(32)
key = base64.urlsafe_b64encode(key_bytes).decode()
print("Clave generada:", key)  # Guarda este valor