import os
import requests
from msal import ConfidentialClientApplication


CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
TENANT_ID = os.getenv("AZURE_TENANT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]


def obtener_token():

    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

    resultado = app.acquire_token_for_client(
        scopes=SCOPE
    )

    return resultado


def probar_conexion():

    token = obtener_token()

    if "access_token" not in token:
        return {
            "ok": False,
            "error": token
        }

    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }
    url = (
    "https://graph.microsoft.com/v1.0/"
    "sites/sedapalcompe.sharepoint.com:/sites/RECLAMOSECCA2022"
    )

    respuesta = requests.get(
        url,
        headers=headers
    )

    return {
        "ok": respuesta.ok,
        "status_code": respuesta.status_code,
        "respuesta": (
            respuesta.json()
            if "application/json" in respuesta.headers.get("Content-Type", "")
            else respuesta.text
        )
    }
