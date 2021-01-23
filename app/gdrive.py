import io

from app.base import SourceInterface
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from app.constants import FOLDER_MIMETYPE


class GoogleDrive(SourceInterface):

    def __init__(self, client):
        self.cli = client

    def get_source_folder(self, name):
        page_token = None
        drive_folders = self.cli.files().list(
            q=f"mimeType = '{FOLDER_MIMETYPE}' and name = '{name}' and trashed = False",
            spaces='drive',
            pageToken=page_token
        ).execute()

        if not drive_folders:
            return None
        return drive_folders['files'][0]

    def get_source_files(self, folder_id):
        page_token = None
        drive_files = self.cli.files().list(
            q=f"'{folder_id}' in parents and trashed = False",
            spaces='drive',
            pageToken=page_token
        ).execute()

        return drive_files['files']

    def upload_file(self, file, folder):
        file_metadata = {
            'name': file.name,
            'parents': [folder['id']]
        }
        media = MediaFileUpload(
            file,
            mimetype='image/jpeg',
        )
        print(f"I'm greenlet for the {file}")
        self.cli.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
        ).execute()

        print(f"Downloaded for the {file}")

    def download_file(self, file, local_folder):
        request = self.cli.files().get_media(fileId=file['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        print(f"I'm greenlet for the {file['name']}")
        while done is False:
            status, done = downloader.next_chunk()
            print
            "Download %d%%." % int(status.progress() * 100)

        with open(f"{local_folder}/{file['name']}", "wb") as f:
            f.write(fh.getbuffer())
        print(f"Downloaded for the {file['name']}")