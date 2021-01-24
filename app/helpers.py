from pathlib import Path


def get_folder(folder):
    p = Path(folder)
    if not p.is_dir() and not p.exists():
        return False
    return p


def get_root_path(filename):
    return Path.joinpath(Path(__name__).parent, filename)


def create_root_file(filename):
    return Path.joinpath(Path(__name__), filename).touch()

