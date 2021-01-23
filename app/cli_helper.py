import click

from app.cli import pass_provider
from app.helpers import get_folder
from app.upload_pipeline import upload_dir
from app.download_pipeline import download_dir


def upload_handler(drive):
    msg = f"Local folder to upload (full path) \n"
    value = click.prompt(msg, type=str)
    frm = get_folder(value)
    if not frm:
        click.echo("Please specify existing folder", err=True)
        return upload_handler(drive)

    msg = f"Google Drive folder to move files into \n"
    to = click.prompt(msg, type=str)

    upload_dir(drive, frm, to)


def download_handler(drive):
    msg = f"Google Drive folder to move files from \n"
    value = click.prompt(msg, type=str)
    frm = get_folder(value)
    if not frm:
        click.echo("Please specify existing folder", err=True)
        return upload_handler(drive)

    msg = f"Local folder to move files into \n"
    to = click.prompt(msg, type=str)

    download_dir(drive, frm, to)


def gdrive_handler(drive):
    msg = '\n'.join([f'{k} - {v}' for k, v in HELPER_COMMANDS.items()])
    msg = f"Please choose a command \n" + msg
    value = click.prompt(msg, type=str)
    COMMAND_HANDLERS[value](drive)


BACKENDS = {'g': 'Google Drive'}
HELPER_COMMANDS = {'u': 'upload', 'd': 'download'}

SOURCE_HANDLERS = {
    'g': gdrive_handler
}
COMMAND_HANDLERS = {
    'u': upload_handler,
    'd': download_handler
}


@click.command()
@pass_provider
def helper(drive):
    """Run interactive helper"""
    msg = '\n'.join([f'{k} - {v}' for k, v in BACKENDS.items()])
    msg = f"Please choose a backend ({BACKENDS['g']} by default) \n" + msg
    value = click.prompt(msg, type=str, default=BACKENDS['g'])
    SOURCE_HANDLERS[value](drive)
