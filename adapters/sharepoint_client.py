from dataclasses import dataclass
import requests
import io
from domain.errors import ATError


@dataclass
class GraphContext:
    access_token: str
    site_id: str
    drive_id: str


def list_input_files_graph(context: GraphContext, folder_path: str) -> list[dict]:

    url = (
        f"https://graph.microsoft.com/v1.0/sites/{context.site_id}"
        f"/drives/{context.drive_id}/root:/{folder_path}:/children"
    )

    headers = {"Authorization": f"Bearer {context.access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ATError("ERR021", f"Could not list files in {folder_path}: {response.text}")

    items = response.json()["value"]

    excel_files = [item for item in items if item["name"].endswith(".xlsx")]

    return excel_files


def download_file_graph(context: GraphContext, item_id: str) -> io.BytesIO:

    url = (
        f"https://graph.microsoft.com/v1.0/sites/{context.site_id}"
        f"/drives/{context.drive_id}/items/{item_id}/content"
    )

    headers = {"Authorization": f"Bearer {context.access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ATError("ERR022", f"Could not download file {item_id}: {response.text}")

    return io.BytesIO(response.content)


def upload_file_graph(context: GraphContext, folder_path: str, file_name: str, file_bytes: bytes) -> None:
    url = (
        f"https://graph.microsoft.com/v1.0/sites/{context.site_id}"
        f"/drives/{context.drive_id}/root:/{folder_path}/{file_name}:/content"
    )

    headers = {"Authorization": f"Bearer {context.access_token}"}

    response = requests.put(url, headers=headers, data=file_bytes)

    if response.status_code not in (200, 201):
        raise ATError("ERR023", f"Could not upload file {file_name}: {response.text}")


def get_file_by_path(context: GraphContext, file_path: str) -> io.BytesIO | None:
    url = (
        f"https://graph.microsoft.com/v1.0/sites/{context.site_id}"
        f"/drives/{context.drive_id}/root:/{file_path}:/content"
    )

    headers = {"Authorization": f"Bearer {context.access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise ATError("ERR022", f"Could not download file {file_path}: {response.text}")

    return io.BytesIO(response.content)


def build_output_path(year: int, month: int) -> tuple[str, str]:
    folder = f"AT_Internal_Metrics/Output/{year}/{month:02d}"
    file_name = f"AT_Metrics_{year}-{month:02d}.xlsx"
    return folder, file_name


def build_next_month_output_path(year: int, month: int) -> tuple[str, str]:
    next_year = year
    next_month = month + 1

    if next_month == 13:
        next_month = 1
        next_year += 1

    folder = f"AT_Internal_Metrics/Output/{next_year}/{next_month:02d}"
    file_name = f"AT_Metrics_{next_year}-{next_month:02d}.xlsx"
    return folder, file_name


def get_site_id(access_token: str) -> str:
    site_hostname = "employersolution.sharepoint.com"
    site_path = "/sites/VMC-RPA"

    url = f"https://graph.microsoft.com/v1.0/sites/{site_hostname}:{site_path}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ATError("ERR024", f"Could not get site_id: {response.text}")

    return response.json()["id"]


def get_drive_id(access_token: str, site_id: str) -> str:
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ATError("ERR024", f"Could not get drive_id: {response.text}")

    drives = response.json().get("value", [])

    if not drives:
        raise ATError("ERR024", "No drives found for the site")

    return drives[0]["id"]