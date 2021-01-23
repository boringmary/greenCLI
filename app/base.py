import abc


class SourceInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_source_folder(self, name):
        """Get provider folder"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_source_files(self, folder_id):
        """Fet all files from provider folder"""
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, file, source_folder):
        """Upload file to the provider"""
        raise NotImplementedError

    @abc.abstractmethod
    def download_file(self, file, local_folder):
        """Download file from the provider"""
        raise NotImplementedError
