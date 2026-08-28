from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential

from infrastructure.graph_config import (
    VAULT_TENANT_ID,
    VAULT_CLIENT_ID,
    VAULT_URL,
    GraphCredentials,
    SHAREP_SECRET_NAMES,
)


def get_key_vault_session(vault_client_secret: str) -> SecretClient:
    credential = ClientSecretCredential(
        VAULT_TENANT_ID, VAULT_CLIENT_ID, vault_client_secret
    )
    session = SecretClient(vault_url=VAULT_URL, credential=credential)
    
    return session


def get_sharepoint_credentials(session: SecretClient) -> GraphCredentials:
    tenant_id = session.get_secret(SHAREP_SECRET_NAMES["tenant_id"]).value
    client_id = session.get_secret(SHAREP_SECRET_NAMES["client_id"]).value
    client_secret = session.get_secret(SHAREP_SECRET_NAMES["client_secret"]).value

    return GraphCredentials(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )