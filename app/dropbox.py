from pprint import pprint

import dropbox

from app.base import SourceInterface


class DropboxProvider(SourceInterface):

    prefix = "/Dropbox"

    def __init__(self, client):
        self.cli = client

    def get_source_folder(self, name):
        """Upload file to the source"""
        return {"name": name, "id": name}

    def get_source_files(self, source_folder):
        """Download file from the source"""
        path = f"{self.prefix}/{source_folder}"
        return self.cli.files_list_folder(path).entries

    def upload_file(self, file, source_folder):
        """Download file from the source"""
        with open(file, "rb") as f:
            data = f.read()
        self.cli.files_upload(
            data,
            f"{self.prefix}/{source_folder}/{file.name}",
            mode=dropbox.files.WriteMode.overwrite
        )

    def download_file(self, file, local_folder):
        """Download file from the source"""
        self.cli.files_download_to_file(f'{str(local_folder)}/{file.name}', file.path_lower)
