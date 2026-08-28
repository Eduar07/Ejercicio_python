'''
Configuración de SharePoint / Microsoft Graph y del Azure Key Vault
donde se guardan las credenciales de la app registrada.
'''
from dataclasses import dataclass


# ============================================================
# Credenciales de la app registrada en Entra ID (Azure AD) usada
# para autenticar contra Microsoft Graph.
# Se completan en runtime desde Key Vault — ver adapters/key_vault_auth.py.
# ============================================================

@dataclass
class GraphCredentials:
    tenant_id: str
    client_id: str
    client_secret: str
    site_id: str = ""
    drive_id: str = ""


# ============================================================
# SharePoint: sitio y carpeta base donde vive todo el flujo
# (Input/, Input/Processed/, Output/, Parametric Files/).
# Usado por adapters/sharepoint_client.py y los adapters que arman
# rutas (sharepoint_raw_input_adapter, sharepoint_metrics_output_adapter,
# sharepoint_log_adapter).
# ============================================================

BASE_FOLDER = "Development/IT/AT_Internal_Metrics"


# ============================================================
# Azure Key Vault: de acá se obtienen las credenciales reales de
# SharePoint (tenant/client id/secret) en cada ejecución.
# Usado por adapters/key_vault_auth.py.
# ============================================================

VAULT_TENANT_ID = "2e8802e0-0b68-49d0-857f-46e74756f974"
VAULT_CLIENT_ID = "3d9eae87-c30c-4137-8c28-4c8c6c080fe0"
VAULT_URL = "https://akv-rpa-automation.vault.azure.net/"

# Nombres de los secretos dentro del vault (no los valores).
SHAREP_SECRET_NAMES = {
    "client_id": "prod-servicep-sharep-clientid",
    "client_secret": "prod-servicep-sharep-clientsecret",
    "tenant_id": "prod-servicep-sharep-tenantid",
}
