import abc


class SourceInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_source_folder(self, path: str, file_name: str):
        """Upload file to the source"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_source_files(self, full_file_path: str):
        """Download file from the source"""
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, full_file_path: str):
        """Download file from the source"""
        raise NotImplementedError

    @abc.abstractmethod
    def download_file(self, full_file_path: str):
        """Download file from the source"""
        raise NotImplementedError
