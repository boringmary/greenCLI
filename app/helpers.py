from pathlib import Path


def get_folder(folder):
    p = Path(folder)
    if not p.is_dir() and not p.exists():
        return False
    return p
