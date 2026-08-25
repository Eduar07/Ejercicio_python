from dataclasses import dataclass


@dataclass
class GraphCredentials:
    tenant_id: str
    client_id: str
    client_secret: str
    site_id: str = ""
    drive_id: str = ""
    
BASE_FOLDER = "Development/IT/AT_Internal_Metrics"

VAULT_TENANT_ID = "2e8802e0-0b68-49d0-857f-46e74756f974"   
VAULT_CLIENT_ID = "3d9eae87-c30c-4137-8c28-4c8c6c080fe0"  
VAULT_URL = "https://akv-rpa-automation.vault.azure.net/"

SHAREP_SECRET_NAMES = {
    "client_id": "prod-servicep-sharep-clientid",
    "client_secret": "prod-servicep-sharep-clientsecret",
    "tenant_id": "prod-servicep-sharep-tenantid",
}