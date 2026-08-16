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

    headers = {"Authorization": f"Bearer {context.access_token}"
               }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ATError("ERR021", f"Could not list files in {folder_path}: {response.text}")

    items = response.json()["value"]

    excel_files = [item for item in items if item["name"].endswith(".xlsx")]

    return excel_files

def download_file_graph(context: GraphContext, item_id: str) -> io.BytesIO:

    url = ( f"https://graph.microsoft.com/v1.0/sites/{context.site_id}"
            f"/drives/{context.drive_id}/items/{item_id}/content")

    headers = {"Authorization": f"Bearer {context.access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ATError  ("ERR022", f"Could not download file {item_id}: {response.text}")

    return io.BytesIO(response.content)

def upload_file_graph(context: GraphContext, folder_path: str, file_name: str, file_bytes: bytes) -> None:
    url = ( f"https://graph.microsoft.com/v1.0/sites/{context.site_id}" 
           f"/drives/{context.drive_id}/root:/{folder_path}/{file_name}:/content")

    headers = {"Authorization": f"Bearer {context.access_token}"}

    response = requests.put(url, headers=headers, data = file_bytes)

    if response.status_code not in (200,2001):
        raise ATError("ERR023", f"Could not upload file {file_name}: {response.text}")
    

def get_file_by_path(context: GraphContext, file_path: str) -> io.BytesIO | None:
    url = ( f"https://graph.microsoft.com/v1.0/sites/{context.site_id}"
           f"/drives/{context.drive_id}/root:/{file_path}:/content")

    headers = {"Authorization": f"Bearer {context.access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise ATError ("ERR022", f"Could not dowloand file {file_path}: {response.text}")

    return io.BytesIO(response.content)