from dataclasses import dataclass
import io
import requests

from domain.errors import ATError
from infrastructure.graph_config import BASE_FOLDER


@dataclass
class GraphContext:
    access_token: str
    site_id: str
    drive_id: str


def list_input_files_graph(
    context: GraphContext,
    folder_path: str,
) -> list[dict]:

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{context.site_id}"
        f"/drives/{context.drive_id}"
        f"/root:/{folder_path}:/children"
    )

    headers = {
        "Authorization": (
            f"Bearer {context.access_token}"
        )
    }

    response = requests.get(
        url,
        headers=headers,
    )

    if response.status_code != 200:
        raise ATError(
            "ERR021",
            f"Could not list files in "
            f"{folder_path}: {response.text}",
        )

    items = response.json()["value"]

    return [
        item
        for item in items
        if item["name"].endswith(".xlsx")
    ]


def download_file_graph(
    context: GraphContext,
    item_id: str,
) -> io.BytesIO:

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{context.site_id}"
        f"/drives/{context.drive_id}"
        f"/items/{item_id}/content"
    )

    headers = {
        "Authorization": (
            f"Bearer {context.access_token}"
        )
    }

    response = requests.get(
        url,
        headers=headers,
    )

    if response.status_code != 200:
        raise ATError(
            "ERR022",
            f"Could not download file "
            f"{item_id}: {response.text}",
        )

    return io.BytesIO(response.content)


def upload_file_graph(
    context: GraphContext,
    folder_path: str,
    file_name: str,
    file_bytes: bytes,
) -> None:

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{context.site_id}"
        f"/drives/{context.drive_id}"
        f"/root:/{folder_path}/{file_name}:/content"
    )

    headers = {
        "Authorization": (
            f"Bearer {context.access_token}"
        )
    }

    response = requests.put(
        url,
        headers=headers,
        data=file_bytes,
    )

    if response.status_code not in (200, 201):
        raise ATError(
            "ERR023",
            f"Could not upload file "
            f"{file_name}: {response.text}",
        )


def get_file_by_path(
    context: GraphContext,
    file_path: str,
) -> io.BytesIO | None:

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{context.site_id}"
        f"/drives/{context.drive_id}"
        f"/root:/{file_path}:/content"
    )

    headers = {
        "Authorization": (
            f"Bearer {context.access_token}"
        )
    }

    response = requests.get(
        url,
        headers=headers,
    )

    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise ATError(
            "ERR022",
            f"Could not download file "
            f"{file_path}: {response.text}",
        )

    return io.BytesIO(response.content)


def build_output_path(
    year: int,
    month: int,
) -> tuple[str, str]:

    folder = (
        f"{BASE_FOLDER}/Output/"
        f"{year}/{month:02d}"
    )

    file_name = (
        f"AT_Metrics_"
        f"{year}-{month:02d}.xlsx"
    )

    return folder, file_name


def build_next_month_output_path(
    year: int,
    month: int,
) -> tuple[str, str]:

    next_year = year
    next_month = month + 1

    if next_month == 13:
        next_month = 1
        next_year += 1

    folder = (
        f"{BASE_FOLDER}/Output/"
        f"{next_year}/{next_month:02d}"
    )

    file_name = (
        f"AT_Metrics_"
        f"{next_year}-{next_month:02d}.xlsx"
    )

    return folder, file_name


def get_site_id(access_token: str) -> str:
    site_hostname = "employersolution.sharepoint.com"
    site_path = "/sites/VMC-RPA"

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{site_hostname}:{site_path}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        url,
        headers=headers,
    )

    if response.status_code != 200:
        raise ATError(
            "ERR024",
            f"Could not get site_id: "
            f"{response.text}",
        )

    return response.json()["id"]


def get_drive_id(
    access_token: str,
    site_id: str,
) -> str:

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{site_id}/drives"
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        url,
        headers=headers,
    )

    if response.status_code != 200:
        raise ATError(
            "ERR024",
            f"Could not get drive_id: "
            f"{response.text}",
        )

    drives = response.json().get(
        "value",
        [],
    )

    for drive in drives:
        if drive["name"] == "Shared Documents":
            return drive["id"]

    raise ATError(
        "ERR024",
        "Shared Documents drive not found",
    )