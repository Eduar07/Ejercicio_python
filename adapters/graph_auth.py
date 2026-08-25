import msal

from domain.errors import ATError


def get_access_token(
    tenant_id: str,
    client_id: str,
    client_secret: str,
) -> str:

    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=(
            f"https://login.microsoftonline.com/"
            f"{tenant_id}"
        ),
    )

    result = app.acquire_token_for_client(
        scopes=[
            "https://graph.microsoft.com/.default"
        ]
    )

    if "access_token" not in result:
        raise ATError(
            "ERR020",
            "Could not authenticate with Graph: "
            f"{result.get('error_description')}",
        )

    return result["access_token"]