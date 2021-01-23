from app.base import SourceInterface


class Dropbox(SourceInterface):

    def get_source_folder(self, path: str, file_name: str):
        """Upload file to the source"""
        raise NotImplementedError

    def get_source_files(self, full_file_path: str):
        """Download file from the source"""
        raise NotImplementedError

    def upload_file(self, full_file_path: str):
        """Download file from the source"""
        raise NotImplementedError

    def download_file(self, full_file_path: str):
        """Download file from the source"""
        raise NotImplementedError
